#ifndef EYETRACKER_H
#define EYETRACKER_H

#include <QObject>
#include <QPointF>
#include <QVariant>
#include <QDebug>

#include "smoother.h"

class Eyetracker : public QObject
{
    Q_OBJECT

public:
    explicit Eyetracker(QObject * parent = 0);
    ~Eyetracker();

    Q_INVOKABLE virtual bool loadConfig() = 0;
    Q_INVOKABLE virtual bool saveConfig() const = 0;

    Q_INVOKABLE virtual QString getBackend() const = 0;

    Q_INVOKABLE virtual void runCameraSetup() = 0;

    Q_INVOKABLE virtual bool startTracking() = 0;
    Q_INVOKABLE virtual bool stopTracking() = 0;

public slots:
    virtual void initialize() = 0;
    virtual void shutdown() = 0;

    virtual void calibrationStart() = 0;
    virtual void calibrationStop() = 0;
    virtual void calibrationAddPoint(QPointF point) = 0;
    virtual void calibrationComputeAndSet() = 0;

signals:
    void initialized(bool success, QString errorMessage);
    void shutdownCompleted(bool success, QString errorMessage);
    void cameraSetupFinished(bool success, QString errorMessage);

    void gazeData(QPointF point);

    void calibrationStarted(bool success, QString errorMessage);
    void calibrationStopped(bool success, QString errorMessage);
    void pointCalibrated(bool success, QString errorMessage);
    void computeAndSetCalibrationFinished(bool success, QString errorMessage);

    void gazeDetectionFailed(QString errorMessage);

protected:
    virtual const char * getBackendCodename() const = 0; // only lowercase ASCII, no spaces
    QString getBaseConfigPath() const;

    virtual void emitNewPoint(cv::Point2d point);
    QPointF m_previousPoint;

    std::unique_ptr<MovementSmoother> m_smoother;

private:
    SmoothingMethod m_smoothingMethod;
    void createSmoother();
};

#endif // EYETRACKER_H
