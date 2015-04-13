#include <smoother.h>

EyeTrackerDataSmoother::EyeTrackerDataSmoother()
    : m_inputDataXBuffer(m_bufferSize)
    , m_inputDataYBuffer(m_bufferSize)
{
}

EyeTrackerDataSmoother::~EyeTrackerDataSmoother()
{
}

void EyeTrackerDataSmoother::newPoint(cv::Point2d &point, int timestamp)
{
    m_inputDataXBuffer.push_back(point.x);
    m_inputDataYBuffer.push_back(point.y);
    filter(point);
}

void EyeTrackerDataSmoother::filter(cv::Point2d &point)
{
}

MovingAverageSmoother::MovingAverageSmoother()
{
}

MovingAverageSmoother::~MovingAverageSmoother()
{
}

void MovingAverageSmoother::filter(cv::Point2d &point)
{
    point.x = std::accumulate(m_inputDataXBuffer.begin(),
                              m_inputDataXBuffer.end(), 0.0) / m_bufferSize;
    point.y = std::accumulate(m_inputDataYBuffer.begin(),
                              m_inputDataYBuffer.end(), 0.0) / m_bufferSize;
}

DoubleMovingAverageSmoother::DoubleMovingAverageSmoother()
    : m_meansXBuffer(m_bufferSize)
    , m_meansYBuffer(m_bufferSize)
{
}

DoubleMovingAverageSmoother::~DoubleMovingAverageSmoother()
{
}

void DoubleMovingAverageSmoother::filter(cv::Point2d &point)
{
    m_meansXBuffer.push_back(std::accumulate(m_inputDataXBuffer.begin(),
                            m_inputDataXBuffer.end(), 0.0) / m_bufferSize);
    m_meansYBuffer.push_back(std::accumulate(m_inputDataYBuffer.begin(),
                            m_inputDataYBuffer.end(), 0.0) / m_bufferSize);

    double secondOrderMeanX = std::accumulate(m_meansXBuffer.begin(),
                            m_meansXBuffer.end(), 0.0) / m_bufferSize;
    double secondOrderMeanY = std::accumulate(m_meansYBuffer.begin(),
                            m_meansYBuffer.end(), 0.0) / m_bufferSize;

    point.x = 2 * m_meansXBuffer.back() - secondOrderMeanX;
    point.y = 2 * m_meansYBuffer.back() - secondOrderMeanY;
}

MedianSmoother::MedianSmoother()
{
}

MedianSmoother::~MedianSmoother()
{
}

void MedianSmoother::filter(cv::Point2d &point)
{
    std::nth_element(m_inputDataXBuffer.begin(),
        m_inputDataXBuffer.begin() + m_bufferSize/2, m_inputDataXBuffer.end());
    std::nth_element(m_inputDataYBuffer.begin(),
        m_inputDataYBuffer.begin() + m_bufferSize/2, m_inputDataYBuffer.end());

    point.x = m_inputDataXBuffer[m_bufferSize/2];
    point.y = m_inputDataYBuffer[m_bufferSize/2];
}

DoubleExpSmoother::DoubleExpSmoother()
{
}

DoubleExpSmoother::~DoubleExpSmoother()
{
}

void DoubleExpSmoother::filter(cv::Point2d &point)
{
    point.x = alpha*point.x + (1 - alpha)*(m_previousOutputX + m_previousTrendX);
    point.y = alpha*point.y + (1 - alpha)*(m_previousOutputY + m_previousTrendY);

    m_previousTrendX = gamma*(point.x - m_previousOutputX) + \
            (1 - gamma)*m_previousTrendX;
    m_previousTrendY = gamma*(point.y - m_previousOutputY) + \
            (1 - gamma)*m_previousTrendY;
    m_previousOutputX = point.x;
    m_previousOutputY = point.y;
}

CustomSmoother::CustomSmoother()
{
}

CustomSmoother::~CustomSmoother()
{
}

void CustomSmoother::filter(cv::Point2d &point)
{
    std::nth_element(m_inputDataXBuffer.begin(), \
        m_inputDataXBuffer.begin() + m_bufferSize/2, m_inputDataXBuffer.end());
    std::nth_element(m_inputDataYBuffer.begin(), \
        m_inputDataYBuffer.begin() + m_bufferSize/2, m_inputDataYBuffer.end());

    double medianX = m_inputDataXBuffer[m_bufferSize/2];
    double medianY = m_inputDataYBuffer[m_bufferSize/2];

    point.x = (std::abs(point.x - medianX) > m_jitterThreshold) ? medianX : \
            alpha*point.x + (1 - alpha)*(m_previousOutputX + m_previousTrendX);
    point.y = (std::abs(point.y - medianY) > m_jitterThreshold) ? medianY : \
            alpha*point.y + (1 - alpha)*(m_previousOutputY + m_previousTrendY);

    m_previousTrendX = gamma*(point.x - m_previousOutputX) + \
            (1 - gamma)*m_previousTrendX;
    m_previousTrendY = gamma*(point.y - m_previousOutputY) + \
            (1 - gamma)*m_previousTrendY;
    m_previousOutputX = point.x;
    m_previousOutputY = point.y;
}

 KalmanSmoother::KalmanSmoother()
    : m_filter(4, 2, 0)
    , m_input(2, 0)
{
    setUp();
}

void KalmanSmoother::setUp()
{
    m_filter.transitionMatrix = *(cv::Mat_<float>(4, 4) <<
                                  1,0,1,0,  0,1,0,1,  0,0,1,0,  0,0,0,1);
    m_input.setTo(cv::Scalar(0));
    m_filter.statePre.at<float>(0) = m_inputDataXBuffer.back();
    m_filter.statePre.at<float>(1) = m_inputDataYBuffer.back();
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

void KalmanSmoother::filter(cv::Point2d &point)
{
    cv::Mat prediction = m_filter.predict();

    m_input(0) = point.x;
    m_input(1) = point.y;

    cv::Mat estimation = m_filter.correct(m_input);
    point.x = estimation.at<float>(0);
    point.y = estimation.at<float>(1);
}

SavitzkyGolaySmoother::SavitzkyGolaySmoother()
{
}

SavitzkyGolaySmoother::~SavitzkyGolaySmoother()
{
}

void SavitzkyGolaySmoother::filter(cv::Point2d &point)
{
}
