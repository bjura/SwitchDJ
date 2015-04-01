#include "pupildetector.h"

static inline cv::Mat correctGamma(cv::Mat & img, double gamma)
{
    const double inverse_gamma = 1.0 / gamma;

    cv::Mat lut_matrix(1, 256, CV_8UC1);
    uchar * ptr = lut_matrix.ptr();
    for(int i = 0; i < 256; i++)
        ptr[i] = int(pow(double(i) / 255.0, inverse_gamma) * 255.0);

    cv::Mat result;
    cv::LUT(img, lut_matrix, result);

    return result;
}

static inline void drawPupil(cv::Mat & img,
                             const cv::RotatedRect & box,
                             const cv::Scalar & color,
                             int thickness)
{
    const int crossSize = 20;

    cv::ellipse(img, box, color, thickness);

    cv::line(img,
             cv::Point2f(box.center.x, box.center.y - crossSize),
             cv::Point2f(box.center.x, box.center.y + crossSize),
             color
    );

    cv::line(img,
             cv::Point2f(box.center.x - crossSize, box.center.y),
             cv::Point2f(box.center.x + crossSize, box.center.y),
             color
    );
}

PupilDetector::Result PupilDetector::detect(const cv::Mat & frame,
                                            cv::Mat & drawFrame)
{
    cv::Mat tmp;

    // find areas darker than threshold
    cv::threshold(frame, tmp, threshold, 255, CV_THRESH_BINARY);

    if(!drawFrame.empty())
    {
        const cv::Point points[4] = {
            cv::Point(searchAreaHorizontal, searchAreaVertical),
            cv::Point(drawFrame.cols - searchAreaHorizontal, searchAreaVertical),
            cv::Point(drawFrame.cols - searchAreaHorizontal, drawFrame.rows - searchAreaVertical),
            cv::Point(searchAreaHorizontal, drawFrame.rows - searchAreaVertical)
        };
        const auto color = cv::Scalar(255, 255, 255);
        cv::line(drawFrame, points[0], points[1], color);
        cv::line(drawFrame, points[1], points[2], color);
        cv::line(drawFrame, points[2], points[3], color);
        cv::line(drawFrame, points[3], points[0], color);
    }

    std::vector<std::vector<cv::Point>> contours;
    std::vector<cv::Vec4i> hierarchy;

    cv::findContours(tmp, contours,
                     hierarchy,
                     CV_RETR_TREE,
                     CV_CHAIN_APPROX_NONE);

    // paint dark areas blue.
    /*if(!drawFrame.empty())
    {
        for(int y = 0; y < frame.rows; y++)
        {
            for(int x = 0; x < frame.cols; x++)
            {
                if(frame.at<unsigned char>(x,y) <= 10)
                {
                    cv::Vec3b px = drawFrame.at<cv::Vec3b>(x,y);
                    px[0] = 255;
                    //drawFrame.at<cv::Vec3b>(x,y) = val;
                }
            }
        }
    }*/

    cv::RotatedRect firstCandidateRects[MAX_FIRST_CANDIDATES];
    size_t numCandidates = 0;

    // find pupil candidates
    for(const auto & contour : contours)
    {
        // contour of the area is too short or too long
        if(contour.size() < pointMin || contour.size() > pointMax)
            continue;

        const cv::RotatedRect r = cv::fitEllipse(contour);

        // Is the center of ellipse in dark area?
        // TODO: this crashes
        /*const unsigned char* p = tmp.ptr<unsigned char>((int)(r.center.y) - 0);
        if(p[(int)(r.center.x) - 0] > 0)
        {
            //The center is NOT in dark area.
            continue;
        }*/

        if(r.size.height / r.size.width > oblatenessLow &&
           r.size.height / r.size.width < oblatenessHigh &&
           r.center.x > searchAreaHorizontal &&
           r.center.y > searchAreaVertical &&
           r.center.x < frame.cols - searchAreaHorizontal &&
           r.center.y < frame.rows - searchAreaVertical)
        {
            if(!drawFrame.empty())
                drawPupil(drawFrame, r, CV_RGB(0, 255, 0), 1);

            firstCandidateRects[numCandidates] = r;
            numCandidates++;

            if(numCandidates >= MAX_FIRST_CANDIDATES)
                break;
        }
    }

    if(numCandidates == 0)
    {
        if(!drawFrame.empty())
            cv::putText(drawFrame,
                        "NO_PUPIL_CANDIDATE",
                        cv::Point2d(0, 16),
                        cv::FONT_HERSHEY_PLAIN,
                        1.0,
                        CV_RGB(255, 0, 0)
            );
        return NO_PUPIL_CANDIDATE;
    }
    else if(numCandidates >= MAX_FIRST_CANDIDATES)
    {
        if(!drawFrame.empty())
            cv::putText(drawFrame,
                        "TOO_MANY_PUPIL_CANDIDATES",
                        cv::Point2d(0, 16),
                        cv::FONT_HERSHEY_PLAIN,
                        1.0,
                        CV_RGB(255, 0, 0)
            );
        return TOO_MANY_PUPIL_CANDIDATES;
    }
    else
    {
        if(!drawFrame.empty())
            cv::putText(drawFrame,
                        "PUPIL_DETECTED",
                        cv::Point2d(0, 16),
                        cv::FONT_HERSHEY_PLAIN,
                        1.0,
                        CV_RGB(0, 255, 0)
            );
    }

    std::array<double, MAX_FIRST_CANDIDATES> candidateSizes{{}};

    for(size_t i = 0; i < numCandidates; i++)
    {
        const auto & size = firstCandidateRects[i].size;
        // size if proportional to area
        candidateSizes[i] = double(size.width) * double(size.height);
    }

    // find candidate with largest size
    const cv::RotatedRect pupilRect =
            firstCandidateRects[
                std::distance(candidateSizes.begin(),
                              std::max_element(candidateSizes.begin(), candidateSizes.end()))
            ];

    if(!drawFrame.empty())
        drawPupil(drawFrame, pupilRect, CV_RGB(0, 255, 192), 2);

    pupilX = pupilRect.center.x;
    pupilY = pupilRect.center.y;
    pupilSize = pupilRect.size.width * pupilRect.size.height / 4.0; // area

    return OK;
}

QDataStream & operator << (QDataStream & out, const PupilDetector & detector)
{
    out << detector.threshold
        << detector.searchAreaHorizontal
        << detector.searchAreaVertical
        << detector.pointMax
        << detector.pointMin
        << detector.oblatenessHigh
        << detector.oblatenessLow;
    return out;
}

QDataStream & operator >> (QDataStream & in, PupilDetector & detector)
{
    in >> detector.oblatenessLow
       >> detector.oblatenessHigh
       >> detector.pointMin
       >> detector.pointMax
       >> detector.searchAreaVertical
       >> detector.searchAreaHorizontal
       >> detector.threshold;
    return in;
}

void FramePupilDetector::serialize(QDataStream & stream)
{
    stream << m_pupilDetector;
}

bool FramePupilDetector::deserialize(QDataStream & stream)
{
    stream >> m_pupilDetector;
    return stream.status() == QDataStream::Ok;
}

void FramePupilDetector::processFrame(cv::Mat & frame)
{
    if(m_mirrored)
        cv::flip(frame, frame, 1);

    cv::Mat monoFrame;
    cv::cvtColor(frame, monoFrame, CV_BGR2GRAY);

    if(m_grayscale)
        cv::cvtColor(monoFrame, frame, CV_GRAY2BGR);

    cv::Mat empty;
    const PupilDetector::Result result =
        m_pupilDetector.detect(monoFrame, m_drawDebug ? frame : empty);

    emit pupilData(result == PupilDetector::OK,
                   m_pupilDetector.pupilX,
                   m_pupilDetector.pupilY,
                   m_pupilDetector.pupilSize);
}

//---------------------------------------------------------------------------------

PupilDetectorSetupWindow::PupilDetectorSetupWindow(QWidget * parent)
    : QDialog(parent)
    , m_pupilDetector(nullptr)
{
    m_gui.setupUi(this);

    connect(m_gui.cameraIndexSpinBox, SIGNAL(valueChanged(int)), [](){
        // do not emit cameraIndexChanged when co pupilDetector connected
        if(m_pupilDetector)
            emit cameraIndexChanged(value);
    });

    connect(m_gui.drawDebugCheckBox, SIGNAL(stateChanged(int)), this, SLOT(onDrawDebugCheckBoxStateChanged(int)));
    connect(m_gui.grayscaleCheckBox, SIGNAL(stateChanged(int)), this, SLOT(onGrayscaleCheckBoxStateChanged(int)));
    connect(m_gui.mirrorCheckBox, SIGNAL(stateChanged(int)), this, SLOT(onMirrorCheckBoxStateChanged(int)));
    connect(m_gui.thresholdSlider, SIGNAL(valueChanged(int)), this, SLOT(onThresholdSliderValueChanged(int)));
    connect(m_gui.searchAreaHorizontalSlider, SIGNAL(valueChanged(int)), this, SLOT(onSearchAreaHorizontalSliderValueChanged(int)));
    connect(m_gui.searchAreaVerticalSlider, SIGNAL(valueChanged(int)), this, SLOT(onSearchAreaVerticalSliderValueChanged(int)));
    connect(m_gui.pointMinSlider, SIGNAL(valueChanged(int)), this, SLOT(onPointMinSliderValueChanged(int)));
    connect(m_gui.pointMaxSlider, SIGNAL(valueChanged(int)), this, SLOT(onPointMaxSliderValueChanged(int)));
    connect(m_gui.oblatenessLowSlider, SIGNAL(valueChanged(int)), this, SLOT(onOblatenessLowSliderValueChanged(int)));
    connect(m_gui.oblatenessHighSlider, SIGNAL(valueChanged(int)), this, SLOT(onOblatenessHighSliderValueChanged(int)));
    connect(m_gui.calibrationButton, SIGNAL(clicked(bool)), this, SLOT(onCalibrationButtonClicked()));
    connect(m_gui.exitButton, SIGNAL(clicked(bool)), this, SLOT(onExitButtonClicked()));
}

PupilDetectorSetupWindow::~PupilDetectorSetupWindow()
{
    setVideoSource(nullptr, 0); // disconnect from m_pupilDetector
}

void PupilDetectorSetupWindow::setVideoSource(FramePupilDetector * pupilDetector, int cameraIndex)
{
    if(m_pupilDetector)
        m_gui.cameraView->disconnect();

    m_pupilDetector = pupilDetector;

    if(!m_pupilDetector)
        return;

    m_gui.cameraView->connect(m_pupilDetector, SIGNAL(imageReady(QImage)), SLOT(setImage(QImage)));

    qDebug() << "Video source connected...";

    m_gui.cameraIndexSpinBox->setValue(cameraIndex);
    m_gui.grayscaleCheckBox->setChecked(m_pupilDetector->isGrayscale());
    m_gui.drawDebugCheckBox->setChecked(m_pupilDetector->drawDebug());
    m_gui.mirrorCheckBox->setChecked(m_pupilDetector->isMirrored());
    m_gui.thresholdSlider->setValue(m_pupilDetector->getThreshold());
    m_gui.searchAreaHorizontalSlider->setValue(m_pupilDetector->getSearchAreaHorizontal());
    m_gui.searchAreaVerticalSlider->setValue(m_pupilDetector->getSearchAreaVertical());
    m_gui.pointMinSlider->setValue(m_pupilDetector->getPointMin());
    m_gui.pointMaxSlider->setValue(m_pupilDetector->getPointMax());
    m_gui.oblatenessLowSlider->setValue(int(m_pupilDetector->getOblatenessLow() * oblatenessUnit));
    m_gui.oblatenessHighSlider->setValue(int(m_pupilDetector->getOblatenessHigh() * oblatenessUnit));
}

void PupilDetectorSetupWindow::onGrayscaleCheckBoxStateChanged(int value)
{
    if(m_pupilDetector)
        m_pupilDetector->setGrayscale(value != 0);
}

void PupilDetectorSetupWindow::onDrawDebugCheckBoxStateChanged(int value)
{
    if(m_pupilDetector)
        m_pupilDetector->setDrawDebug(value != 0);
}

void PupilDetectorSetupWindow::onMirrorCheckBoxStateChanged(int value)
{
    if(m_pupilDetector)
        m_pupilDetector->setMirroring(value != 0);
}

void PupilDetectorSetupWindow::onThresholdSliderValueChanged(int value)
{
    m_gui.thresholdValueLabel->setText(QString::number(value));
    if(m_pupilDetector)
        m_pupilDetector->setThreshold(value);
}

void PupilDetectorSetupWindow::onSearchAreaVerticalSliderValueChanged(int value)
{
    m_gui.searchAreaVerticalValueLabel->setText(QString::number(value));
    if(m_pupilDetector)
        m_pupilDetector->setSearchAreaVertical(value);
}

void PupilDetectorSetupWindow::onSearchAreaHorizontalSliderValueChanged(int value)
{
    m_gui.searchAreaHorizontalValueLabel->setText(QString::number(value));
    if(m_pupilDetector)
        m_pupilDetector->setSearchAreaHorizontal(value);
}

void PupilDetectorSetupWindow::onPointMinSliderValueChanged(int value)
{
    m_gui.pointMinValueLabel->setText(QString::number(value));
    if(m_pupilDetector)
        m_pupilDetector->setPointMin(value);
}

void PupilDetectorSetupWindow::onPointMaxSliderValueChanged(int value)
{
    m_gui.pointMaxValueLabel->setText(QString::number(value));
    if(m_pupilDetector)
        m_pupilDetector->setPointMax(value);
}

void PupilDetectorSetupWindow::onOblatenessLowSliderValueChanged(int value)
{
    const double doubleValue = double(value) / oblatenessUnit;
    m_gui.oblatenessLowValueLabel->setText(QString::number(doubleValue));
    if(m_pupilDetector)
        m_pupilDetector->setOblatenessLow(doubleValue);
}

void PupilDetectorSetupWindow::onOblatenessHighSliderValueChanged(int value)
{
    const double doubleValue = double(value) / oblatenessUnit;
    m_gui.oblatenessHighValueLabel->setText(QString::number(doubleValue));
    if(m_pupilDetector)
        m_pupilDetector->setOblatenessHigh(doubleValue);
}

void PupilDetectorSetupWindow::onCameraIndexSpinBoxValueChanged(int value)
{
}

void PupilDetectorSetupWindow::showEvent(QShowEvent * event)
{
    Q_UNUSED(event);
    setResult(-1);
}

void PupilDetectorSetupWindow::closeEvent(QCloseEvent * event)
{
    Q_UNUSED(event);
    qDebug() << "Video source disconnected";
    setVideoSource(nullptr, 0);
    emit finished(result() == QDialog::Accepted);
}

void PupilDetectorSetupWindow::onCalibrationButtonClicked()
{
    accept();
    close();
}

void PupilDetectorSetupWindow::onExitButtonClicked()
{
    reject();
    close();
}
