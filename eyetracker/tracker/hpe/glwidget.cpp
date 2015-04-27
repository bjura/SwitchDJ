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

/*
 * This code uses SolidTetrahedron drawing code from FreeGLUT.
 *
 * FreeGLUT Copyright (c) 1999-2000 Pawel W. Olszta. All Rights Reserved.
 *
 * Permission is hereby granted, free of charge, to any person obtaining a
 * copy of this software and associated documentation files (the "Software"),
 * to deal in the Software without restriction, including without limitation
 * the rights to use, copy, modify, merge, publish, distribute, sublicense,
 * and/or sell copies of the Software, and to permit persons to whom the
 * Software is furnished to do so, subject to the following conditions:
 *
 * The above copyright notice and this permission notice shall be included
 * in all copies or substantial portions of the Software.
 *
 * THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS
 * OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
 * FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.  IN NO EVENT SHALL
 * PAWEL W. OLSZTA BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER
 * IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN
 * CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
 */

#include "glwidget.h"
#include "glm.h"
#include <GL/glu.h>

static void drawSolidCylinder(GLdouble radius,
                              GLdouble height,
                              GLint slices,
                              GLint stacks)
{
    GLUquadricObj * qobj = gluNewQuadric();
    gluQuadricDrawStyle(qobj, GLU_FILL);
    gluCylinder(qobj, radius, radius, height, stacks, slices);
    gluDeleteQuadric(qobj);
}

void drawSolidTetrahedron(void)
{
    /* Magic Numbers:  r0 = ( 1, 0, 0 )
     *                 r1 = ( -1/3, 2 sqrt(2) / 3, 0 )
     *                 r2 = ( -1/3, -sqrt(2) / 3, sqrt(6) / 3 )
     *                 r3 = ( -1/3, -sqrt(2) / 3, -sqrt(6) / 3 )
     * |r0| = |r1| = |r2| = |r3| = 1
     * Distance between any two points is 2 sqrt(6) / 3
     *
     * Normals:  The unit normals are simply the negative of the coordinates of the point not on the surface.
     */

    const double r0[3] = {             1.0,             0.0,             0.0 };
    const double r1[3] = { -0.333333333333,  0.942809041582,             0.0 };
    const double r2[3] = { -0.333333333333, -0.471404520791,  0.816496580928 };
    const double r3[3] = { -0.333333333333, -0.471404520791, -0.816496580928 };

    glBegin(GL_TRIANGLES);
        glNormal3d(-1.0, 0.0, 0.0);
        glVertex3dv(r1);
        glVertex3dv(r3);
        glVertex3dv(r2);
        glNormal3d(0.333333333333, -0.942809041582, 0.0);
        glVertex3dv(r0);
        glVertex3dv(r2);
        glVertex3dv(r3);
        glNormal3d(0.333333333333, 0.471404520791, -0.816496580928);
        glVertex3dv(r0);
        glVertex3dv(r3);
        glVertex3dv(r1);
        glNormal3d(0.333333333333, 0.471404520791, 0.816496580928);
        glVertex3dv(r0);
        glVertex3dv(r1);
        glVertex3dv(r2);
    glEnd() ;
}

static void drawAxes()
{
    // Z = red
    glPushMatrix();
        glRotated(180, 0, 1, 0);
        glColor4d(1, 0, 0, 0.5);
        drawSolidCylinder(0.05, 1, 15, 20);
        glBegin(GL_LINES);
            glVertex3d(0, 0, 0);
            glVertex3d(0, 0, 1);
        glEnd();
        glTranslated(0, 0, 1);
        glScaled(0.1, 0.1, 0.1);
        drawSolidTetrahedron();
    glPopMatrix();

    // Y = green
    glPushMatrix();
        glRotated(-90, 1, 0, 0);
        glColor4d(0, 1, 0, 0.5);
        drawSolidCylinder(0.05, 1, 15, 20);
        glBegin(GL_LINES);
            glVertex3d(0, 0, 0);
            glVertex3d(0, 0, 1);
        glEnd();
        glTranslated(0, 0, 1);
        glScaled(0.1, 0.1, 0.1);
        drawSolidTetrahedron();
    glPopMatrix();

    // X = blue
    glPushMatrix();
        glRotated(-90, 0, 1, 0);
        glColor4d(0, 0, 1, 0.5);
        drawSolidCylinder(0.05, 1, 15, 20);
        glBegin(GL_LINES);
            glVertex3d(0, 0, 0);
            glVertex3d(0, 0, 1);
        glEnd();
        glTranslated(0, 0, 1);
        glScaled(0.1, 0.1, 0.1);
        drawSolidTetrahedron();
    glPopMatrix();
}

//--------------------------------------------------------------------------------------------------

GLWidget::GLWidget(QWidget * parent)
    : QOpenGLWidget(parent)
{
    // init Kalman filter
    //initKalmanFilter(KF, nStates, nMeasurements, nInputs, dt);
    //measurements.setTo(cv::Scalar(0));

    m_headObj = glmReadOBJ("head-obj.obj");

    double avgX = 0;
    double avgY = 0;
    double avgZ = 0;
    for(GLuint i = 1; i <= m_headObj->numvertices; i++)
    {
        avgX += m_headObj->vertices[3 * i + 0];
        avgY += m_headObj->vertices[3 * i + 1];
        avgZ += m_headObj->vertices[3 * i + 2];
    }
    avgX /= m_headObj->numvertices;
    avgY /= m_headObj->numvertices;
    avgZ /= m_headObj->numvertices;

    std::cout << "model mean:" << avgX << " " << avgY << " " << avgZ << std::endl;

    for(GLuint i = 1; i <= m_headObj->numvertices; i++)
    {
        m_headObj->vertices[3 * i + 0] -= avgX;
        m_headObj->vertices[3 * i + 1] -= avgY;
        //m_headObj->vertices[3 * i + 2] -= avgZ;
    }

    // feature points (in head-obj.obj coordinates)
    std::vector<cv::Point3f> modelPoints;

    // four points
    modelPoints.push_back(cv::Point3f(85.60, 234.44, 20.02));
    modelPoints.push_back(cv::Point3f(-2.92, 238.53, 20.02));
    modelPoints.push_back(cv::Point3f(-8.02, 140.93, 20.02));
    modelPoints.push_back(cv::Point3f(80.74, 140.93, 20.02));

    m_modelPoints3d = cv::Mat(modelPoints);

    const cv::Scalar mean_point = cv::mean(cv::Mat(modelPoints));
    std::cout << "Mean point: " << mean_point << std::endl;
    m_modelPoints3d = m_modelPoints3d - mean_point;

    //assert(norm(mean(model_points_3d)) < 1e-05); //make sure is centered
    m_modelPoints3d = m_modelPoints3d + cv::Scalar(0, 0, 20.02);

    // std::cout << "model points " << model_points_3d << std::endl;
}

void GLWidget::initializeGL()
{
    glEnable(GL_CULL_FACE);
    glCullFace(GL_BACK);

    glShadeModel(GL_SMOOTH);

    glEnable(GL_DEPTH_TEST);
    glDepthFunc(GL_LEQUAL);

    glEnable(GL_BLEND);
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA);

    glEnable(GL_LIGHT0);
    glEnable(GL_NORMALIZE);
    glEnable(GL_COLOR_MATERIAL);
    glColorMaterial(GL_FRONT, GL_AMBIENT_AND_DIFFUSE);

    const GLfloat light_ambient[]  = { 0.0f, 0.0f, 0.0f, 1.0f };
    const GLfloat light_diffuse[]  = { 1.0f, 1.0f, 1.0f, 1.0f };
    const GLfloat light_specular[] = { 1.0f, 1.0f, 1.0f, 1.0f };
    const GLfloat light_position[] = { 0.0f, 0.0f, 1.0f, 0.0f };

    const GLfloat mat_ambient[]    = { 0.7f, 0.7f, 0.7f, 1.0f };
    const GLfloat mat_diffuse[]    = { 0.8f, 0.8f, 0.8f, 1.0f };
    const GLfloat mat_specular[]   = { 1.0f, 1.0f, 1.0f, 1.0f };
    const GLfloat high_shininess[] = { 100.0f };

    glLightfv(GL_LIGHT0, GL_AMBIENT,  light_ambient);
    glLightfv(GL_LIGHT0, GL_DIFFUSE,  light_diffuse);
    glLightfv(GL_LIGHT0, GL_SPECULAR, light_specular);
    glLightfv(GL_LIGHT0, GL_POSITION, light_position);

    glMaterialfv(GL_FRONT, GL_AMBIENT,   mat_ambient);
    glMaterialfv(GL_FRONT, GL_DIFFUSE,   mat_diffuse);
    glMaterialfv(GL_FRONT, GL_SPECULAR,  mat_specular);
    glMaterialfv(GL_FRONT, GL_SHININESS, high_shininess);

    glEnable(GL_LIGHTING);

    glMatrixMode(GL_MODELVIEW);
    glLoadIdentity();
}

void GLWidget::paintGL()
{
    // draw the image in the back
    int vPort[4];
    glGetIntegerv(GL_VIEWPORT, vPort);

    //glEnable2D();
    //drawOpenCVImageInGL(tex_l);
    //glTranslated(vPort[2]/2.0, 0.0, 0.0);
    //drawOpenCVImageInGL(tex_r);
    //glDisable2D();

    glClear(GL_DEPTH_BUFFER_BIT); // we want to draw stuff over the image

    // draw only on left part
    glViewport(0, 0, vPort[2]/2, vPort[3]);

    glPushMatrix();

        gluLookAt(0, 0, 0, 0, 0, 1, 0, -1, 0);

        // put the object in the right position in space
        //Vec3d tvv(tv[0], tv[1], tv[2]);
        glTranslated(m_tv[0], m_tv[1], m_tv[2]);

        // original matrix
        const GLdouble ogl_rotation_matrix[16] = {
            m_rot[0], m_rot[1], m_rot[2], 0,
            m_rot[3], m_rot[4], m_rot[5], 0,
            m_rot[6], m_rot[7], m_rot[8], 0,
            0,	      0,	    0,        1
        };

        /*
        const GLdouble ogl_rotation_matrix[16] = {
            rot[0], rot[3], rot[6], 0,
            rot[1], rot[4], rot[7], 0,
            rot[2], rot[5], rot[8], 0,
            0,	         0,	     0, 1
        };
        */
        glMultMatrixd(ogl_rotation_matrix);

        // draw the 3D head model
        glColor4f(1, 1, 1, 0.75);
        glmDraw(m_headObj, GLM_SMOOTH);

        glDisable(GL_DEPTH_TEST);
        glColor4f(0, 1, 0, 0.6);
        glBegin(GL_QUADS);
            for(int i = 0; i < 4; i++)
               glVertex3f(m_modelPoints3d.at<float>(i, 0),
                          m_modelPoints3d.at<float>(i, 1),
                          m_modelPoints3d.at<float>(i, 2));
        glEnd();
        glEnable(GL_DEPTH_TEST);

        //----------Axes
        glScaled(100, 100, 100);
        drawAxes();

    glPopMatrix();

    // restore to looking at complete viewport
    glViewport(0, 0, vPort[2], vPort[3]);

    // glutSwapBuffers();
}

void GLWidget::resizeGL(int width, int height)
{
    const float ar = float(width) / float(height);

    glViewport(0, 0, width, height);

    glMatrixMode(GL_PROJECTION);
    glLoadIdentity();
    //glFrustum(-ar, ar, -1.0, 1.0, 2.0, 100.0);
    gluPerspective(47, 1.0, 0.01, 1000.0);

    glMatrixMode(GL_MODELVIEW);
    glLoadIdentity();
}
