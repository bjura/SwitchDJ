#include <smoother.h>


EyeTrackerDataSmoother::EyeTrackerDataSmoother()
    : m_inputDataXBuffer(m_bufferSize)
    , m_inputDataYBuffer(m_bufferSize)
    , m_meansXBuffer(m_bufferSize)
    , m_meansYBuffer(m_bufferSize)
{
}

EyeTrackerDataSmoother::~EyeTrackerDataSmoother()
{
}

void EyeTrackerDataSmoother::newPoint(cv::Point2d &point, int timestamp)
{
    m_inputDataXBuffer.push_back(point.x);
    m_inputDataYBuffer.push_back(point.y);
    switch (m_smoothingMethod)
    {
        case SIMPLE_MOVING_AVERAGE: filterSimpleMovingAverage(point);
        case DOUBLE_MOVING_AVERAGE: filterDoubleMovingAverage(point);
        case MEDIAN: filterMedian(point);
        case SAVITZKY_GOLAY: filterSavitzkyGolay(point);
    }
}

void EyeTrackerDataSmoother::pickMethod(const char* methodName)
{
    m_smoothingMethod = m_methodsMap[methodName];
}

void EyeTrackerDataSmoother::filterSimpleMovingAverage(cv::Point2d &point)
{
    point.x = std::accumulate(m_inputDataXBuffer.begin(), m_inputDataXBuffer.end(), 0) / m_bufferSize;
    point.y = std::accumulate(m_inputDataYBuffer.begin(), m_inputDataYBuffer.end(), 0) / m_bufferSize;
}

void EyeTrackerDataSmoother::filterDoubleMovingAverage(cv::Point2d &point)
{
    m_meansXBuffer.push_back(std::accumulate(m_inputDataXBuffer.begin(), m_inputDataXBuffer.end(), 0) / m_bufferSize);
    m_meansYBuffer.push_back(std::accumulate(m_inputDataYBuffer.begin(), m_inputDataYBuffer.end(), 0) / m_bufferSize);

    double secondOrderMeanX = std::accumulate(m_meansXBuffer.begin(), m_meansXBuffer.end(), 0) / m_bufferSize;
    double secondOrderMeanY = std::accumulate(m_meansYBuffer.begin(), m_meansYBuffer.end(), 0) / m_bufferSize;

    point.x = 2 * m_meansXBuffer.back() - secondOrderMeanX;
    point.y = 2 * m_meansYBuffer.back() - secondOrderMeanY;
}

void EyeTrackerDataSmoother::filterMedian(cv::Point2d &point)
{
    std::nth_element(m_inputDataXBuffer.begin(), m_inputDataXBuffer.begin() + m_bufferSize/2, m_inputDataXBuffer.end());
    std::nth_element(m_inputDataYBuffer.begin(), m_inputDataYBuffer.begin() + m_bufferSize/2, m_inputDataYBuffer.end());

    point.x = m_inputDataXBuffer[m_bufferSize/2];
    point.y = m_inputDataYBuffer[m_bufferSize/2];
}

void EyeTrackerDataSmoother::filterSavitzkyGolay(cv::Point2d &point)
{
}
