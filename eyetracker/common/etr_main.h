
#include <cstring>
#include <iostream>

#include <QApplication>
#include <QtQml>

template<typename EyeTrackerType>
int etr_main(int argc, char * argv[])
{
    bool trackingOnly = false;
    if(argc > 1)
    {
        for(int i = 1; i < argc; i++)
        {
            if(std::strcmp(argv[i], "--tracking") == 0)
            {
                trackingOnly = true;
                break;
            }
        }
    }

    if(trackingOnly)
    {
        QCoreApplication app(argc, argv);
        EyeTrackerType tracker;

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
            [](QPointF right, QPointF left)
            {
                QPointF pt(-1, -1);
                if(right.x() != -1 &&
                   right.y() != -1 &&
                   left.x() != -1 &&
                   left.y() != -1)
                {
                    pt.setX(0.5 * (right.x() + left.x()));
                    pt.setY(0.5 * (right.y() + left.y()));
                }
                else if(right.x() != -1 && right.y() != -1)
                {
                    pt = right;
                }
                else if(left.x() != -1 && left.y() != -1)
                {
                    pt = left;
                }

                std::cout << "gaze_pos: " << pt.x() << " " << pt.y() << std::endl;
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
