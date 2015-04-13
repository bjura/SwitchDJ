#ifndef SMOOTHER_H
#define SMOOTHER_H

#include <unordered_map>

#include <boost/circular_buffer.hpp>
#include <opencv2/opencv.hpp>

#include <QPointF>

// Skeletal Joint Smoothing White Paper
// https://msdn.microsoft.com/en-us/library/jj131429.aspx


enum NoiseReductionMethod { MovingAverage, DoubleMovingAverage, Median, \
                            SavitzkyGolay, Kalman, DoubleExp, Custom };


class EyeTrackerDataSmoother
{

public:
    EyeTrackerDataSmoother();
    ~EyeTrackerDataSmoother();

    void newPoint(QPointF &point);

protected:
    int m_previousPointTime;
    int m_bufferSize;

    boost::circular_buffer<double> m_inputDataXBuffer;
    boost::circular_buffer<double> m_inputDataYBuffer;

    virtual void filter(QPointF &point);
};

class MovingAverageSmoother : public EyeTrackerDataSmoother
{

public:
    MovingAverageSmoother();
    ~MovingAverageSmoother();

private:
    void filter(QPointF &point);
};


class DoubleMovingAverageSmoother : public EyeTrackerDataSmoother
{

public:
    DoubleMovingAverageSmoother();
    ~DoubleMovingAverageSmoother();

private:
    boost::circular_buffer<double> m_meansXBuffer;
    boost::circular_buffer<double> m_meansYBuffer;

    void filter(QPointF &point);
};


class MedianSmoother : public EyeTrackerDataSmoother
{

public:
    MedianSmoother();
    ~MedianSmoother();

private:
    void filter(QPointF &point);
};


class DoubleExpSmoother : public EyeTrackerDataSmoother
{

public:
    DoubleExpSmoother();
    ~DoubleExpSmoother();

private:
    double gamma;
    double alpha;

    double m_previousOutputX;
    double m_previousOutputY;
    double m_previousTrendX;
    double m_previousTrendY;

    void filter(QPointF &point);
};


class CustomSmoother : public EyeTrackerDataSmoother
{

public:
    CustomSmoother();
    ~CustomSmoother();

private:
    double gamma;
    double alpha;

    double m_previousOutputX;
    double m_previousOutputY;
    double m_previousTrendX;
    double m_previousTrendY;

    double m_jitterThreshold;

    void filter(QPointF &point);
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

    void filter(QPointF &point);
};


class SavitzkyGolaySmoother : public EyeTrackerDataSmoother
{

public:
    SavitzkyGolaySmoother();
    ~SavitzkyGolaySmoother();

private:
    void filter(QPointF &point);
};

#endif
