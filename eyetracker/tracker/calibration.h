#ifndef CALIBRATION_H
#define CALIBRATION_H

#include <QSettings>
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

    void save(QSettings & settings) const;
    void load(QSettings & settings);

    void setToZero();

private:
    bool estimateParameters(const std::vector<cv::Point2d> & eyeData,
                            const std::vector<cv::Point2d> & calPointData);

    // method 1
    cv::Mat m_transform;

    // method 2
    double m_paramX[3] = { 0, 0, 0 };
    double m_paramY[3] = { 0, 0, 0 };

    bool m_useHomography = true;
    const int m_dataPreparationMethod = 1;
};

#endif // CALIBRATION_H
