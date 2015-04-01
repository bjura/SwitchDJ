#ifndef SMOOTHER_H
#define SMOOTHER_H

// Skeletal Joint Smoothing White Paper
// https://msdn.microsoft.com/en-us/library/jj131429.aspx

// enum NoiseReductionMethod { MOVING_AVERAGE, MEDIAN, KALMAN, JITTER_REMOVAL, OTHER? };

class EyetrackerDataSmoother
{
	
	EyetrackerDataSmoother();
	~EyetrackerDataSmoother();

	// returns smoothed points
	virtual cv::Point2d newPoint(const cv::Point2d & point, double timestamp);

};

#endif
