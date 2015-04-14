#ifndef SMOOTHER_H
#define SMOOTHER_H

#include <unordered_map>

#include <boost/circular_buffer.hpp>
#include <opencv2/opencv.hpp>

// Skeletal Joint Smoothing White Paper
// https://msdn.microsoft.com/en-us/library/jj131429.aspx


enum NoiseReductionMethod { MovingAverage, DoubleMovingAverage, Median, \
                            SavitzkyGolay, Kalman, DoubleExp, Custom };


class MovementSmoother
{

public:
    MovementSmoother();
    virtual ~MovementSmoother();

    virtual cv::Point2d filter(const cv::Point2d & point) = 0;
};


class MovementSmootherWithBuffer : public MovementSmoother
{

public:
    MovementSmootherWithBuffer();
    virtual ~MovementSmootherWithBuffer();

    cv::Point2d filter(const cv::Point2d & point) override;

protected:
   int m_bufSize;
   int m_previousPointTimestamp;

   boost::circular_buffer<double> m_bufX;
   boost::circular_buffer<double> m_bufY;
};


class MovingAverageSmoother : public MovementSmootherWithBuffer
{

public:
    MovingAverageSmoother();
    ~MovingAverageSmoother();

    cv::Point2d filter(const cv::Point2d & point);
};


class DoubleMovingAverageSmoother : public MovementSmootherWithBuffer
{

public:
    DoubleMovingAverageSmoother();
    ~DoubleMovingAverageSmoother();

    cv::Point2d filter(const cv::Point2d & point);

private:
    boost::circular_buffer<double> m_bufAveragesX;
    boost::circular_buffer<double> m_bufAveragesY;
};


class MedianSmoother : public MovementSmootherWithBuffer
{

public:
    MedianSmoother();
    ~MedianSmoother();

    cv::Point2d filter(const cv::Point2d & point);
};


class DoubleExpSmoother : public MovementSmoother
{

public:
    DoubleExpSmoother();
    ~DoubleExpSmoother();

    cv::Point2d filter(const cv::Point2d & point);

private:
    double m_gamma;
    double m_alpha;

    double m_previousOutputX;
    double m_previousOutputY;
    double m_previousTrendX;
    double m_previousTrendY;
};


class CustomSmoother : public MovementSmootherWithBuffer
{

public:
    CustomSmoother();
    ~CustomSmoother();

    cv::Point2d filter(const cv::Point2d & point);

private:
    double m_gamma;
    double m_alpha;

    double m_previousOutputX;
    double m_previousOutputY;
    double m_previousTrendX;
    double m_previousTrendY;

    double m_jitterThreshold;
};


class KalmanSmoother : public MovementSmoother
{

public:
    KalmanSmoother();
    ~KalmanSmoother();

    cv::Point2d filter(const cv::Point2d & point);

private:
    void setUp();

    cv::KalmanFilter m_filter;
    cv::Mat_<float> m_input;
};


class SavitzkyGolaySmoother : public MovementSmootherWithBuffer
{

public:
    SavitzkyGolaySmoother();
    ~SavitzkyGolaySmoother();

    cv::Point2d filter(const cv::Point2d & point);
};

#endif
