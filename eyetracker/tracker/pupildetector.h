#ifndef PUPILDETECTOR_H
#define PUPILDETECTOR_H

#include "opencvcapture.h"
#include "ui_camera_setup.h"
#include <QtWidgets>
#include <QString>

class PupilDetector
{
public:
    enum Result { OK, NO_PUPIL_CANDIDATE, TOO_MANY_PUPIL_CANDIDATES };

    Result detect(const cv::Mat & frame, cv::Mat & drawFrame);

    // detection parameters
    int threshold = 27;
    int searchAreaHorizontal = 10;
    int searchAreaVertical = 10;
    unsigned int pointMin = 26;
    unsigned int pointMax = 694;

    // extra parameters
    double oblatenessLow = 0.67;
    double oblatenessHigh = 1.50;

    // output data
    double pupilX = -1;
    double pupilY = -1;
    double pupilSize = -1;

private:
    static constexpr size_t MAX_FIRST_CANDIDATES = 5;
};

QDataStream & operator << (QDataStream & out, const PupilDetector & painting);
QDataStream & operator >> (QDataStream & in, PupilDetector & painting);

class FramePupilDetector : public FrameReceiver
{
    Q_OBJECT

    Q_PROPERTY(bool grayscale READ isGrayscale WRITE setGrayscale)
    Q_PROPERTY(bool drawDebug READ drawDebug WRITE setDrawDebug)
    Q_PROPERTY(bool mirrored READ isMirrored WRITE setMirroring)

    // detection parameters
    Q_PROPERTY(int threshold READ getThreshold WRITE setThreshold)
    Q_PROPERTY(int searchAreaVertical READ getSearchAreaVertical WRITE setSearchAreaVertical)
    Q_PROPERTY(int searchAreaHorizontal READ getSearchAreaHorizontal WRITE setSearchAreaHorizontal)
    Q_PROPERTY(int pointMin READ getPointMin WRITE setPointMin)
    Q_PROPERTY(int pointMax READ getPointMax WRITE setPointMax)
    Q_PROPERTY(double oblatenessLow READ getOblatenessLow WRITE setOblatenessLow)
    Q_PROPERTY(double oblatenessHigh READ getOblatenessHigh WRITE setOblatenessHigh)

public:
    explicit FramePupilDetector(QObject * parent = 0)
        : FrameReceiver(parent)
        , m_grayscale(true)
        , m_drawDebug(true)
        , m_mirrored(false)
    {
    }

    void serialize(QDataStream & stream);
    bool deserialize(QDataStream & stream);

    inline bool isGrayscale() const { return m_grayscale; }
    inline void setGrayscale(bool value) { m_grayscale = value; }

    inline bool drawDebug() const { return m_drawDebug; }
    inline void setDrawDebug(bool value) { m_drawDebug = value; }

    inline bool isMirrored() const { return m_mirrored; }
    inline void setMirroring(bool value) { m_mirrored = value; }

    inline int getThreshold() const { return m_pupilDetector.threshold; }
    inline void setThreshold(int value) { m_pupilDetector.threshold = value; }

    inline int getSearchAreaHorizontal() const { return m_pupilDetector.searchAreaHorizontal; }
    inline void setSearchAreaHorizontal(int value) { m_pupilDetector.searchAreaHorizontal = value; }

    inline int getSearchAreaVertical() const { return m_pupilDetector.searchAreaVertical; }
    inline void setSearchAreaVertical(int value) { m_pupilDetector.searchAreaVertical = value; }

    inline int getPointMin() const { return m_pupilDetector.pointMin; }
    inline void setPointMin(int value) { m_pupilDetector.pointMin = value; }

    inline int getPointMax() const { return m_pupilDetector.pointMax; }
    inline void setPointMax(int value) { m_pupilDetector.pointMax = value; }

    inline double getOblatenessLow() const { return m_pupilDetector.oblatenessLow; }
    inline void setOblatenessLow(double value) { m_pupilDetector.oblatenessLow = value; }

    inline double getOblatenessHigh() const { return m_pupilDetector.oblatenessHigh; }
    inline void setOblatenessHigh(double value) { m_pupilDetector.oblatenessHigh = value; }

signals:
    void pupilData(bool, double, double, double);

private:
    void processFrame(cv::Mat & frame) override;

private:
    PupilDetector m_pupilDetector;
    bool m_grayscale;
    bool m_drawDebug;
    bool m_mirrored;
};

class PupilDetectorSetupWindow : public QDialog
{
    Q_OBJECT

public:
    explicit PupilDetectorSetupWindow(QWidget * parent = 0);
    ~PupilDetectorSetupWindow();

    void setVideoSource(FramePupilDetector * pupilDetector, int cameraIndex);

signals:
    void cameraIndexChanged(int);

protected:
    void showEvent(QShowEvent * event) override;
    void closeEvent(QCloseEvent * event) override;

private:
    void connectSignals();

private:
    Ui::CameraSetupForm m_gui;
    QPointer<Capture> m_capture;
    QPointer<FramePupilDetector> m_pupilDetector;
    const double oblatenessUnit = 100.0;

private slots:
    void onGrayscaleCheckBoxStateChanged(int value);
    void onDrawDebugCheckBoxStateChanged(int value);
    void onMirrorCheckBoxStateChanged(int value);
    void onThresholdSliderValueChanged(int value);
    void onSearchAreaVerticalSliderValueChanged(int value);
    void onSearchAreaHorizontalSliderValueChanged(int value);
    void onPointMinSliderValueChanged(int value);
    void onPointMaxSliderValueChanged(int value);
    void onOblatenessLowSliderValueChanged(int value);
    void onOblatenessHighSliderValueChanged(int value);
    void onCameraIndexSpinBoxValueChanged(int value);
    void onExitButtonClicked();
    void onCalibrationButtonClicked();
};

#endif // PUPILDETECTOR_H
