TEMPLATE = app

QT += qml quick widgets
CONFIG += c++11

SOURCES += main.cpp \
    ../common/eyetracker.cpp \
    tobiieyetracker.cpp

RESOURCES += qml.qrc

INCLUDEPATH += \
    ../tobii/sdk/include \
    ../common

LIBPATH += ../tobii/sdk/lib

LIBS += -ltobiigazecore

# Additional import path used to resolve QML modules in Qt Creator's code model
QML_IMPORT_PATH =

# Default rules for deployment.
include(deployment.pri)

HEADERS += \
    ../common/eyetracker.h \
    tobiieyetracker.h \
    ../common/etr_main.h

