
QT += core gui widgets qml quick
CONFIG += c++11

TARGET = tracker
TEMPLATE = app

LIBS += -lpthread -lopencv_core -lopencv_highgui -lopencv_imgproc

INCLUDEPATH += \
    ../common

SOURCES += main.cpp \
    opencvcapture.cpp \
    pupildetector.cpp \
    ../common/eyetracker.cpp \
    cameraeyetracker.cpp \
    calibration.cpp

HEADERS  += \
    opencvcapture.h \
    pupildetector.h \
    ../common/etr_main.h \
    ../common/eyetracker.h \
    cameraeyetracker.h \
    calibration.h

FORMS += \
    camera_setup.ui

RESOURCES += \
    qml.qrc
