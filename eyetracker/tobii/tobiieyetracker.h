#ifndef TOBIIEYETRACKER_H
#define TOBIIEYETRACKER_H

#include <QObject>
#include <QDebug>
#include <QMessageBox>
#include <QTimer>
#include <QThread>
#include <QApplication>
#include <QQmlApplicationEngine>
#include <QQmlListProperty>

#include "../common/eyetracker.h"

#include "tobiigaze.h"
#include "tobiigaze_calibration.h"
#include "tobiigaze_discovery.h"
#include "tobiigaze_error_codes.h"

class EyetrackerEventLoopWorker;

class TobiiEyetracker : public Eyetracker
{
    Q_OBJECT

public:
    explicit TobiiEyetracker(QObject * parent = 0);
    ~TobiiEyetracker();

    Q_INVOKABLE QString getBackend() const override;

    Q_INVOKABLE void runCameraSetup() override;

    Q_INVOKABLE bool startTracking() override;
    Q_INVOKABLE bool stopTracking() override;

    Q_INVOKABLE bool loadCalibration() override;
    Q_INVOKABLE bool saveCalibration() override;

public slots:
    void initialize() override;
    void shutdown() override;

    void calibrationStart() override;
    void calibrationStop() override;
    void calibrationAddPoint(QPointF point) override;
    void calibrationComputeAndSet() override;

protected:
    const char * getBackendCodename() const override;
    QString getConnectedEyeTracker() const;

private slots:

    // slots for tobiigaze async API callbacks
    void privCalibrationStarted(int error_code);
    void privCalibrationStopped(int error_code);
    void privPointCalibrated(int error_code);
    void privComputeAndSetCalibrationFinished(int error_code);
    void privGazeData(QPointF right, QPointF left);

    // thread related slots
    void privEventLoopFinished(int error_code);

private:
    void cleanup();

    tobiigaze_eye_tracker * m_eye_tracker = nullptr;
    EyetrackerEventLoopWorker * m_worker = nullptr;
};

// internal class used by TobiiEyetracker
// this class translates async callbacks to Qt signals
class EyetrackerEventLoopWorker : public QObject
{
    Q_OBJECT

public:
    EyetrackerEventLoopWorker(tobiigaze_eye_tracker * eye_tracker, QObject * parent = 0)
        : QObject(parent)
        , m_eye_tracker(eye_tracker)
    {
    }

    ~EyetrackerEventLoopWorker()
    {
    }

    friend class TobiiEyetracker;

signals:
    void calibrationStarted(int error_code);
    void calibrationStopped(int error_code);
    void pointCalibrated(int error_code);
    void computeAndSetCalibrationFinished(int error_code);

    void gazeData(QPointF, QPointF);

    void finished(int error_code);

private:

    // all callback handlers are called in event thread

    static void TOBIIGAZE_CALL calibration_start_helper(tobiigaze_error_code error_code, void * user_data)
    {
        if(user_data)
            reinterpret_cast<EyetrackerEventLoopWorker *>(user_data)->emit_calibration_start_callback(error_code);
    }

    static void TOBIIGAZE_CALL calibration_stop_helper(tobiigaze_error_code error_code, void * user_data)
    {
        if(user_data)
            reinterpret_cast<EyetrackerEventLoopWorker *>(user_data)->emit_calibration_stop_callback(error_code);
    }

    static void TOBIIGAZE_CALL calibration_add_point_helper(tobiigaze_error_code error_code, void * user_data)
    {
        if(user_data)
            reinterpret_cast<EyetrackerEventLoopWorker *>(user_data)->emit_calibration_add_point_callback(error_code);
    }

    static void TOBIIGAZE_CALL calibration_compute_and_set_helper(tobiigaze_error_code error_code, void * user_data)
    {
        if(user_data)
           reinterpret_cast<EyetrackerEventLoopWorker *>(user_data)->emit_calibration_compute_and_set_callback(error_code);
    }

    static void TOBIIGAZE_CALL gaze_data_helper(const tobiigaze_gaze_data * gazedata,
                                                const tobiigaze_gaze_data_extensions * extensions,
                                                void * user_data)
    {
        if(user_data)
           reinterpret_cast<EyetrackerEventLoopWorker *>(user_data)->emit_gaze_data(gazedata, extensions);
    }

    void emit_calibration_start_callback(tobiigaze_error_code error_code)
    {
        emit calibrationStarted(error_code);
    }

    void emit_calibration_stop_callback(tobiigaze_error_code error_code)
    {
        emit calibrationStopped(error_code);
    }

    void emit_calibration_add_point_callback(tobiigaze_error_code error_code)
    {
        emit pointCalibrated(error_code);
    }

    void emit_calibration_compute_and_set_callback(tobiigaze_error_code error_code)
    {
        emit computeAndSetCalibrationFinished(error_code);
    }

    void emit_gaze_data(const tobiigaze_gaze_data * gazedata,
                        const tobiigaze_gaze_data_extensions * extensions)
    {
        Q_UNUSED(extensions);

        QPointF right(-1, -1);
        QPointF left(-1, -1);

        if(gazedata)
        {
            const tobiigaze_tracking_status tracking_status = gazedata->tracking_status;

            if(tracking_status == TOBIIGAZE_TRACKING_STATUS_BOTH_EYES_TRACKED ||
               tracking_status == TOBIIGAZE_TRACKING_STATUS_ONLY_RIGHT_EYE_TRACKED ||
               tracking_status == TOBIIGAZE_TRACKING_STATUS_ONE_EYE_TRACKED_PROBABLY_RIGHT)
            {
                right.setX(gazedata->right.gaze_point_on_display_normalized.x);
                right.setY(gazedata->right.gaze_point_on_display_normalized.y);
            }

            if(tracking_status == TOBIIGAZE_TRACKING_STATUS_BOTH_EYES_TRACKED ||
               tracking_status == TOBIIGAZE_TRACKING_STATUS_ONLY_LEFT_EYE_TRACKED ||
               tracking_status == TOBIIGAZE_TRACKING_STATUS_ONE_EYE_TRACKED_PROBABLY_LEFT)
            {
                left.setX(gazedata->left.gaze_point_on_display_normalized.x);
                left.setY(gazedata->left.gaze_point_on_display_normalized.y);
            }

            if(gazedata->tracking_status == TOBIIGAZE_TRACKING_STATUS_ONE_EYE_TRACKED_UNKNOWN_WHICH)
            {
                // treat as invalid data
                /*
                qDebug() << "ONE_EYE_TRACKED_UNKNOWN_WHICH: ("
                         << gazedata->right.gaze_point_on_display_normalized.x
                         << ", "
                         << gazedata->right.gaze_point_on_display_normalized.y
                         << "), ("
                         << gazedata->left.gaze_point_on_display_normalized.x
                         << ", "
                         << gazedata->left.gaze_point_on_display_normalized.y
                         << ")";
                */
            }
        }

        emit gazeData(right, left);
    }

public slots:
    void run()
    {
        if(m_eye_tracker)
        {
            tobiigaze_error_code error_code;
            tobiigaze_run_event_loop(m_eye_tracker, &error_code);
            emit finished(error_code);
        }
        else
        {
            emit finished(-1);
        }
    }

private:
    tobiigaze_eye_tracker * m_eye_tracker = nullptr;
};

#endif // TOBIIEYETRACKER_H
