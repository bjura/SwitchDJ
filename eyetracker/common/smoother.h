#ifndef SMOOTHER_H
#define SMOOTHER_H

#include <unordered_map>

#include <boost/circular_buffer.hpp>
#include <opencv2/opencv.hpp>

// Skeletal Joint Smoothing White Paper
// https://msdn.microsoft.com/en-us/library/jj131429.aspx

enum NoiseReductionMethod { SIMPLE_MOVING_AVERAGE, DOUBLE_MOVING_AVERAGE, MEDIAN, \
                            SAVITZKY_GOLAY, KALMAN, DOUBLE_EXP };


class EyeTrackerDataSmoother
{

public:
    EyeTrackerDataSmoother();
    ~EyeTrackerDataSmoother();

    void newPoint(cv::Point2d &point, int timestamp);

protected:
    int m_bufferSize = 10;

    boost::circular_buffer<double> m_inputDataXBuffer;
    boost::circular_buffer<double> m_inputDataYBuffer;

    virtual void filter(cv::Point2d &point);
};

class MovingAverageSmoother : public EyeTrackerDataSmoother
{

public:
    MovingAverageSmoother();
    ~MovingAverageSmoother();

private:
    void filter(cv::Point2d &point);
};


class DoubleMovingAverageSmoother : public EyeTrackerDataSmoother
{

public:
    DoubleMovingAverageSmoother();
    ~DoubleMovingAverageSmoother();

private:
    boost::circular_buffer<double> m_meansXBuffer;
    boost::circular_buffer<double> m_meansYBuffer;

    void filter(cv::Point2d &point);
};


class MedianSmoother : public EyeTrackerDataSmoother
{

public:
    MedianSmoother();
    ~MedianSmoother();

private:
    void filter(cv::Point2d &point);
};


class DoubleExpSmoother : public EyeTrackerDataSmoother
{

public:
    DoubleExpSmoother();
    ~DoubleExpSmoother();

private:
    double gamma = 0.7;
    double alpha = 0.5;

    std::vector<double> m_outputsXBuffer;
    std::vector<double> m_outputsYBuffer;
    std::vector<double> m_trendsXBuffer;
    std::vector<double> m_trendsYBuffer;

    void filter(cv::Point2d &point);
};


class KalmanSmoother : public EyeTrackerDataSmoother
{

public:
    KalmanSmoother();
    ~KalmanSmoother();

private:
    void setUp();

    cv::KalmanFilter m_filter;
    cv::Mat_<float> m_input;

    void filter(cv::Point2d &point);
};


class SavitzkyGolaySmoother : public EyeTrackerDataSmoother
{

public:
    SavitzkyGolaySmoother();
    ~SavitzkyGolaySmoother();

private:
    void filter(cv::Point2d &point);
};


class SmootherFactory
{

public:
    std::unordered_map<const char*, NoiseReductionMethod> methodsMap = {
            {"ma", SIMPLE_MOVING_AVERAGE},
            {"double-ma", DOUBLE_MOVING_AVERAGE},
            {"median", MEDIAN},
            {"double-exp", DOUBLE_EXP},
            {"savitzky-golay", SAVITZKY_GOLAY},
            {"kalman", KALMAN}
        };

    inline EyeTrackerDataSmoother* pickSmoother(const char* methodName)
    {
        switch (methodsMap[methodName])
        {
            case SIMPLE_MOVING_AVERAGE:
                return new MovingAverageSmoother();
            case DOUBLE_MOVING_AVERAGE:
                return new DoubleMovingAverageSmoother();
            case MEDIAN:
                return new MedianSmoother();
            case DOUBLE_EXP:
                return new DoubleExpSmoother();
            case SAVITZKY_GOLAY:
                return new SavitzkyGolaySmoother();
            case KALMAN:
                return new KalmanSmoother();
        }
    }
};

#endif
