#ifndef PUPILDETECTOR_H
#define PUPILDETECTOR_H

#include "opencvcapture.h"
#include "ui_camera_setup.h"
#include <QtWidgets>
#include <QString>

#include <boost/algorithm/clamp.hpp>

class FramePupilDetector : public FrameReceiver
{
    Q_OBJECT

public:
    enum PupilDetectionResult { Ok, NoPupilCandidate, TooManyPupilCandidates };
    enum PreviewType { PreviewColor, PreviewGrayscale, PreviewThreshold };

    explicit FramePupilDetector(QObject * parent = 0);

    void loadSettings(QSettings & settings);
    void saveSettings(QSettings & settings) const;

    inline PreviewType previewType() const { return m_previewType; }
    inline void setPreviewType(PreviewType value) { m_previewType = value; }

    inline bool mirrored() const { return m_mirrored; }
    inline void setMirrored(bool value) { m_mirrored = value; }

    inline bool equalizeHistogram() const { return m_equalizeHistogram; }
    inline void setEqualizeHistogram(bool value) { m_equalizeHistogram = value; }

    inline float contrast() const { return m_contrast; }
    inline void setContrast(float value) { m_contrast = value; }

    inline float brightness() const { return m_brightness; }
    inline void setBrightness(float value) { m_brightness = value; }

    inline float gamma() const { return m_gamma; }
    inline void setGamma(float value) { m_gamma = value; }

    inline int threshold() const { return m_threshold; }
    inline void setThreshold(int value) { m_threshold = value; }

    inline float topMargin() const { return m_topMargin; }
    inline void setTopMargin(float value)
    {
        m_topMargin = boost::algorithm::clamp(value, 0.0, 1.0 - m_bottomMargin);
    }

    inline float bottomMargin() const { return m_bottomMargin; }
    inline void setBottomMargin(float value)
    {
        m_bottomMargin = boost::algorithm::clamp(value, 0.0, 1.0 - m_topMargin);
    }

    inline float rightMargin() const { return m_rightMargin; }
    inline void setRightMargin(float value)
    {
        m_rightMargin = boost::algorithm::clamp(value, 0.0, 1.0 - m_leftMargin);
    }

    inline float leftMargin() const { return m_leftMargin; }
    inline void setLeftMargin(float value)
    {
        m_leftMargin = boost::algorithm::clamp(value, 0.0, 1.0 - m_rightMargin);
    }

    inline int pointsMin() const { return m_pointsMin; }
    inline void setPointsMin(int value) { m_pointsMin = value; }

    inline int pointsMax() const { return m_pointsMax; }
    inline void setPointsMax(int value) { m_pointsMax = value; }

    inline float oblatenessLow() const { return m_oblatenessLow; }
    inline void setOblatenessLow(float value) { m_oblatenessLow = value; }

    inline float oblatenessHigh() const { return m_oblatenessHigh; }
    inline void setOblatenessHigh(float value) { m_oblatenessHigh = value; }

signals:
    void pupilData(bool, double, double, double);

private:
    void processFrame(cv::Mat & frame) override;

private:
    PreviewType m_previewType;

    // image preprocessing parameters
    bool m_mirrored = true;
    bool m_equalizeHistogram = false;
    float m_contrast = 1.0;
    float m_brightness = 0.0;
    float m_gamma = 1.0;
    int m_threshold = 27;

    // search area margins - floats from 0.0 to 1.0
    float m_topMargin    = 0.0;
    float m_bottomMargin = 0.0;
    float m_leftMargin   = 0.0;
    float m_rightMargin  = 0.0;

    // minimal and maximal number of points in contour
    unsigned int m_pointsMin = 25;
    unsigned int m_pointsMax = 690;

    // extra parameters
    float m_oblatenessLow = 0.67;
    float m_oblatenessHigh = 1.50;

    // output data
    float m_pupilX = -1.0;
    float m_pupilY = -1.0;
    float m_pupilSize = -1.0;

    // pupil detection algorithm
    PupilDetectionResult detect(const cv::Mat & frame, cv::Mat & drawFrame);
    static constexpr size_t MAX_FIRST_CANDIDATES = 6;
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
    Ui::CameraSetupForm m_gui;
    QPointer<FramePupilDetector> m_pupilDetector;
    const float m_marginCoeff = 100.0;
    const float m_contrastCoeff = 100.0;
    const float m_brightnessCoeff = 1.0;
    const float m_gammaCoeff = 100.0;
    const float m_oblatenessCoeff = 50.0;
};

#endif // PUPILDETECTOR_H
