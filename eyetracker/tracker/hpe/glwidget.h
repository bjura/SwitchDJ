/*
 * This file is part of Head Pose Estimation.
 *
 * This program is free software: you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation, either version 3 of the License, or
 * (at your option) any later version.
 *
 * This program is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 *
 * You should have received a copy of the GNU General Public License
 * along with this program. If not, see <http://www.gnu.org/licenses/>.
 *
 * Copyright 2015, Alex Khrabrov <alex@mroja.net>
 *
 */

#ifndef GLWIDGET_H
#define GLWIDGET_H

#include <QOpenGLWidget>
#include <opencv/cv.h>
#include "glm.h"

class GLWidget : public QOpenGLWidget
{
    Q_OBJECT
public:
    explicit GLWidget(QWidget * parent = 0);

signals:

public slots:

protected:
    void initializeGL() override;
    void paintGL() override;
    void resizeGL(int w, int h) override;

private:

    // 3d model reference points
    cv::Mat m_modelPoints3d;

    // object orientation
    double m_rot[9] = { 0 }; // opengl rotation matrix
    std::vector<double> m_tv; // opengl translation vector
    std::vector<double> m_rv;

    cv::Mat m_rvec;
    cv::Mat m_tvec;

    GLMmodel * m_headObj = nullptr;

    std::vector<cv::Point2f> estimatePose(const std::vector<cv::Point2f> & markers,
                                          const cv::Mat & img);
    void idle();
};

#endif // GLWIDGET_H
