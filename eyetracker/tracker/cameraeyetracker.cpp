#include "cameraeyetracker.h"
#include "smoother.h"

#include <QFile>
#include <boost/math/special_functions/fpclassify.hpp>

CameraEyetracker::CameraEyetracker(QObject * parent)
    : Eyetracker(parent)
    , m_cameraIndex(0)
    , m_captureThread(nullptr)
    , m_detectorThread(nullptr)
    , m_tracking(false)
    , m_calibrating(false)
    , m_calibrating_point(false)
    , m_measurementsPerPoint(20)
    , m_distStdDevCoeff(1.6)
    , m_pointCalibrationTimeout(5000)
{
    m_captureThread = new QThread;
    m_detectorThread = new QThread;
    m_captureThread->start();
    m_detectorThread->start();

    m_capture.moveToThread(m_captureThread);

    m_pupilDetector.moveToThread(m_detectorThread);
    m_pupilDetector.connect(&m_capture, SIGNAL(matReady(cv::Mat)), SLOT(newFrame(cv::Mat)));

    connect(&m_pupilDetector,
        SIGNAL(pupilData(bool, double, double, double)),
        this,
        SLOT(pupilData(bool, double, double, double))
    );

    m_pointCalibrationTimer.setSingleShot(true);
    connect(&m_pointCalibrationTimer, SIGNAL(timeout()), this, SLOT(pointCalibrationTimeout()));
}

CameraEyetracker::~CameraEyetracker()
{
    m_detectorThread->quit();
    m_captureThread->quit();

    m_detectorThread->wait();
    m_captureThread->wait();

    m_detectorThread->deleteLater();
    m_captureThread->deleteLater();
}

const char * CameraEyetracker::getBackendCodename() const
{
    return "camera";
}

QString CameraEyetracker::getBackend() const
{
    return QStringLiteral("Camera eyetracker ver. 1.0");
}

void CameraEyetracker::runCameraSetup()
{
    if(m_cameraSetupWindow.isNull())
    {
        m_cameraSetupWindow = new PupilDetectorSetupWindow;
        connect(m_cameraSetupWindow, SIGNAL(finished(int)), this, SLOT(cameraSetupDialogFinished(int)));
        connect(m_cameraSetupWindow, SIGNAL(cameraIndexChanged(int)), this, SLOT(setCameraIndex(int)));
    }

    m_cameraSetupWindow->setVideoSource(&m_pupilDetector, m_cameraIndex);
    m_cameraSetupWindow->show();
}

void CameraEyetracker::cameraSetupDialogFinished(int result)
{
    if(result == QDialog::Accepted)
    {
        saveConfig();
        emit cameraSetupFinished(true, QString());
    }
    else
        emit cameraSetupFinished(false, tr("camera setup cancelled"));
}

void CameraEyetracker::setCameraIndex(int cameraIndex)
{
    m_cameraIndex = cameraIndex;
    QMetaObject::invokeMethod(&m_capture, "start", Q_ARG(int, cameraIndex));
}

void CameraEyetracker::initialize()
{
    // Everything runs at the same priority as the gui, so it won't supply useless frames.
    m_pupilDetector.setProcessAll(false);

    QMetaObject::invokeMethod(&m_capture, "start", Q_ARG(int, m_cameraIndex));

    emit initialized(true, QString());
}

void CameraEyetracker::shutdown()
{
}

bool CameraEyetracker::loadConfig()
{
    QSettings settings(getBaseConfigPath() + ".ini", QSettings::IniFormat);
    m_pupilDetector.loadSettings(settings);
    m_calibration.load(settings);
    m_cameraIndex = settings.value("camera_index", m_cameraIndex).toInt();
    return settings.status() == QSettings::NoError;
}

bool CameraEyetracker::saveConfig() const
{
    QSettings settings(getBaseConfigPath() + ".ini", QSettings::IniFormat);
    m_pupilDetector.saveSettings(settings);
    m_calibration.save(settings);
    settings.setValue("camera_index", m_cameraIndex);
    settings.sync();
    return settings.status() == QSettings::NoError;
}

void CameraEyetracker::calibrationStart()
{
    m_calibrationData.clear();
    m_calibrating = true;
    m_calibrating_point = false;
    m_calibration.setToZero();

    emit calibrationStarted(true, QString());

    // REMOVE ME: only for debug
    //runCameraSetup();
}

void CameraEyetracker::calibrationStop()
{
    m_calibrationData.clear();
    m_calibrating = false;
    m_calibrating_point = false;
    emit calibrationStopped(true, QString());
}

void CameraEyetracker::calibrationAddPoint(QPointF point)
{
    if(!m_calibrating)
    {
        emit pointCalibrated(false, tr("calibration not started"));
        return;
    }

    CalibrationPoint pt;
    pt.screenPoint.x = point.x();
    pt.screenPoint.y = point.y();
    m_calibrationData.push_back(pt);
    m_calibrating_point = true;

    m_pointCalibrationTimer.start(m_pointCalibrationTimeout);
}

void CameraEyetracker::pointCalibrationTimeout()
{
    m_calibrating_point = false;
    emit pointCalibrated(false, tr("point calibration timeout"));
}

void CameraEyetracker::calibrationComputeAndSet()
{
    const bool success = m_calibration.calibrate(m_calibrationData);
    if(success)
        emit computeAndSetCalibrationFinished(true, QString());
    else
        emit computeAndSetCalibrationFinished(false, tr("calibration failed"));
}

bool CameraEyetracker::startTracking()
{
    m_tracking = true;
    return true;
}

bool CameraEyetracker::stopTracking()
{
    m_tracking = false;
    return true;
}

bool CameraEyetracker::addDataPoint(std::vector<cv::Point2d> & v, const cv::Point2d & pt)
{
    v.push_back(pt);

    if(v.size() < m_measurementsPerPoint)
        return false;

    double meanX = 0.0;
    std::for_each(std::begin(v), std::end(v), [&](const cv::Point2d & p) { meanX += p.x; });
    meanX /= v.size();

    double meanY = 0.0;
    std::for_each(std::begin(v), std::end(v), [&](const cv::Point2d & p) { meanY += p.y; });
    meanY /= v.size();

    // distances from mean point
    std::vector<double> distances(v.size());
    for(size_t i = 0; i < distances.size(); i++)
    {
        const double dx = v[i].x - meanX;
        const double dy = v[i].y - meanY;
        distances[i] = std::sqrt(dx * dx + dy * dy);
    }

    // mean distance
    double meanDist = 0.0;
    std::for_each(std::begin(distances), std::end(distances), [&](const double val) {
        meanDist += val;
    });
    meanDist /= distances.size();

    double stdDevDist = 0.0;
    std::for_each(std::begin(distances), std::end(distances), [&](const double val) {
        const double c = val - meanDist;
        stdDevDist += c * c;
    });
    stdDevDist = std::sqrt(stdDevDist / (v.size() - 1));

    // outliers cutoff
    const double maxDist = meanDist + stdDevDist * m_distStdDevCoeff;

    //qDebug() << "meanDist:" << meanDist << "+/-" << stdDevDist;
    //qDebug() << "maxDist:" << maxDist;

    //qDebug() << "dist:";
    //for(auto d : distances)
    //    qDebug() << d;

    std::vector<size_t> removeIndexes;
    removeIndexes.reserve(distances.size());
    for(size_t i = 0; i < distances.size(); i++)
        if(distances[i] >= maxDist)
            removeIndexes.push_back(i);

    //qDebug() << "removing:";
    //for(auto i : removeIndexes)
    //    qDebug() << distances[i];

    for(int i = removeIndexes.size() - 1; i >= 0; i--)
        v.erase(v.begin() + removeIndexes[i]);

    return true;
    //if(v.size() >= m_measurementsPerPoint)
    //    return true;
    //else
    //    return false;
}

void CameraEyetracker::pupilData(bool ok, double posX, double posY, double size)
{
    Q_UNUSED(size);

    if(!ok)
        emit gazeDetectionFailed(tr("Tracker failed in detecting any pupil."));
        return;

    cv::Point2d pos(posX, posY);

    if(m_tracking)
    {
        emitNewPoint(m_calibration.getGazePosition(pos));

    }

    if(m_calibrating && m_calibrating_point)
    {
        //qDebug() << "cm: " << pos.x << pos.y;

        // append new eye positions to the last calibration point
        std::vector<cv::Point2d> & eyePositions =
            m_calibrationData[m_calibrationData.size() - 1].eyePositions;

        const bool gotEnoughPoints = addDataPoint(eyePositions, pos);

        if(gotEnoughPoints)
        {
            //for(size_t i = 0; i < eyePositions.size(); i++)
            //    qDebug() << eyePositions[i].x << eyePositions[i].y;
            m_calibrating_point = false;
            m_pointCalibrationTimer.stop();
            emit pointCalibrated(true, QString());
        }
    }
}
