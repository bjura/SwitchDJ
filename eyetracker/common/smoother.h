#ifndef SMOOTHER_H
#define SMOOTHER_H

#include <unordered_map>

#include <boost/circular_buffer.hpp>
#include <opencv2/opencv.hpp>

// Skeletal Joint Smoothing White Paper
// https://msdn.microsoft.com/en-us/library/jj131429.aspx


enum class SmoothingMethod {
    None,
    MovingAverage,
    DoubleMovingAverage,
    Median,
    Kalman,
    DoubleExp,
    Custom
};


class MovementSmoother
{
public:
    virtual ~MovementSmoother();

    virtual cv::Point2d filter(const cv::Point2d & point) = 0;
};


class NullSmoother final : public MovementSmoother
{
public:
    cv::Point2d filter(const cv::Point2d & point) override;
};


class MovementSmootherWithBuffer : public MovementSmoother
{
public:
    MovementSmootherWithBuffer();

protected:
   int m_bufSize;
   int m_previousPointTimestamp;

   boost::circular_buffer<double> m_bufX;
   boost::circular_buffer<double> m_bufY;
};


class MovingAverageSmoother final : public MovementSmootherWithBuffer
{
public:
    cv::Point2d filter(const cv::Point2d & point) override;
};


class DoubleMovingAverageSmoother final : public MovementSmootherWithBuffer
{
public:
    DoubleMovingAverageSmoother();

    cv::Point2d filter(const cv::Point2d & point) override;

private:
    boost::circular_buffer<double> m_bufAveragesX;
    boost::circular_buffer<double> m_bufAveragesY;
};


class MedianSmoother final : public MovementSmootherWithBuffer
{
public:
    cv::Point2d filter(const cv::Point2d & point) override;
};


class DoubleExpSmoother final : public MovementSmoother
{
public:
    DoubleExpSmoother();

    cv::Point2d filter(const cv::Point2d & point) override;

private:
    double m_gamma;
    double m_alpha;

    double m_previousOutputX;
    double m_previousOutputY;
    double m_previousTrendX;
    double m_previousTrendY;
};


class CustomSmoother final : public MovementSmootherWithBuffer
{
public:
    CustomSmoother();

    cv::Point2d filter(const cv::Point2d & point) override;

private:
    double m_gamma;
    double m_alpha;

    double m_previousOutputX;
    double m_previousOutputY;
    double m_previousTrendX;
    double m_previousTrendY;

    double m_jitterThreshold;
};


class KalmanSmoother final : public MovementSmoother
{
public:
    KalmanSmoother();

    cv::Point2d filter(const cv::Point2d & point) override;

private:
    cv::KalmanFilter m_filter;
    cv::Mat_<float> m_input;

    double m_previousOutputX;
    double m_previousOutputY;
};

#endif
