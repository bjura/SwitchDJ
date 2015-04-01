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

void Eyetracker::setParameter(QString name, QVariant value)
{
    m_params[name] = value;
}

QVariant Eyetracker::getParameter(QString name) const
{
    if(m_params.contains(name))
       return m_params[name];
    else
        return QVariant();
}

bool Eyetracker::saveParameters() const
{
    QSettings settings(getConfigFilePath(), QSettings::IniFormat);
    if(settings.status() != QSettings::NoError)
        return false;

    settings.clear();

    auto i = m_params.constBegin();
    while(i != m_params.constEnd())
    {
        settings.setValue(i.key(), i.value());
        ++i;
    }

    settings.sync();

    if(settings.status() != QSettings::NoError)
        return false;
    else
        return true;
}

bool Eyetracker::loadParameters()
{
    QSettings settings(getConfigFilePath(), QSettings::IniFormat);
    if(settings.status() != QSettings::NoError)
        return false;

    m_params.clear();

    QStringList keys = settings.allKeys();

    for(int i = 0; i < keys.size(); i++)
        m_params[keys[i]] = settings.value(keys[i]);

    return true;
}

QString Eyetracker::getBaseConfigPath() const
{
    const QDir dir(QDir::homePath() + "/.pisak/eyetracker");
    if(!dir.exists())
        dir.mkpath(".");
    return dir.filePath(getBackendCodename());
}

QString Eyetracker::getConfigFilePath() const
{
    return tr("%1.ini").arg(getBaseConfigPath());
}

QString Eyetracker::getCalibrationFilePath() const
{
    return tr("%1.calibration").arg(getBaseConfigPath());
}
