import cv2
import numpy as np
from PyQt5 import QtCore
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PIL import Image

from widgets.labels.Label import Label as lbl

import os

class PhotoDescriptionLabel(lbl):

    def __init__(self, label_name, label_description, color = 'grey', param_setup = True, zoom_feature = False, stretch = False):
        super().__init__(label_name, label_description)
        self.label_name = label_name
        self.zoom_feature = zoom_feature
        self.label_description = label_description
        self.bounding_boxes = []
        self.img_path = ''
        self.color = color
        self.setObjectName(self.label_name)
        self.setStyleSheet("border: 1px solid black;")

        if param_setup:
            self.param_setup()

        self.photo_label_layout = QVBoxLayout()
        self.photo_label_layout.setContentsMargins(0, 0, 0, 0)

        self.photo_label_layout.setSpacing(0)
        self.photo_label_layout.setStretch(0, 8)
        self.photo_label_layout.setStretch(1, 2)

        self.image_part = lbl(label_name, label_description, zoom_feature = zoom_feature)
        self.image_part.setStyleSheet("border: 3px solid " + 'black' + "; background-color: " + color + "; font-size: 18pt;")
        self.label_height = self.image_part.height()
        self.label_width = self.image_part.width()


        self.text_part = QLabel()
        self.text_part.setStyleSheet("border: 3px solid " + 'black' + "; background-color: " + color + "; font-size: 18pt;")
        self.text_part.setText(label_description)
        self.text_part.setAlignment(Qt.AlignCenter)
        self.text_part.setMaximumHeight(50)

        self.photo_label_layout.addWidget(self.image_part, stretch=8)
        if stretch == True:
            self.photo_label_layout.addStretch()
        self.photo_label_layout.addWidget(self.text_part, stretch=2)




        self.setLayout(self.photo_label_layout)





    def param_setup(self):

        self.setMinimumHeight(400)
        self.setMaximumHeight(400)
        self.setMaximumWidth(300)
        self.setMinimumWidth(300)




    def change_text_part_to_button(self, button_text, action_class_function):
        self.photo_label_layout.removeWidget(self.text_part)
        self.text_part = QPushButton()
        self.text_part.setObjectName(self.label_name)
        self.text_part.setText(button_text)
        self.text_part.clicked.connect(action_class_function)
        self.text_part.setStyleSheet("border: 3px solid " + 'black' + "; background-color: " + self.color + "; font-size: 18pt;")
        self.text_part.setMaximumHeight(50)
        self.text_part.setMinimumHeight(50)
        self.photo_label_layout.addWidget(self.text_part, stretch=2)
        self.update()

    def set_text_part_to_button(self, button):
        self.photo_label_layout.removeWidget(self.text_part)
        self.text_part = button
        self.photo_label_layout.addWidget(self.text_part, stretch=2)
        self.update()

    def update_parts(self):
        self.image_part.set_width(self.width())
        self.image_part.set_height(self.height() - self.text_part.height())


    def set_image_part(self, new_image_part):
        self.photo_label_layout.removeWidget(self.image_part)
        self.photo_label_layout.removeWidget(self.text_part)
        self.image_part.hide()
        self.image_part = new_image_part
        self.photo_label_layout.addWidget(self.image_part, stretch=8)
        self.photo_label_layout.addWidget(self.text_part, stretch=2)
        self.image_part.show()
        self.update()

    def set_img_from_np_array(self, img_np_array, updtate_parts = True):
        if updtate_parts:
            self.update_parts()
        self.image_part.set_label_img_from_np_array(img_np_array)
        self.set_width(self.image_part.newWidth)
        self.text_part.setFixedWidth(self.image_part.newWidth)
        self.image_part.setText('')
        self.update()

    def set_image_from_path(self, image_path, updtate_parts = True):
        if updtate_parts:
            self.update_parts()
        self.img_path = image_path
        self.image_part.set_image(image_path)
        self.set_width(self.image_part.newWidth)
        self.text_part.setFixedWidth(self.image_part.newWidth)
        self.image_part.setText('')
        self.update()

    def rotate_image(self, image, angle):
        (h, w) = image.shape[:2]
        center = (w // 2, h // 2)
        M = cv2.getRotationMatrix2D(center, angle, 1.0)
        rotated = cv2.warpAffine(image, M, (w, h))
        return np.asarray(rotated)

    # TODO: add this to the workstation
    def set_image_cropped(self, xmin, ymin, xmax, ymax, input_image, angle = 0):
        self.photo_label_layout.removeWidget(self.image_part)
        self.photo_label_layout.removeWidget(self.text_part)
        image = self.rotate_image(input_image[ymin:ymax, xmin:xmax], angle)
        self.set_img_from_np_array(image)
        self.photo_label_layout.addWidget(self.image_part, stretch=8)
        self.photo_label_layout.addWidget(self.text_part, stretch=2)


    def set_width(self, width):
        width = int(width)
        self.text_part.setMaximumWidth(width)
        self.text_part.setMinimumWidth(width)
        self.image_part.set_width(width)
        self.setMaximumWidth(width)
        self.setMinimumWidth(width)
        self.update()

    def set_height(self, height):
        height = int(height)
        self.setMaximumHeight(height)
        self.setMinimumHeight(height)
        self.update()

    def get_label(self):
        return self.image_part

    def set_label(self, label):
        self.image_part = label
        self.update()

    def get_top_margin(self):
        return (self.height() - self.newHeight - self.text_part.height()) * .5

    def get_height_ratio(self):
        return self.image_part.get_height_ratio()

    def change_text(self, text):
        self.text_part.setText(text)
        self.update()

    def get_width_ratio(self):
        return self.image_part.get_width_ratio()

    def add_bounding_box(self, minx, miny, maxx, maxy, color, text = None):
        self.image_part.add_bounding_box(minx, miny, maxx, maxy, color, text)

    def remove_bounding_box(self):
        self.image_part.remove_bounding_box()









