
#include "etr_main.h"
#include "cameraeyetracker.h"
#include <opencv2/opencv.hpp>

int main(int argc, char * argv[])
{
    qRegisterMetaType<cv::Mat>();
    return etr_main<CameraEyetracker>(argc, argv);
}
