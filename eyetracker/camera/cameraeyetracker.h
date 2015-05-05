/*
 * This file is part of PISAK project.
 *
 * This program is free software: you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation, either version 3 of the License, or
 * (at your option) any later version.
 *
 * This program is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 *
 * You should have received a copy of the GNU General Public License
 * along with this program. If not, see <http://www.gnu.org/licenses/>.
 */

#ifndef CAMERAEYETRACKER_H
#define CAMERAEYETRACKER_H

#include <QObject>
#include <QDebug>
#include <QMessageBox>
#include <QTimer>
#include <QThread>
#include <QApplication>

#include "../common/eyetracker.h"
#include "pupildetector.h"
#include "calibration.h"

class CameraEyetracker : public Eyetracker
{
    Q_OBJECT

public:
    explicit CameraEyetracker(QObject * parent = 0);
    ~CameraEyetracker();

    Q_INVOKABLE QString getBackend() const override;

    Q_INVOKABLE bool loadConfig() override;
    Q_INVOKABLE bool saveConfig() const override;

    Q_INVOKABLE void runCameraSetup() override;

    Q_INVOKABLE bool startTracking() override;
    Q_INVOKABLE bool stopTracking() override;

public slots:
    void initialize() override;
    void shutdown() override;

    void calibrationStart() override;
    void calibrationStop() override;
    void calibrationAddPoint(QPointF point) override;
    void calibrationComputeAndSet() override;

protected:
    const char * getBackendCodename() const override;

private:
    bool addDataPoint(std::vector<cv::Point2d> & v, const cv::Point2d & pt);

    int m_cameraIndex;
    Capture m_capture;
    FramePupilDetector m_pupilDetector;

    QPointer<QThread> m_captureThread;
    QPointer<QThread> m_detectorThread;

    QPointer<PupilDetectorSetupWindow> m_cameraSetupWindow;

    bool m_tracking;
    bool m_calibrating;
    bool m_calibrating_point;

    CalibrationData m_calibrationData;
    EyeTrackerCalibration m_calibration;
    QTimer m_pointCalibrationTimer;

    // calibration parameters
    size_t m_measurementsPerPoint;
    double m_distStdDevCoeff;
    int m_pointCalibrationTimeout;

private slots:
    void pupilData(bool, double, double, double);
    void setCameraIndex(int cameraIndex);
    void cameraSetupDialogFinished(int result);
    void pointCalibrationTimeout();
};

#endif // CALIBRATION_H
