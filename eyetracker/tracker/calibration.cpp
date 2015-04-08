
#include "calibration.h"
#include <QDebug>

// http://gazeparser.sourceforge.net/adv/principle.html
cv::Point2d EyeTrackerCalibration::getGazePosition(const cv::Point2d & pupilPos)
{
    // return m_transform * pupilPos + m_translation;
    return cv::Point2d(m_paramX[0] * pupilPos.x + m_paramX[1] * pupilPos.y + m_paramX[2],
                       m_paramY[0] * pupilPos.x + m_paramY[1] * pupilPos.y + m_paramY[2]);
}

bool EyeTrackerCalibration::calibrate(const CalibrationData & calibrationData)
{
    if(calibrationData.size() == 0)
        return false;

    size_t totalCalibrationPointsNum = 0;

    for(const auto & p: calibrationData)
        totalCalibrationPointsNum += p.eyePositions.size();

    if(totalCalibrationPointsNum < 10)
        return false;

    std::vector<cv::Point2d> eyePositions;
    std::vector<cv::Point2d> screenPositions;

    if(0)
    {
        eyePositions.resize(totalCalibrationPointsNum);
        screenPositions.resize(totalCalibrationPointsNum);

        size_t i = 0;
        for(const auto & p: calibrationData)
        {
            const auto screenPos = p.screenPoint;
            for(const auto & eyePos: p.eyePositions)
            {
                eyePositions[i] = eyePos;
                screenPositions[i] = screenPos;
                ++i;
            }
        }
    }
    else
    {
        eyePositions.resize(calibrationData.size());
        screenPositions.resize(calibrationData.size());

        size_t i = 0;
        for(const auto & p: calibrationData)
        {
            const auto screenPos = p.screenPoint;
            double mean_x = 0.0;
            double mean_y = 0.0;
            for(const auto & eyePos: p.eyePositions)
            {
                mean_x += eyePos.x;
                mean_y += eyePos.y;
            }
            mean_x /= p.eyePositions.size();
            mean_y /= p.eyePositions.size();

            eyePositions[i] = cv::Point2d(mean_x, mean_y);
            screenPositions[i] = screenPos;
            i++;
        }
    }

    return estimateParameters(eyePositions, screenPositions);
}

bool EyeTrackerCalibration::estimateParameters(
    const std::vector<cv::Point2d> & eyeData,
    const std::vector<cv::Point2d> & calPointData)
{
    Q_ASSERT(eyeData.size() == calPointData.size());

    const size_t dataCounter = eyeData.size();

    qDebug() << "Calibration data:";
    for(size_t i = 0; i < dataCounter; i++)
    {
        qDebug() << "calib point:"
                 << calPointData[i].x << " " << calPointData[i].y
                 << "- pupil pos:"
                 << eyeData[i].x << " " <<  eyeData[i].y;
    }

    if(dataCounter <= 0)
    {
        // TODO: zero calibration coeffs
        return false;
    }

    cv::Mat IJ(dataCounter, 3, CV_64FC1); // positions of eye in video frame
    cv::Mat X(dataCounter, 1, CV_64FC1); // positions of point on screen
    cv::Mat Y(dataCounter, 1, CV_64FC1);

    for(int i = 0; i < IJ.rows; i++)
    {
        double * Mi = IJ.ptr<double>(i);
        Mi[0] = eyeData[i].x;
        Mi[1] = eyeData[i].y;
        Mi[2] = 1.0;
    }

    cv::MatIterator_<double> it;

    int i;
    for(i = 0, it = X.begin<double>(); it != X.end<double>(); it++)
    {
        *it = calPointData[i].x;
        i++;
    }

    for(i = 0, it = Y.begin<double>(); it != Y.end<double>(); it++)
    {
        *it = calPointData[i].y;
        i++;
    }

    const cv::Mat PX = (IJ.t() * IJ).inv() * IJ.t() * X;
    const cv::Mat PY = (IJ.t() * IJ).inv() * IJ.t() * Y;

    //g_GX = IJ*PX;  //If calibration results are necessary ...
    //g_GY = IJ*PY;

    //m_transform = cv::Matx22d();
    //m_translation = cv::Vec2d(*PX.ptr<double>(2), *PY.ptr<double>(2));

    for(int i = 0; i < 3; i++)
    {
        const double* MiX = PX.ptr<double>(i);
        const double* MiY = PY.ptr<double>(i);
        m_paramX[i] = *MiX;
        m_paramY[i] = *MiY;
    }

    qDebug() << "Calibration coeffs:";
    qDebug() << m_paramX[0] << " " <<  m_paramX[1] << " " << m_paramX[2];
    qDebug() << m_paramY[0] << " " <<  m_paramY[2] << " " << m_paramY[2];

    return true;
}

void EyeTrackerCalibration::save(QSettings & settings) const
{
    settings.setValue("param_x_0", m_paramX[0]);
    settings.setValue("param_x_1", m_paramX[1]);
    settings.setValue("param_x_2", m_paramX[2]);
    settings.setValue("param_y_0", m_paramY[0]);
    settings.setValue("param_y_1", m_paramY[1]);
    settings.setValue("param_y_2", m_paramY[2]);
}

void EyeTrackerCalibration::load(QSettings & settings)
{
    m_paramX[0] = settings.value("param_x_0", 0.0).toDouble();
    m_paramX[1] = settings.value("param_x_1", 0.0).toDouble();
    m_paramX[2] = settings.value("param_x_2", 0.0).toDouble();
    m_paramY[0] = settings.value("param_y_0", 0.0).toDouble();
    m_paramY[1] = settings.value("param_y_1", 0.0).toDouble();
    m_paramY[2] = settings.value("param_y_2", 0.0).toDouble();
}
