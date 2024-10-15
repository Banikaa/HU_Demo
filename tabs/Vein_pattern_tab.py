import os, shutil

from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *

import cv2
import numpy as np


from tabs.Split_tab import Split_tab as Split_Tab

# TODO: implement the changing of label sizes when resizing the window after setting image
# TODO: debug the finger tab label resizing issues




# Class for the Vain Pattern Tab
# This class is responsible for the layout and functionality of the Vain Pattern Tab
# for the vain pattern segmentation model output
class VainPatternTab(Split_Tab):

    def detect_white_points(self, image):
        # image = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
        _, binary = cv2.threshold(image.astype(np.uint8), 2, 255, cv2.THRESH_BINARY)
        white_points_indices = np.column_stack(np.where(binary == 255))
        white_points = [(point[1], point[0]) for point in white_points_indices]
        return white_points


    def draw_points(self):
        self.show_infrared()

    def set_img_to_labels(self, img_mask, img_orig, img_mask_infrared=None):

        self.set_img_and_mask(cv2.cvtColor(img_mask, cv2.COLOR_GRAY2RGB), img_orig)
        self.graph_points = []
        self.graph_points_infrared = []

        self.graph_points = self.detect_white_points(img_mask)
        if img_mask_infrared is not None:
            self.graph_points_infrared = self.detect_white_points(img_mask_infrared)

        if img_mask.shape == img_orig.shape:
            self.graph_points_for_original = self.graph_points
            self.graph_points_for_original_infrared = self.graph_points_infrared
        else:
            print('resizing')
            width_ratio = img_orig.shape[1] / img_mask.shape[1]
            height_ratio = img_orig.shape[0] / img_mask.shape[0]
            self.graph_points_for_original = []
            self.graph_points_for_original_infrared = []
            for point in self.graph_points:
                self.graph_points_for_original.append([int(point[0] * width_ratio), int(point[1] * height_ratio)])
            for point in self.graph_points_infrared:
                self.graph_points_for_original_infrared.append([int(point[0] * width_ratio), int(point[1] * height_ratio)])

        # keep only the first hapf of the points
        # self.graph_points_for_original = self.graph_points_for_original[:len(self.graph_points_for_original)//2]
        # self.graph_points = self.graph_points[:len(self.graph_points)//2]
        
        self.central_widget.draw_graph({'rgb': self.graph_points, 'infrared': self.graph_points_infrared})
        self.right_widget.draw_graph({'rgb': self.graph_points_for_original, 'infrared': self.graph_points_for_original_infrared})
        self.w3.setChecked(True)
        self.w3_clicked()


    def show_infrared(self):
        if self.infrared_btn.isChecked():
            self.right_widget.delete_points()
            self.right_widget.draw_graph({'rgb': self.graph_points_for_original, 'infrared': self.graph_points_for_original_infrared})
            self.central_widget.delete_points()
            self.central_widget.draw_graph({'rgb': self.graph_points, 'infrared': self.graph_points_infrared})
        else:
            self.right_widget.delete_points()
            self.right_widget.draw_graph({'rgb': self.graph_points_for_original})
            self.central_widget.delete_points()
            self.central_widget.draw_graph({'rgb': self.graph_points})



