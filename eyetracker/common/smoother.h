#ifndef SMOOTHER_H
#define SMOOTHER_H

#include <unordered_map>

#include <boost/circular_buffer.hpp>
#include <opencv2/opencv.hpp>

// Skeletal Joint Smoothing White Paper
// https://msdn.microsoft.com/en-us/library/jj131429.aspx

enum NoiseReductionMethod { SIMPLE_MOVING_AVERAGE, DOUBLE_MOVING_AVERAGE, MEDIAN, SAVITZKY_GOLAY };

class EyeTrackerDataSmoother
{

public:
    explicit EyeTrackerDataSmoother();
    ~EyeTrackerDataSmoother();

    void newPoint(cv::Point2d &point, int timestamp);
    void pickMethod(const char* methodName);

private:
    int m_bufferSize = 5;
    NoiseReductionMethod m_smoothingMethod = SIMPLE_MOVING_AVERAGE;
    std::unordered_map<const char*, NoiseReductionMethod> m_methodsMap = {
        {"simple-ma", SIMPLE_MOVING_AVERAGE},
        {"double-ma", DOUBLE_MOVING_AVERAGE},
        {"median", MEDIAN},
        {"savitzky-golay", SAVITZKY_GOLAY}
    };

    boost::circular_buffer<double> m_meansXBuffer;
    boost::circular_buffer<double> m_meansYBuffer;
    boost::circular_buffer<double> m_inputDataXBuffer;
    boost::circular_buffer<double> m_inputDataYBuffer;

    void filterSimpleMovingAverage(cv::Point2d &point);
    void filterDoubleMovingAverage(cv::Point2d &point);
    void filterMedian(cv::Point2d &point);
    void filterSavitzkyGolay(cv::Point2d &point);
};

#endif
