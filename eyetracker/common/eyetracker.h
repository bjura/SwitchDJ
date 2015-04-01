#ifndef EYETRACKER_H
#define EYETRACKER_H

#include <QObject>
#include <QPointF>
#include <QVariant>

class Eyetracker : public QObject
{
    Q_OBJECT

public:
    explicit Eyetracker(QObject * parent = 0);
    ~Eyetracker();

    Q_INVOKABLE void setParameter(QString name, QVariant value);
    Q_INVOKABLE QVariant getParameter(QString name) const;

    Q_INVOKABLE bool saveParameters() const;
    Q_INVOKABLE bool loadParameters();

    Q_INVOKABLE virtual QString getBackend() const = 0;

    Q_INVOKABLE virtual void runCameraSetup() = 0;

    Q_INVOKABLE virtual bool startTracking() = 0;
    Q_INVOKABLE virtual bool stopTracking() = 0;

    Q_INVOKABLE virtual bool loadCalibration() = 0;
    Q_INVOKABLE virtual bool saveCalibration() = 0;

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

    void gazeData(QPointF right, QPointF left);

    void calibrationStarted(bool success, QString errorMessage);
    void calibrationStopped(bool success, QString errorMessage);
    void pointCalibrated(bool success, QString errorMessage);
    void computeAndSetCalibrationFinished(bool success, QString errorMessage);

protected:
    virtual QString getBaseConfigPath() const;
    virtual QString getConfigFilePath() const;
    virtual QString getCalibrationFilePath() const;
    virtual const char * getBackendCodename() const = 0; // only lowercase ASCII, no spaces

    QHash<QString, QVariant> m_params;
};

#endif // EYETRACKER_H
