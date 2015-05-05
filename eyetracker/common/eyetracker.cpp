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

#include "eyetracker.h"

#include <QDir>
#include <QSettings>

Eyetracker::Eyetracker(QObject * parent)
    : QObject(parent)
    , m_smoothingMethod(SmoothingMethod::Kalman)
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
        case SmoothingMethod::Kalman:
            m_smoother.reset(new KalmanSmoother);
            break;
        default:
            m_smoother.reset(new NullSmoother);
    }
}

void Eyetracker::emitNewPoint(cv::Point2d point)
{
    if(std::isnan(point.x) || std::isnan(point.y) ||
       point.x < 0 || point.y < 0)
    {
        point.x = m_previousPoint.x();
        point.y = m_previousPoint.y();
    }

    const cv::Point2d smoothed = m_smoother->filter(point);
    QPointF ret(smoothed.x, smoothed.y);
    m_previousPoint = ret;

    qDebug() << "pos:" << ret;
    emit gazeData(ret);
}
