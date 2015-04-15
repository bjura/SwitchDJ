#include "eyetracker.h"

#include <QDir>
#include <QSettings>

Eyetracker::Eyetracker(QObject * parent)
    : QObject(parent)
    , m_smoothingMethod(SmoothingMethod::Custom)
{
    createSmoother();
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

void Eyetracker::createSmoother()
{
    switch (m_smoothingMethod)
    {
        case SmoothingMethod::None:
            m_smoother.reset(new NullSmoother);
            break;
        case SmoothingMethod::MovingAverage:
            m_smoother.reset(new MovingAverageSmoother);
            break;
        case SmoothingMethod::DoubleMovingAverage:
            m_smoother.reset(new DoubleMovingAverageSmoother);
            break;
        case SmoothingMethod::Median:
            m_smoother.reset(new MedianSmoother);
            break;
        case SmoothingMethod::DoubleExp:
            m_smoother.reset(new DoubleExpSmoother);
            break;
        case SmoothingMethod::Custom:
            m_smoother.reset(new CustomSmoother);
            break;
        case SmoothingMethod::SavitzkyGolay:
            m_smoother.reset(new SavitzkyGolaySmoother);
            break;
        case SmoothingMethod::Kalman:
            m_smoother.reset(new KalmanSmoother);
            break;
        default:
            m_smoother.reset(new NullSmoother);
    }
}
