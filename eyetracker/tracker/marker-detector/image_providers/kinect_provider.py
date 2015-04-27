'''
Created on 24-03-2011

@author: Macias
'''
import kinect
from kinect import Kinect,CONFIG_XML,Transform
from image_providers import ImageProvider
from utils import createImg
import cv
from os.path import join,dirname,abspath
from gof.singleton import Singleton
from image_providers.image_input_manager import ImageInputManager
from image_providers.image_provider import ImageProviderType
class KinectProvider(Singleton,ImageProvider):
    def init(self,p_image_index=0,filename=CONFIG_XML,*args,**kwargs):
        self._dev=Kinect(filename)
        ImageProvider.__init__(self,*args,**kwargs)
        self.main_image=p_image_index;
        self.fga_image=None
        self.white_image=None
    def __getattr__(self,key):
        return getattr(self._dev, key)
    def _update_image(self):        
        self._dev.update()        
        if self.main_image==Kinect.DEPTH:
            return self.get_depth_image()
        elif self.main_image==Kinect.RGB:
            return self.get_rgb_image()
        elif self.main_image==Kinect.USER:
            return self.get_user_image()
        elif self.main_image==Kinect.FG:
            return self.get_foreground_image()
        elif self.main_image==Kinect.IR:
            return self.get_ir_image()
        else:
            return self.get_foreground_alpha_image()

    def get_foreground_alpha_image(self):
#        cv.ShowImage("user", self.get_normalized_depth_image())           
        rgb_img=self.get_rgb_image()        
        user_img=self.get_user_image()        
        users=self.get_user_coms()
        min=-1;
        for i,u in enumerate(users):
            if u[3]>0 and (min==-1 or u[3]<users[min][3]):
                min=i

        min=users[min][0] if len(users)>0 else 0
#        cv.Not(user_img,user_img)
#        cv.Threshold(user_img, user_img, 254, 255, cv.CV_THRESH_TOZERO_INV)
#        _,max,_,_=cv.MinMaxLoc(user_img)
        cv.CmpS(user_img, min, user_img, cv.CV_CMP_EQ)                
        if not self.fga_image:
            self.fga_image=createImg(rgb_img,c=4)
            self.white_image=createImg(user_img,c=1)
            cv.Set(self.white_image,254)
            self.tmp_img=createImg(rgb_img,c=4)
        cv.MixChannels([rgb_img,self.white_image], [self.tmp_img], [(0,0),(1,1),(2,2),(3,3)])
        cv.Zero(self.fga_image)
        if self.main_image==-1:
            cv.Copy(self.tmp_img, self.fga_image,user_img)
        else:
            cv.Copy(self.tmp_img,self.fga_image)
            cv.SetImageCOI(self.fga_image, 4)
            tmp=createImg(user_img,c=1,d=8)
            cv.Copy(self.white_image,tmp)
            cv.Copy(user_img, tmp,user_img)
            cv.Copy(tmp, self.fga_image)
            cv.SetImageCOI(self.fga_image, 0)
        return self.fga_image
    
    def __repr__(self):
        return "Kinect main_image: nr %d"%self.main_image
    
    def get_type(self):
        return ImageProviderType.KINECT

if __name__=='__main__':
#    kin =Kinect('../kinect/resources/SkeletonRec.oni')
#    kin.update
    kin=KinectProvider(Kinect.IR,'../kinect/resources/SamplesConfig1.xml')
#    kin.set_transform(1)
    img = kin.next()
    print img
#    img=kin.get_rgb_image()
    ir_img=createImg(img, d=8)
    while img and cv.WaitKey(1)!=27:
#        cv.Threshold(img, img, 0, 255, cv.CV_THRESH_BINARY)
        min,max,_,_=cv.MinMaxLoc(img)
        cv.CvtScale(img, ir_img,256.0/max,-min)
        cv.ShowImage("temp", ir_img)
#        kin.update()
        img=kin.next()
        print img
