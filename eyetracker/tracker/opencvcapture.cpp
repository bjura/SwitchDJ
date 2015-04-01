
#include "opencvcapture.h"
#include <QDebug>
#include <QPainter>

Capture::Capture(QObject * parent)
    : QObject(parent)
{
}

Capture::~Capture()
{
    stop();
}

void Capture::start(int cam)
{
    stop();

    m_videoCapture.reset(new cv::VideoCapture(cam));

    if(m_videoCapture->isOpened())
    {
        m_timer.start(0, this);
        emit started();
    }
    else
    {
        m_videoCapture.reset(nullptr);
    }
}

void Capture::stop()
{
    m_timer.stop();
    m_videoCapture.reset(nullptr);
}

void Capture::timerEvent(QTimerEvent * ev)
{
    if(!m_videoCapture || ev->timerId() != m_timer.timerId())
        return;

    cv::Mat frame;

    // Blocks until a new frame is ready
    if(!m_videoCapture->read(frame))
    {
        qDebug() << "read frame failed";
        m_timer.stop();
        return;
    }

    emit matReady(frame);
}

//-----------------------------------------------------------------------------

FrameReceiver::FrameReceiver(QObject * parent)
    : QObject(parent)
    , m_processAll(true)
{
}

void FrameReceiver::setProcessAll(bool all)
{
    m_processAll = all;
}

void FrameReceiver::newFrame(const cv::Mat & frame)
{
    if(m_processAll)
        process(frame);
    else
        queue(frame);
}

void FrameReceiver::processFrame(cv::Mat & mat)
{
    Q_UNUSED(mat); // do nothing
}

void FrameReceiver::matDeleter(void * mat)
{
    delete static_cast<cv::Mat *>(mat);
}

void FrameReceiver::queue(const cv::Mat & frame)
{
    if(!m_frame.empty())
        qDebug() << "Converter dropped frame!";
    m_frame = frame;
    if(!m_timer.isActive())
        m_timer.start(0, this);
}

void FrameReceiver::process(cv::Mat frame)
{
    processFrame(frame);

    cv::cvtColor(frame, frame, CV_BGR2RGB);

    const QImage image(
        frame.data,
        frame.cols,
        frame.rows,
        frame.step,
        QImage::Format_RGB888,
        &matDeleter,
        new cv::Mat(frame)
    );

    Q_ASSERT(image.constBits() == frame.data);

    emit imageReady(image);
}

void FrameReceiver::timerEvent(QTimerEvent * ev)
{
    if(ev->timerId() != m_timer.timerId())
        return;

    process(m_frame);
    m_frame.release();
    m_timer.stop();
}

//-----------------------------------------------------------------------------

ImageViewer::ImageViewer(QWidget * parent)
    : QWidget(parent)
    , m_ratio(0.75)
{
    setAttribute(Qt::WA_OpaquePaintEvent);
    QSizePolicy p(sizePolicy());
    p.setHeightForWidth(true);
    setSizePolicy(p);
}

int ImageViewer::heightForWidth(int width) const
{
    return int(0.5 + m_ratio * width);
}

void ImageViewer::setImage(const QImage & img)
{
    m_img = img;
    update();

    if(m_img.isNull() || m_img.width() <= 0 ||  m_img.height() <= 0)
        return;

    const double ratio = double(m_img.width()) / double(m_img.height());
    if(m_ratio != ratio)
    {
        resize(width(), int(0.5 + m_ratio * width()));
        m_ratio = ratio;
    }
}

void ImageViewer::paintEvent(QPaintEvent * ev)
{
    Q_UNUSED(ev);

    QPainter p(this);
    p.setRenderHint(QPainter::Antialiasing);
    p.setRenderHint(QPainter::SmoothPixmapTransform);
    p.drawImage(QRect(0, 0, width(), height()), m_img,
                QRect(0, 0, m_img.width(), m_img.height()));
    m_img = QImage();
}
