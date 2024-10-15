import cv2

from tabs.Split_tab import Split_tab as Split_Tab
import numpy as np


class DecorationsTab(Split_Tab):
    def detect_white_points(self, image):

        image = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
       
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

        # convert from binary img to 3 channel img
        img_mask = cv2.cvtColor(img_mask*255, cv2.COLOR_GRAY2RGB)
        self.set_img_and_mask(img_mask, img_orig)
        self.graph_points = []
        self.graph_points = self.detect_white_points(img_mask)
        self.central_widget.draw_points(self.graph_points)
        self.right_widget.draw_points(self.graph_points)
        # self.w3.setChecked(True)
        # self.w3_clicked()