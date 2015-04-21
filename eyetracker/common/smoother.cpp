
#include "smoother.h"

MovementSmoother::~MovementSmoother()
{
}

cv::Point2d NullSmoother::filter(const cv::Point2d & point)
{
    return point;
}

MovementSmootherWithBuffer::MovementSmootherWithBuffer()
    : m_bufSize(15)
    , m_previousPointTimestamp(0)
    , m_bufX(m_bufSize, 0.0)
    , m_bufY(m_bufSize, 0.0)
{
}

cv::Point2d MovingAverageSmoother::filter(const cv::Point2d & point)
{
    double x = point.x >= 0 ? point.x : m_bufX.back();
    double y = point.y >= 0 ? point.y : m_bufY.back();

    m_bufX.push_back(x);
    m_bufY.push_back(y);

    return cv::Point2d(std::accumulate(m_bufX.begin(), m_bufX.end(), 0.0) / m_bufX.size(),
                       std::accumulate(m_bufY.begin(), m_bufY.end(), 0.0) / m_bufY.size());
}


DoubleMovingAverageSmoother::DoubleMovingAverageSmoother()
    : m_bufAveragesX(m_bufSize, 0.0)
    , m_bufAveragesY(m_bufSize, 0.0)
{
}

cv::Point2d DoubleMovingAverageSmoother::filter(const cv::Point2d & point)
{
    double x = point.x >= 0 ? point.x : m_bufX.back();
    double y = point.y >= 0 ? point.y : m_bufY.back();

    m_bufX.push_back(x);
    m_bufY.push_back(y);

    m_bufAveragesX.push_back(std::accumulate(m_bufX.begin(), m_bufX.end(), 0.0) / m_bufX.size());
    m_bufAveragesY.push_back(std::accumulate(m_bufY.begin(), m_bufY.end(), 0.0) / m_bufY.size());

    const double secondOrderAverageX =
        std::accumulate(m_bufAveragesX.begin(), m_bufAveragesX.end(), 0.0) / m_bufAveragesX.size();
    const double secondOrderAverageY =
        std::accumulate(m_bufAveragesY.begin(), m_bufAveragesY.end(), 0.0) / m_bufAveragesY.size();

    return cv::Point2d(2 * m_bufAveragesX.back() - secondOrderAverageX,
                       2 * m_bufAveragesY.back() - secondOrderAverageY);
}

cv::Point2d MedianSmoother::filter(const cv::Point2d & point)
{
    double x = point.x >= 0 ? point.x : m_bufX.back();
    double y = point.y >= 0 ? point.y : m_bufY.back();

    m_bufX.push_back(x);
    m_bufY.push_back(y);

    std::nth_element(m_bufX.begin(), m_bufX.begin() + m_bufX.size()/2, m_bufX.end());
    std::nth_element(m_bufY.begin(), m_bufY.begin() + m_bufY.size()/2, m_bufY.end());

    return cv::Point2d(m_bufX[m_bufX.size()/2], m_bufY[m_bufY.size()/2]);
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

cv::Point2d DoubleExpSmoother::filter(const cv::Point2d & point)
{
    double x = point.x >= 0 ? point.x : m_previousOutputX;
    double y = point.y >= 0 ? point.y : m_previousOutputY;

    const cv::Point2d smoothedPoint(
        m_alpha*x + (1 - m_alpha)*(m_previousOutputX + m_previousTrendX),
        m_alpha*y + (1 - m_alpha)*(m_previousOutputY + m_previousTrendY)
    );

    m_previousTrendX =
        m_gamma * (smoothedPoint.x - m_previousOutputX) + (1.0 - m_gamma) * m_previousTrendX;
    m_previousTrendY =
        m_gamma * (smoothedPoint.y - m_previousOutputY) + (1.0 - m_gamma) * m_previousTrendY;
    m_previousOutputX = smoothedPoint.x;
    m_previousOutputY = smoothedPoint.y;

    return smoothedPoint;
}

CustomSmoother::CustomSmoother()
    : m_gamma(0.6)
    , m_alpha(0.4)
    , m_previousOutputX(0.0)
    , m_previousOutputY(0.0)
    , m_previousTrendX(0.0)
    , m_previousTrendY(0.0)
    , m_jitterThreshold(0.5)
{
}

cv::Point2d CustomSmoother::filter(const cv::Point2d & point)
{
    double x = point.x >= 0 ? point.x : m_bufX.back();
    double y = point.y >= 0 ? point.y : m_bufY.back();

    m_bufX.push_back(x);
    m_bufY.push_back(y);

    std::nth_element(m_bufX.begin(), m_bufX.begin() + m_bufX.size()/2, m_bufX.end());
    std::nth_element(m_bufY.begin(), m_bufY.begin() + m_bufY.size()/2, m_bufY.end());

    double medianX = m_bufX[m_bufX.size()/2];
    double medianY = m_bufY[m_bufY.size()/2];

    cv::Point2d smoothedPoint;

    smoothedPoint.x = (std::abs(x - medianX) > m_jitterThreshold) ? medianX :
            m_alpha*x + (1 - m_alpha)*(m_previousOutputX + m_previousTrendX);
    smoothedPoint.y = (std::abs(y - medianY) > m_jitterThreshold) ? medianY :
            m_alpha*y + (1 - m_alpha)*(m_previousOutputY + m_previousTrendY);

    m_previousTrendX =
        m_gamma * (smoothedPoint.x - m_previousOutputX) + (1.0 - m_gamma) * m_previousTrendX;
    m_previousTrendY =
        m_gamma * (smoothedPoint.y - m_previousOutputY) + (1.0 - m_gamma) * m_previousTrendY;
    m_previousOutputX = smoothedPoint.x;
    m_previousOutputY = smoothedPoint.y;
    return smoothedPoint;
}

 KalmanSmoother::KalmanSmoother()
    : m_filter(4, 2, 0)
    , m_input(2, 1)
    , m_previousOutputX(0.0)
    , m_previousOutputY(0.0)
{
    double statePreX = 0.0;
    double statePreY = 0.0;

    m_filter.transitionMatrix = *(cv::Mat_<float>(4, 4) <<
                                  1,0,1,0,  0,1,0,1,  0,0,1,0,  0,0,0,1);
    m_input.setTo(cv::Scalar(0));
    m_filter.statePre.at<float>(0) = statePreX;
    m_filter.statePre.at<float>(1) = statePreY;
    m_filter.statePre.at<float>(2) = 0;
    m_filter.statePre.at<float>(3) = 0;
    cv::setIdentity(m_filter.measurementMatrix);

    // supposed and demanded level of eye movement natural noise,
    // movements in both dimensions are supposed to be independent
    cv::setIdentity(m_filter.processNoiseCov, cv::Scalar::all(5e-5));

    // supposed level of tracker measurement noise,
    // measurements of both dimensions are supposed to be independent
    cv::setIdentity(m_filter.measurementNoiseCov, cv::Scalar::all(1e-1));

    // post prediction state allowed error level,
    // dimensions should be independent
    cv::setIdentity(m_filter.errorCovPost, cv::Scalar::all(0.1));
}

cv::Point2d KalmanSmoother::filter(const cv::Point2d & point)
{
    double x = point.x >= 0 ? point.x : m_previousOutputX;
    double y = point.y >= 0 ? point.y : m_previousOutputY;

    cv::Mat prediction = m_filter.predict();

    m_input(0) = x;
    m_input(1) = y;

    cv::Mat estimation = m_filter.correct(m_input);

    m_previousOutputX = estimation.at<float>(0);
    m_previousOutputY = estimation.at<float>(1);

    return cv::Point2d(m_previousOutputX, m_previousOutputY);
}
