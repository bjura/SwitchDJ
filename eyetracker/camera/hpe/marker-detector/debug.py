'''
Created on 2010-07-01

@author: Macias
'''
import cv
from vectors import scale
from create_img import createImg
forbidden_lables = []
class dummy(object):
    index = 0
prov = dummy()
start_index = 0
windows = []
m_d = None
font = cv.InitFont(cv.CV_FONT_HERSHEY_COMPLEX_SMALL, 0.7, 0.7)

DEBUG = False

def show(image_list, name='temp_show', height=1, wait=500, width=0):
    '''
    Show images next to each other in seperate windows
    @param image_list: image or image list to display
    @param name: name prefix of windows
    @param height: vertical position= height*(image.height+50)
    @param wait: wait after display in ms
    '''
    if not DEBUG: return
#    if name<>'main':return
    print prov.index, start_index, name, forbidden_lables
    if (prov.index < start_index): return
    if name in forbidden_lables: return
    new_list = {}
    if isinstance(image_list, list):
        for i, img in enumerate(image_list):
            new_list["%s %d" % (name, i)] = img
    elif isinstance(image_list, dict):
        for k, v in image_list.iteritems():
            new_list[name + k] = v;
    else:
        new_list[name] = image_list

    last = width * (new_list.values()[0].width + 30)

    for win, image in new_list.iteritems():
        if image is None:
            continue
        if not win in windows:
            # cv.DestroyWindow(win)
            cv.NamedWindow(win)
            cv.MoveWindow(win, last , int(height * (image.height + 50)))
            windows.append(win)
        last += image.width + 30
        rect = cv.GetImageROI(image)
        cv.ResetImageROI(image)
        img = cv.CloneImage(image)
        cv.SetImageROI(image, rect)
        (x, y, wx, wy) = rect
        cv.Rectangle(img, (x - 2, y - 2),
                     (x + wx + 2, y + wy + 2), (255, 255, 0), 1)
        cv.ShowImage(win, img)
    k = cv.WaitKey(wait)
    if k == 32:
        cv.WaitKey(delay=0)
    elif k == 27:
        for win in new_list.iterkeys():
            cv.DestroyWindow(win)

def show_images():
        if not DEBUG: return
        images = ["img", "gray_img", "draw_img", "tmp_img", "bw_img", "canny_img"]
        x, y = m_d.size
        le = len(images) / 2
        for i, im in enumerate(images):
            cv.ShowImage(im, eval("m_d." + im))
            cv.MoveWindow(im, (x + 10) * (i % le), (y + 30) * (i / le))
        cv.WaitKey(1)


def pr(args=[], label='print'):
    if not DEBUG: return
    if prov.index < start_index:return
    if label in forbidden_lables: return
    str = label + ":"
    for a in args:
        str += repr(a) + " "
    print str

def start_at(provider, index):
    if not DEBUG: return
    global prov, start_index
    prov = provider
    start_index = index
def is_time():
    return prov.index == start_index
def db_break(name="break"):
    if prov.index >= start_index:
        pass
def Circle(img, center, radius, color):
    if not DEBUG: return
    cv.Circle(img, center, radius, color)

def PolyLine(img, polys, is_closed, color, text=None, scale_f=1):
    if not DEBUG: return
    if scale_f <> 1:
        polys[0] = map(lambda p:scale(p, scale_f), polys[0])
    polys[0] = [(int(p[0]), int(p[1])) for p in polys[0]]
    cv.PolyLine(img, polys, is_closed, color)
    if text is not None:
        polys = polys[0]
        x, y = reduce(lambda (x, y), (w, z):(x + w, y + z), polys, (0, 0))
        cv.PutText(img, text, (x / len(polys), y / len(polys)), font, (0, 255, 255))

def DrawContours(img, contour, external_color, hole_color, max_level):
    if not DEBUG: return
    cv.Zero(img)
    cv.DrawContours(img, contour, external_color, hole_color, max_level)
def get_hue_in_rgb(img):
    tmp = createImg(img)
    cv.Set(tmp, (255, 255, 255))
    coi = cv.GetImageCOI(img)
    cv.SetImageCOI(img, 1)
    cv.SetImageCOI(tmp, 1)
    cv.Copy(img, tmp)
    cv.SetImageCOI(tmp, 0)
    cv.SetImageCOI(img, coi)

    cv.CvtColor(tmp, tmp, cv.CV_HSV2BGR)
    return tmp


def print_array(array, label="print_array"):
    '''
    Prints an array
    @param array:
    '''
    if not DEBUG: return
    if prov.index < start_index: return
    if label in forbidden_lables: return
    print label
    (cols, rows) = cv.GetSize(array)
    for i in range(rows):
            s = ""
            for j in range(cols):
                s += " %7.3f" % cv.Get2D(array, i, j)[0]
            print s

