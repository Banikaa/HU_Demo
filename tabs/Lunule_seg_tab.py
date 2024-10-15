import os, shutil

from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *

import cv2
import numpy as np
from PIL import Image

from tabs.Split_tab import Split_tab as Split_Tab
from widgets.labels import PhotoDescriptionLabel as photo_descript_lbl



# TODO: implement the changing of label sizes when resizing the window after setting image
# TODO: debug the finger tab label resizing issues



# Class for the Vain Pattern Tab
# This class is responsible for the layout and functionality of the Vain Pattern Tab
# for the vain pattern segmentation model output

class LunuleSegTab(QWidget):

    def __init__(self, main_window, tab_name, tab_description):
        super().__init__()
        self.tab_name = tab_name
        self.tab_description = tab_description
        self.tab_color = 'grey'
        self.main_window = main_window
        self.finger_coord = {}


        self.screen_widget = QTabWidget()
        finger_1 = LunuleSegWidget(self.main_window, 'Finger 1', 'Finger 1')
        finger_2 = LunuleSegWidget(self.main_window, 'Finger 2', 'Finger 2')
        finger_3 = LunuleSegWidget(self.main_window, 'Finger 3', 'Finger 3')
        finger_4 = LunuleSegWidget(self.main_window, 'Finger 4', 'Finger 4')
        finger_5 = LunuleSegWidget(self.main_window, 'Finger 5', 'Finger 5')

        self.finger_tabs = [finger_1, finger_2, finger_3, finger_4, finger_5]

        finger_1_tab = finger_1.get_tab()
        finger_2_tab = finger_2.get_tab()
        finger_3_tab = finger_3.get_tab()
        finger_4_tab = finger_4.get_tab()
        finger_5_tab = finger_5.get_tab()

        self.screen_widget.addTab(finger_1_tab, 'Finger 1')
        self.screen_widget.addTab(finger_2_tab, 'Finger 2')
        self.screen_widget.addTab(finger_3_tab, 'Finger 3')
        self.screen_widget.addTab(finger_4_tab, 'Finger 4')
        self.screen_widget.addTab(finger_5_tab, 'Finger 5')
        self.tab_changed()
        self.update()
        self.screen_widget.currentChanged.connect(self.tab_changed)

    def reset(self):
        for finger in self.finger_tabs:
            finger.delete_points()
            finger.set_img_and_mask(np.zeros((100,100,3)), np.zeros((100,100,3)))

    def tab_changed(self):
        if self.finger_coord not in [{}, {1:None, 2:None, 3:None, 4: None, 5: None}]:
            finger_num = self.screen_widget.currentIndex()
            finger_num += 1
            if self.finger_coord[finger_num] is not None:
                self.main_window.lunule_label.remove_bounding_box()
                ratio = self.main_window.lunule_label.ratio
                self.main_window.lunule_label.add_bounding_box(self.finger_coord[finger_num][0] * ratio,
                                                            self.finger_coord[finger_num][1] * ratio,
                                                            self.finger_coord[finger_num][2] * ratio,
                                                            self.finger_coord[finger_num][3] * ratio,
                                                            'red',
                                                            str("F" + str(finger_num)))
            self.main_window.lunule_label.update()

    def get_lunule_index(self):
        return self.screen_widget.currentIndex() + 1


    # TODO add this
    def input_lunule_dict(self, lunule_mask, finger_img, finger_coord):
        self.finger_coord = finger_coord
        self.main_window.lunule_label.remove_bounding_box()
        for i in range(1,6):
            if lunule_mask[i] is not None:
                self.finger_tabs[i-1].setEnabled(True)
                self.finger_tabs[i-1].set_img_to_labels(lunule_mask[i], finger_img[i])
            else:
                self.finger_tabs[i-1].setEnabled(False)
                self.finger_tabs[i-1].set_img_and_mask(np.zeros((100,100,3)), np.zeros((100,100,3)))
                self.finger_tabs[i-1].delete_points()

    def set_single_lunle(self, lunule_mask, finger_img, finger_num):
        self.main_window.lunule_label.remove_bounding_box()
        ratio = self.main_window.lunule_label.ratio
        # self.main_window.lunule_label.add_bounding_box(self.finger_coord[finger_num][0] * ratio,
        #                                                self.finger_coord[finger_num][1] * ratio,
        #                                                self.finger_coord[finger_num][2] * ratio,
        #                                                self.finger_coord[finger_num][3] * ratio,
        #                                                'red',
        #                                                str("F" + str(finger_num)))
        # self.main_window.lunule_label.update()
        self.finger_tabs[finger_num-1].setEnabled(True)
        self.finger_tabs[finger_num-1].set_img_to_labels(lunule_mask, finger_img)





    def get_tab(self):
        return self.screen_widget
    

    def reset(self):
        for finger in self.finger_tabs:
            finger.delete_points()


class LunuleSegWidget(Split_Tab):

    def detect_white_points(self, image):
        # image = cv2.cvtColor(image.astype(np.uint8), cv2.COLOR_BGR2GRAY)
        border_points = []
        _, binary = cv2.threshold(image, 2, 255, cv2.THRESH_BINARY)
        contours, _ = cv2.findContours(binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
        for contour in contours:
            border_points.append(contour.squeeze())
        return border_points


    def draw_points(self):
        self.central_widget.draw_points(self.graph_points)
        self.right_widget.draw_points(self.graph_points)


    def set_img_to_labels(self, img_mask, img_orig):
        mask_to_rgb = np.stack((img_mask,) * 3, axis = -1)
        self.set_img_and_mask(mask_to_rgb, img_orig)
        self.graph_points = []
        self.graph_points = self.detect_white_points(img_mask)
        self.central_widget.draw_points(self.graph_points)
        self.right_widget.draw_points(self.graph_points)
        # self.w3.setChecked(True)
        # self.w3_clicked()

