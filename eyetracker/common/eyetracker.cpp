#include "eyetracker.h"

#include <QDir>
#include <QSettings>

Eyetracker::Eyetracker(QObject * parent)
    : QObject(parent)
    , m_smoothingMethod(Custom)
{
    pickSmoother();
}

Eyetracker::~Eyetracker()
{
}

QString Eyetracker::getBaseConfigPath() const
{
    const QDir dir(QDir::homePath() + "/.pisak/eyetracker");
    if(!dir.exists())
        dir.mkpath(".");
    return dir.filePath(getBackendCodename());
}

void Eyetracker::pickSmoother()
{
    switch (m_smoothingMethod)
    {
        case MovingAverage:
            m_smoother = new MovingAverageSmoother();
        case DoubleMovingAverage:
            m_smoother = new DoubleMovingAverageSmoother();
        case Median:
            m_smoother = new MedianSmoother();
        case DoubleExp:
            m_smoother = new DoubleExpSmoother();
        case Custom:
            m_smoother = new CustomSmoother();
        case SavitzkyGolay:
            m_smoother = new SavitzkyGolaySmoother();
        case Kalman:
            m_smoother = new KalmanSmoother();
    }
}
