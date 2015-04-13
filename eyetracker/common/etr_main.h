#include <smoother.h>

#include <cstring>
#include <iostream>

#include <QApplication>
#include <QtQml>
#include <QDateTime>

template<typename EyeTrackerType>
int etr_main(int argc, char * argv[])
{
    bool trackingOnly = false;
    const char* smoothingMethod = "ma";
    if(argc > 1)
    {
        for(int i = 1; i < argc; i++)
        {
            if(std::strcmp(argv[i], "--tracking") == 0)
            {
                trackingOnly = true;
            }
            if(std::strcmp(argv[i], "--smoothing-method") == 0 && i+1 <= argc)
            {
                smoothingMethod = argv[i+1];
            }
        }
    }

    if(trackingOnly)
    {
        QCoreApplication app(argc, argv);
        EyeTrackerType tracker;

        SmootherFactory factory;
        EyeTrackerDataSmoother* smoother = factory.pickSmoother(smoothingMethod);

        QObject::connect(&tracker, &EyeTrackerType::initialized,
            [&tracker](bool success, QString errorMessage)
            {
                if(!success)
                {
                    std::cerr << "tracker initialization failed: "
                              << errorMessage.toLocal8Bit().data()
                              << std::endl;

                    QCoreApplication::instance()->exit(1);
                }
                else
                {
                    std::cout << "tracker initialized" << std::endl;
                    tracker.startTracking();
                }
            }
        );

        QObject::connect(&tracker, &EyeTrackerType::shutdownCompleted,
            [](bool success, QString errorMessage) {
                if(success)
                    std::cout << "tracker shutdown completed" << std::endl;
                else
                    std::cout << "tracker shutdown error: "
                              << errorMessage.toLocal8Bit().data()
                              << std::endl;
            }
        );

        QObject::connect(&tracker, &EyeTrackerType::gazeData,
            [&smoother](QPointF right, QPointF left)
            {
                cv::Point2d pt(-1, -1);
                if(right.x() != -1 &&
                   right.y() != -1 &&
                   left.x() != -1 &&
                   left.y() != -1)
                {
                    pt.x = 0.5 * (right.x() + left.x());
                    pt.y = 0.5 * (right.y() + left.y());
                }
                else if(right.x() != -1 && right.y() != -1)
                {
                    pt.x = right.x();
                    pt.y = right.y();
                }
                else if(left.x() != -1 && left.y() != -1)
                {
                    pt.x = left.x();
                    pt.y = left.y();
                }

                smoother->newPoint(pt, QDateTime::currentMSecsSinceEpoch());

                std::cout << "gaze_pos: " << pt.x << " " << pt.y << std::endl;
            }
        );

        if(tracker.loadConfig())
            std::cout << "configuration loaded" << std::endl;
        else
            std::cout << "error loading configuration" << std::endl;

        tracker.initialize();

        return app.exec();
    }
    else // calibration mode
    {
        QApplication app(argc, argv);

        qmlRegisterType<EyeTrackerType>("pisak.eyetracker", 1, 0, "Eyetracker");

        QQmlApplicationEngine engine;
        engine.load(QUrl(QStringLiteral("qrc:///calibration.qml")));

        return app.exec();
    }
}
