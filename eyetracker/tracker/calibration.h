#ifndef CALIBRATION_H
#define CALIBRATION_H

#include <QDataStream>
#include <opencv2/opencv.hpp>

struct CalibrationPoint {
    cv::Point2d screenPoint;
    std::vector<cv::Point2d> eyePositions;
};

typedef std::vector<CalibrationPoint> CalibrationData;

struct EyeTrackerCalibration
{
public:
    cv::Point2d getGazePosition(const cv::Point2d & pupilPos);

    bool calibrate(const CalibrationData & calibrationData);

    friend QDataStream & operator << (QDataStream & out, const EyeTrackerCalibration & painting);
    friend QDataStream & operator >> (QDataStream & in, EyeTrackerCalibration & painting);
    
private:
    bool estimateParameters(const std::vector<cv::Point2d> & eyeData,
                            const std::vector<cv::Point2d> & calPointData);

    // cv::Matx22d m_transform;
    // cv::Vec2d m_translation;

    double m_paramX[3] = { 0, 0, 0 };
    double m_paramY[3] = { 0, 0, 0 };
};

QDataStream & operator << (QDataStream & out, const EyeTrackerCalibration & painting);
QDataStream & operator >> (QDataStream & in, EyeTrackerCalibration & painting);

#endif // CALIBRATION_H
