
QT     += core gui widgets
CONFIG += c++11

LIBS += -lGL -lGLU -lopencv_core -lopencv_highgui -lopencv_imgproc -lopencv_calib3d -lopencv_video

TARGET = hpe
TEMPLATE = app

SOURCES += main.cpp \
    mainwindow.cpp \
    glwidget.cpp \
    glm.cpp

HEADERS  += mainwindow.h \
    glwidget.h \
    glm.h \
    pstream.h
