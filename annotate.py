import os
import glob
import cv2
import cv2.cv as cv
import sys
import pickle

if len(sys.argv) == 1:
    sys.exit(0)
HOME_DIR_IMGS = sys.argv[1]
IMGS_PATH_IN_HOME_DIR = glob.glob(os.path.join(HOME_DIR_IMGS, '*.jpg'))

class annotate:

    def __init__(self):
        self.IMG_PATH = None
        self.PREV_POS = None
        self.rectangle_drawn = False
        self.COORDS = None
        self.run_dic = {}
        self.count = 0
        self.index = 0
        self.save_after = 10
        if os.path.isfile('annotations.pkl'):
            with open('annotations.pkl', 'rb') as handle:
                self.run_dic, self.index = pickle.load(handle)
                self.count = len(self.run_dic)
                print "### Previos Annotation Pickle File Loaded ###"
        self.prev_count = self.count

    def draw_window(self, POS):
        title = self.IMG_PATH  
        cv2.destroyAllWindows()
        img = cv2.imread(self.IMG_PATH)
        if not self.rectangle_drawn:
            if self.PREV_POS:
                cv2.rectangle(img, self.PREV_POS[::-1], POS[::-1], (0, 0, 255), thickness=1, lineType=8, shift=0)
                title += ' | ' + ','.join(list(map(str, self.PREV_POS[::-1]))) + ' - ' + ','.join(list(map(str, POS[::-1])))
                self.COORDS = [self.PREV_POS[::-1][:], POS[::-1][:]]
                self.PREV_POS = None
                self.rectangle_drawn = True
            elif POS and POS[0]-2 >= 0 and POS[0]+2 < img.shape[0] and POS[1]-2 >= 0 and POS[1]+2 < img.shape[1]:
                img[POS[0]-2 : POS[0]+2, POS[1]-2 : POS[1]+2] = [0, 0, 255]
                self.PREV_POS = POS[:]
        cv2.imshow(title, img)
        cv2.moveWindow(title, 100, 100)
        cv.SetMouseCallback(title, self.on_mouse, 0)

    def on_mouse(self, event, x, y, flags, params):
        if event == cv.CV_EVENT_LBUTTONUP:
            self.draw_window((y, x))
    
    def start(self, ALL_IMAGES_PATH):
        index = self.index
        max_index = index
        coord_pos = None
        count_flag = -1
        while True:
            try:
                max_index = max(index, max_index)
                img_path = ALL_IMAGES_PATH[index]
                if img_path in self.run_dic:
                    self.rectangle_drawn = False
                    self.PREV_POS = self.run_dic[ALL_IMAGES_PATH[index]][0][::-1][:]
                    coord_pos = self.run_dic[ALL_IMAGES_PATH[index]][1][::-1][:]
                self.IMG_PATH = img_path
                # print "Loading Image", self.IMG_PATH
                self.draw_window(coord_pos)
                key = None
                while True:
                    key = cv2.waitKey()
                    if key in [ord('q'), ord('n'), ord('p'), ord('d')]:
                        break
                    elif key == ord('r'):
                        self.PREV_POS = None
                        self.draw_window(None)
                        self.rectangle_drawn = False
                if self.COORDS:
                    if self.IMG_PATH not in self.run_dic: self.count += 1
                    self.run_dic[self.IMG_PATH] = self.COORDS
                    # print "Coordinates saved", self.IMG_PATH, self.COORDS
                if key == ord('q'):
                    if self.prev_count != self.count:
                        with open('annotations.pkl', 'wb') as handle:
                            pickle.dump([self.run_dic, max_index], handle, protocol=pickle.HIGHEST_PROTOCOL)
                        print "### Records Saved Addition/Deletion", self.count - self.prev_count, "###"
                    break
                index += 1
                if key == ord('p'):
                    index -= 2
                if key == ord('d'):
                    index -= 1
                    self.count -= 1
                    if ALL_IMAGES_PATH[index] in self.run_dic:
                        del self.run_dic[ALL_IMAGES_PATH[index]]
                    index += 1
                    print "Coordinates deleted", self.IMG_PATH                    
                if index == len(ALL_IMAGES_PATH):
                    print "### All Images Annotated ###"
                    break
                coord_pos = None
                self.PREV_POS = None
                self.rectangle_drawn = False
                self.COORDS = None
                if self.count and not self.count%self.save_after and count_flag!=self.count:
                    with open('annotations.pkl', 'wb') as handle:
                        pickle.dump([self.run_dic, max_index], handle, protocol=pickle.HIGHEST_PROTOCOL)
                    print "### Records Saved Count", self.count, "###"
                    count_flag = self.count
            except IOError:
                index += 1
                print "Input Output Error Occured"
                if index == len(ALL_IMAGES_PATH):
                    print "### All Images Annotated ###"
                    break

ann = annotate()
ann.start(IMGS_PATH_IN_HOME_DIR)
