#include<QDateTime>

#include <smoother.h>

MovementSmoother::MovementSmoother()
{
}

MovementSmoother::~MovementSmoother()
{
}


MovementSmootherWithBuffer::MovementSmootherWithBuffer()
    : m_previousPointTimestamp(0)
    , m_bufSize(8)
    , m_bufX(m_bufSize)
    , m_bufY(m_bufSize)
{
}

MovementSmootherWithBuffer::~MovementSmootherWithBuffer()
{
}

cv::Point2d MovementSmootherWithBuffer::filter(const cv::Point2d &point)
{
}

MovingAverageSmoother::MovingAverageSmoother()
{
}

MovingAverageSmoother::~MovingAverageSmoother()
{
}

cv::Point2d MovingAverageSmoother::filter(const cv::Point2d &point)
{
    int timestamp = QDateTime::currentMSecsSinceEpoch();

    m_bufX.push_back(point.x);
    m_bufY.push_back(point.y);

    return cv::Point2d(std::accumulate(m_bufX.begin(), m_bufX.end(), 0.0) / m_bufSize,
                       std::accumulate(m_bufY.begin(), m_bufY.end(), 0.0) / m_bufSize);
}


DoubleMovingAverageSmoother::DoubleMovingAverageSmoother()
    : m_bufAveragesX(m_bufSize)
    , m_bufAveragesY(m_bufSize)
{
}

DoubleMovingAverageSmoother::~DoubleMovingAverageSmoother()
{
}

cv::Point2d DoubleMovingAverageSmoother::filter(const cv::Point2d &point)
{
    int timestamp = QDateTime::currentMSecsSinceEpoch();

    m_bufX.push_back(point.x);
    m_bufY.push_back(point.y);

    m_bufAveragesX.push_back(std::accumulate(m_bufX.begin(), m_bufX.end(), 0.0) / m_bufSize);
    m_bufAveragesY.push_back(std::accumulate(m_bufY.begin(), m_bufY.end(), 0.0) / m_bufSize);

    double secondOrderAverageX = std::accumulate(m_bufAveragesX.begin(), m_bufAveragesX.end(), 0.0) / m_bufSize;
    double secondOrderAverageY = std::accumulate(m_bufAveragesY.begin(), m_bufAveragesY.end(), 0.0) / m_bufSize;

    return cv::Point2d(2 * m_bufAveragesX.back() - secondOrderAverageX,
                       2 * m_bufAveragesY.back() - secondOrderAverageY);
}


MedianSmoother::MedianSmoother()
{
}

MedianSmoother::~MedianSmoother()
{
}

cv::Point2d MedianSmoother::filter(const cv::Point2d &point)
{
    int timestamp = QDateTime::currentMSecsSinceEpoch();

    m_bufX.push_back(point.x);
    m_bufY.push_back(point.y);

    std::nth_element(m_bufX.begin(), m_bufX.begin() + m_bufSize/2, m_bufX.end());
    std::nth_element(m_bufY.begin(), m_bufY.begin() + m_bufSize/2, m_bufY.end());

    return cv::Point2d(m_bufX[m_bufSize/2], m_bufY[m_bufSize/2]);
}

DoubleExpSmoother::DoubleExpSmoother()
    : m_gamma(0.6)
    , m_alpha(0.5)
    , m_previousOutputX(0.0)
    , m_previousOutputY(0.0)
    , m_previousTrendX(0.0)
    , m_previousTrendY(0.0)
{
}

DoubleExpSmoother::~DoubleExpSmoother()
{
}

cv::Point2d DoubleExpSmoother::filter(const cv::Point2d &point)
{
    int timestamp = QDateTime::currentMSecsSinceEpoch();

    cv::Point2d smoothedPoint;

    smoothedPoint.x = m_alpha*point.x + (1 - m_alpha)*(m_previousOutputX + m_previousTrendX);
    smoothedPoint.y = m_alpha*point.y + (1 - m_alpha)*(m_previousOutputY + m_previousTrendY);

    m_previousTrendX = m_gamma*(smoothedPoint.x - m_previousOutputX) + \
            (1 - m_gamma)*m_previousTrendX;
    m_previousTrendY = m_gamma*(smoothedPoint.y - m_previousOutputY) + \
            (1 - m_gamma)*m_previousTrendY;
    m_previousOutputX = smoothedPoint.x;
    m_previousOutputY = smoothedPoint.y;

    return smoothedPoint;
}


CustomSmoother::CustomSmoother()
    : m_gamma(0.6)
    , m_alpha(0.5)
    , m_previousOutputX(0.0)
    , m_previousOutputY(0.0)
    , m_previousTrendX(0.0)
    , m_previousTrendY(0.0)
    , m_jitterThreshold(0.7)
{
}

CustomSmoother::~CustomSmoother()
{
}

cv::Point2d CustomSmoother::filter(const cv::Point2d &point)
{
    int timestamp = QDateTime::currentMSecsSinceEpoch();

    m_bufX.push_back(point.x);
    m_bufY.push_back(point.y);

    std::nth_element(m_bufX.begin(), m_bufX.begin() + m_bufSize/2, m_bufX.end());
    std::nth_element(m_bufY.begin(), m_bufY.begin() + m_bufSize/2, m_bufY.end());

    double medianX = m_bufX[m_bufSize/2];
    double medianY = m_bufY[m_bufSize/2];

    cv::Point2d smoothedPoint;

    smoothedPoint.x = (std::abs(point.x - medianX) > m_jitterThreshold) ? medianX :
            m_alpha*point.x + (1 - m_alpha)*(m_previousOutputX + m_previousTrendX);
    smoothedPoint.y = (std::abs(point.y - medianY) > m_jitterThreshold) ? medianY :
            m_alpha*point.y + (1 - m_alpha)*(m_previousOutputY + m_previousTrendY);

    m_previousTrendX = m_gamma*(smoothedPoint.x - m_previousOutputX) + \
            (1 - m_gamma)*m_previousTrendX;
    m_previousTrendY = m_gamma*(smoothedPoint.y - m_previousOutputY) + \
            (1 - m_gamma)*m_previousTrendY;
    m_previousOutputX = smoothedPoint.x;
    m_previousOutputY = smoothedPoint.y;

    return smoothedPoint;
 }


 KalmanSmoother::KalmanSmoother()
    : m_filter(4, 2, 0)
    , m_input(2, 0)
{
    setUp();
}

void KalmanSmoother::setUp()
{
    double statePreX = 0;
    double statePreY = 0;

    m_filter.transitionMatrix = *(cv::Mat_<float>(4, 4) <<
                                  1,0,1,0,  0,1,0,1,  0,0,1,0,  0,0,0,1);
    m_input.setTo(cv::Scalar(0));
    m_filter.statePre.at<float>(0) = statePreX;
    m_filter.statePre.at<float>(1) = statePreY;
    m_filter.statePre.at<float>(2) = 0;
    m_filter.statePre.at<float>(3) = 0;
    cv::setIdentity(m_filter.measurementMatrix);
    cv::setIdentity(m_filter.processNoiseCov, cv::Scalar::all(1e-4));
    cv::setIdentity(m_filter.measurementNoiseCov, cv::Scalar::all(1e-1));
    cv::setIdentity(m_filter.errorCovPost, cv::Scalar::all(.1));
}

KalmanSmoother::~KalmanSmoother()
{
}

cv::Point2d KalmanSmoother::filter(const cv::Point2d &point)
{
    cv::Mat prediction = m_filter.predict();

    m_input(0) = point.x;
    m_input(1) = point.y;

    cv::Mat estimation = m_filter.correct(m_input);

    return cv::Point2d(estimation.at<float>(0), estimation.at<float>(1));
}


SavitzkyGolaySmoother::SavitzkyGolaySmoother()
{
}

SavitzkyGolaySmoother::~SavitzkyGolaySmoother()
{
}

cv::Point2d SavitzkyGolaySmoother::filter(const cv::Point2d &point)
{
}
