TEMPLATE = app

TARGET = pisak-eyetracker-hpe

QT += core gui widgets qml quick

CONFIG += c++11

LIBS += -lGL -lGLU -lpthread -lopencv_core -lopencv_highgui -lopencv_imgproc -lopencv_calib3d -lopencv_video

INCLUDEPATH += \
    ../common

SOURCES += main.cpp \
    opencvcapture.cpp \
    pupildetector.cpp \
    ../common/eyetracker.cpp \
    ../common/smoother.cpp \
    cameraeyetracker.cpp \
    calibration.cpp \
    hpe/glm.cpp \
    hpe/hpewidget.cpp

HEADERS  += \
    opencvcapture.h \
    pupildetector.h \
    ../common/etr_main.h \
    ../common/eyetracker.h \
    ../common/smoother.h \
    cameraeyetracker.h \
    calibration.h \
    hpe/glm.h \
    hpe/pstream.h \
    hpe/hpewidget.h

FORMS += \
    camera_setup.ui

RESOURCES += \
    ../common/qml.qrc
