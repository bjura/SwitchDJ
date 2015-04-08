#include "eyetracker.h"

#include <QDir>
#include <QSettings>

Eyetracker::Eyetracker(QObject * parent)
    : QObject(parent)
{
}

Eyetracker::~Eyetracker()
{
}

QString Eyetracker::getBaseConfigPath() const
{
    const QDir dir(QDir::homePath() + "/.pisak/eyetracker");
    if(!dir.exists())
        dir.mkpath(".");
    return dir.filePath(getBackendCodename());
}
