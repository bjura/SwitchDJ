#ifndef OPENCVCAPTURE_H
#define OPENCVCAPTURE_H

#include <QObject>
#include <QBasicTimer>
#include <QImage>
#include <QWidget>
#include <QPaintEvent>

#include <opencv2/opencv.hpp>

Q_DECLARE_METATYPE(cv::Mat)

class Capture : public QObject
{
    Q_OBJECT

public:
    explicit Capture(QObject * parent = 0);
    ~Capture();

signals:
    void started();
    void matReady(const cv::Mat &);

public slots:
    void start(int cam = 0);
    void stop();

private:
    void timerEvent(QTimerEvent * ev);

    QBasicTimer m_timer;
    QScopedPointer<cv::VideoCapture> m_videoCapture;
};

class FrameReceiver : public QObject
{
    Q_OBJECT

public:
    explicit FrameReceiver(QObject * parent = 0);
    void setProcessAll(bool all = true);

signals:
    void imageReady(const QImage &);

public slots:
    void newFrame(const cv::Mat & frame);

protected:
    virtual void processFrame(cv::Mat & mat);

private:
    static void matDeleter(void * mat);

    void queue(const cv::Mat & frame);
    void process(cv::Mat frame);
    void timerEvent(QTimerEvent * ev);

private:
    QBasicTimer m_timer;
    cv::Mat m_frame;
    bool m_processAll;
};

class ImageViewer : public QWidget
{
    Q_OBJECT

public:
    explicit ImageViewer(QWidget * parent = 0);

    int heightForWidth(int width) const override;

public slots:
    void setImage(const QImage & img);

private:
    void paintEvent(QPaintEvent * ev);

private:
    QImage m_img;
    double m_ratio;
};

#endif // OPENCVCAPTURE_H
