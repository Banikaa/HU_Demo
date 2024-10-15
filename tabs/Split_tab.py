import os, shutil

from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *

import cv2
import numpy as np

from widgets.labels import PhotoDescriptionLabel as photo_descript_lbl
from widgets.labels import Label as lbl
from widgets.buttons import CheckBox as check_box
from widgets.buttons import Button as btn


# TODO: meeting:


# TODO: implement the changing of label sizes when resizing the window after setting image
# TODO: debug the finger tab label resizing issues

# TODO: look into finding ways to activate the tabs from diferent models



class Color(QLabel):
    def __init__(self, color):
        super(Color, self).__init__()
        self.setAutoFillBackground(True)
        palette = self.palette()
        palette.setColor(QPalette.Window, QColor(color))
        self.setPalette(palette)

# Class for the Creating a TAB with split screen view
# This class is responsible for the layout and functionality of the Vain Pattern Tab
# for the vain pattern segmentation model output
#
#     WHEN EXTENDING THIS, NEED TO ADD THE
    #     "detect_white_points"
    #     "set_img_to_labels"
    #     "draw_points"
    #     FUNCTIONS
# def detect_white_points(self, img_path):
#     specific for each class needs
#
class Split_tab(QWidget):
    def __init__(self, main_window, tab_name, tab_description):
        super().__init__()
        self.tab_name = tab_name
        self.tab_description = tab_description
        self.tab_color = 'grey'
        self.is_label_hidden = False
        self.graph_points = []
        self.main_window = main_window
        self.photo_viewer_label = None
        self.photo_ready = False
        self.central_img_np_array = []
        self.right_img_np_array = []

        self.initUI()

    # setting up the layout and widgets for the vain pattern tab
    def initUI(self):
        self.screen_widget = QWidget()
        self.screen_widget_layout = QVBoxLayout()
        self.screen_widget_layout.setContentsMargins(0, 0, 0, 0)
        self.screen_widget_layout.setSpacing(0)

        self.model_output_widget_layout = QHBoxLayout()

        # central widget setup
        self.central_photo_label = photo_descript_lbl.PhotoDescriptionLabel('central_photo_label', 'Photo', 'grey', False, True)
        self.central_widget = self.central_photo_label.get_label()
        self.central_photo_label.setScaledContents(True)
        self.central_photo_label.change_text_part_to_button('Photo View', self.focus_tab)
        self.model_output_widget_layout.addWidget(self.central_photo_label, 1)
        self.central_widget.set_parent(self)

        # right widget setup
        self.right_photo_label = photo_descript_lbl.PhotoDescriptionLabel('right_photo_label', 'Graph','grey', False, True)
        self.right_widget = self.right_photo_label.get_label()
        self.right_photo_label.change_text_part_to_button('Graph View', self.focus_tab)
        self.right_photo_label.setStyleSheet("border: 1px solid black;")
        self.model_output_widget_layout.addWidget(self.right_photo_label, 1)
        self.right_widget.set_parent(self)

        # setting up the layout of the model output tab for vain pattern segmentation
        self.screen_widget_layout.addWidget(self.tool_bar(), 1)
        self.screen_widget_layout.addLayout(self.model_output_widget_layout, 10)
        self.screen_widget.setLayout(self.screen_widget_layout)

    # called in main
    # sets the photo viewer label to the given label
    # @param view_label: string
    def set_photo_labels(self, view_label):
        self.draw_btn.setChecked(True)
        self.w1.setChecked(True)

        self.set_photo_viewer_label(view_label)
        img_fname = view_label.get_img()
        if img_fname == '':
            return
        self.photo_ready = True
        self.img_path = img_fname
        self.set_img_to_labels(img_fname)

    # returns an instance of the current tab
    def get_tab(self):
        return self.screen_widget

    # sets the photo viewer label variable to the given label
    # @param photo_viewer_label: string
    def set_photo_viewer_label(self, photo_viewer_label):
        self.photo_viewer_label = photo_viewer_label

    # getter for the photo viewer label
    def get_photo_viewer_label(self):
        return self.photo_viewer_label



    def sync_zoom(self, zoom_factor, delta_x, delta_y):
        self.right_widget.sync_zoom(zoom_factor)
        self.central_widget.sync_zoom(zoom_factor)
        self.right_widget.set_delta_pixmap(delta_x, delta_y)
        self.central_widget.set_delta_pixmap(delta_x, delta_y)

    # focuses on the correct viewer label when pressing the buttons
    # responsible for the switching between the central and right viewer labels
    # and changing the dimensions of the labels and buttons
    def focus_tab(self):
        # print('screen width: {w}'.format(w=self.screen_widget.width()))
        # print('central width: {w}'.format(w=self.central_widget.width()))
        # print('right width: {w}'.format(w=self.right_widget.width()))
        # print('--------------------------------------')

        sender_button = self.sender().objectName()
        if sender_button == 'central_photo_label':      # switch to central viewer label and back
            if not self.is_label_hidden:
                self.model_output_widget_layout.removeWidget(self.right_photo_label)
                self.right_photo_label.hide()
                self.central_photo_label.set_width(self.screen_widget.width())
                self.central_widget.set_width(self.screen_widget.width())
                if self.photo_ready:
                    self.central_photo_label.set_img_from_np_array(self.central_img_np_array)
                self.is_label_hidden = True
            else:
                self.model_output_widget_layout.removeWidget(self.right_photo_label)
                self.model_output_widget_layout.removeWidget(self.central_photo_label)
                self.set_label_half_screen_width()
                self.model_output_widget_layout.addWidget(self.central_photo_label, 1)
                self.model_output_widget_layout.addWidget(self.right_photo_label, 1)
                self.right_photo_label.show()
                self.is_label_hidden = False
                if self.photo_ready:
                    self.set_label_half_screen_width()
                    self.right_photo_label.set_img_from_np_array(self.right_img_np_array, False)
                    self.central_photo_label.set_img_from_np_array(self.central_img_np_array, False)


        elif sender_button == 'right_photo_label':      # switch to right viewer label and back
            if not self.is_label_hidden:
                self.model_output_widget_layout.removeWidget(self.central_photo_label)
                self.central_photo_label.hide()
                self.right_photo_label.set_width(self.screen_widget.width())
                self.right_widget.set_width(self.screen_widget.width())
                if self.photo_ready:
                    self.right_photo_label.set_img_from_np_array(self.right_img_np_array)
                self.is_label_hidden = True
            else:
                self.model_output_widget_layout.removeWidget(self.right_photo_label)
                self.model_output_widget_layout.removeWidget(self.central_photo_label)
                self.set_label_half_screen_width()
                self.model_output_widget_layout.addWidget(self.right_photo_label, 1)
                self.model_output_widget_layout.addWidget(self.central_photo_label, 1)
                self.central_photo_label.show()
                self.is_label_hidden = False
                self.set_label_half_screen_width()
                if self.photo_ready:
                    self.set_label_half_screen_width()
                    self.central_photo_label.set_img_from_np_array(self.central_img_np_array, False)
                    self.right_photo_label.set_img_from_np_array(self.right_img_np_array, False)

        self.central_photo_label.update()
        self.right_photo_label.update()
        self.draw_points()


    # sets the width of the labels to half of the screen width
    def set_label_half_screen_width(self):
        screen_width = self.main_window.model_output.width()-100
        screen_height = self.main_window.model_output.height()-20
        self.central_photo_label.set_width(int(screen_width / 2))
        self.right_photo_label.set_width(int(screen_width / 2))
        self.central_widget.set_width(int(screen_width / 2))
        self.central_widget.set_height(int(screen_height))
        self.central_widget.set_height(int(screen_height))
        self.right_widget.set_width(int(screen_width / 2))
        self.update()

    def set_label_screen_width(self):
        screen_width = self.screen_widget.width()-50
        self.central_photo_label.set_width(int(screen_width))
        self.right_photo_label.set_width(int(screen_width))
        self.central_widget.set_width(int(screen_width))
        self.right_widget.set_width(int(screen_width))


    # sets the image to the labels
    # called after the image is selected
    # @param img_fname: string

    # get the graph iamge associated with the output image from the model
    # and detect the white points for vectorisation and displaying on the image
    # @param img_path: string
    # TODO: change this so it oly sets the image to the labels
    def set_img_and_mask(self, img_mask, img_orig):
        self.photo_ready = True
        # self.model_output_widget_layout.removeWidget(self.central_photo_label)
        # self.model_output_widget_layout.removeWidget(self.right_photo_label)
        # self.set_label_half_screen_width()
        # self.model_output_widget_layout.addWidget(self.central_photo_label, 1)
        # self.model_output_widget_layout.addWidget(self.right_photo_label, 1)
    
        self.right_photo_label.set_width(int(self.main_window.model_output.width()/2-50))
        self.central_photo_label.set_width(int(self.main_window.model_output.width()/2-50))
        self.right_widget.set_width(int(self.main_window.model_output.width()/2-50))
        self.central_widget.set_width(int(self.main_window.model_output.width()/2-50))
        
        self.central_img_np_array = img_mask
        self.right_img_np_array = img_orig
        self.right_widget.set_label_img_from_np_array(img_orig)
        self.central_widget.set_label_img_from_np_array(img_mask)

        self.right_photo_label.set_width(self.right_widget.newWidth)
        self.central_photo_label.set_width(self.central_widget.newWidth)
        self.update()

    def reset(self):
        self.photo_ready = False
        self.central_img_np_array = []
        self.right_img_np_array = []
        self.central_widget.setText('')
        self.right_widget.setText('')
        self.central_widget.set_image('')
        self.right_widget.set_image('') 
        self.set_label_half_screen_width  


    def delete_points(self):
        self.central_widget.delete_points()
        self.right_widget.delete_points()



#---------------------------------------------------------------
#---------------------TOOL BAR SETUP---------------------------
#---------------------------------------------------------------
    def tool_bar(self):
        tool_bar = QToolBar()
        tool_bar.setMovable(False)

        self.green_btn = check_box.CheckBox('green_btn', 'Green', 'green')
        self.green_btn.clicked.connect(self.green_points)
        self.white_btn = check_box.CheckBox('white_btn', 'White', 'white')
        self.white_btn.clicked.connect(self.white_points)
        self.w1 = check_box.CheckBox('w1', 'w 1px', 'w1')
        self.w1.clicked.connect(self.w1_clicked)
        self.w2 = check_box.CheckBox('w2', 'w 2px', 'w2')
        self.w2.clicked.connect(self.w2_clicked)
        self.w3 = check_box.CheckBox('w3', 'w 3px', 'w3')
        self.w3.clicked.connect(self.w3_clicked)

        if self.tab_name == 'Vein Pattern':
            self.infrared_btn = check_box.CheckBox('infrared_btn', 'Infrared', 'infrared')
            self.infrared_btn.clicked.connect(self.show_infrared)
            tool_bar.addWidget(self.infrared_btn)
            self.infrared_btn.setChecked(True)

        self.zoom_sync_btn = check_box.CheckBox('zoom_sync_btn', 'Sync Zoom', 'zoom_sync')
        self.zoom_sync_btn.clicked.connect(self.enable_sync)

        self.draw_btn = check_box.CheckBox('draw_btn', 'Draw', 'draw')
        self.draw_btn.clicked.connect(self.draw_btn_clicked)
        self.draw_btn.setChecked(True)

        self.reset_zoom_btn = check_box.CheckBox("reset_zoom", 'Reset Zoom', 'Reset')
        self.reset_zoom_btn.clicked.connect(self.reset_zoom)

        tool_bar.addWidget(self.green_btn)
        tool_bar.addWidget(self.white_btn)
        tool_bar.addWidget(self.draw_btn)
        tool_bar.addWidget(self.w1)
        tool_bar.addWidget(self.w2)
        tool_bar.addWidget(self.w3)
        tool_bar.addWidget(self.zoom_sync_btn)
        tool_bar.addWidget(self.reset_zoom_btn)

        return tool_bar

    def draw_btn_clicked(self):
        if self.draw_btn.isChecked():
            self.draw_points()
        else:
            self.green_btn.setChecked(False)
            self.white_btn.setChecked(False)
            self.delete_points()

    def w1_clicked(self):
        self.w1.setChecked(True)
        self.w2.setChecked(False)
        self.w3.setChecked(False)
        self.central_widget.set_pen_point_width(1)
        self.right_widget.set_pen_point_width(1)

    def w2_clicked(self):
        self.w2.setChecked(True)
        self.w1.setChecked(False)
        self.w3.setChecked(False)
        self.central_widget.set_pen_point_width(2)
        self.right_widget.set_pen_point_width(2)

    def w3_clicked(self):
        self.w3.setChecked(True)
        self.w1.setChecked(False)
        self.w2.setChecked(False)
        self.central_widget.set_pen_point_width(3)
        self.right_widget.set_pen_point_width(3)

    def white_points(self):
        self.green_btn.setChecked(False)
        self.draw_btn.setChecked(True)
        self.draw_btn_clicked()
        self.central_widget.set_point_color('white')
        self.right_widget.set_point_color('white')

    def green_points(self):
        self.white_btn.setChecked(False)
        self.draw_btn.setChecked(True)
        self.draw_btn_clicked()
        self.central_widget.set_point_color('green')
        self.right_widget.set_point_color('green')

    def enable_sync(self):
        if self.zoom_sync_btn.isChecked():
            self.right_widget.set_sync_bool(True)
            self.central_widget.set_sync_bool(True)
        else:
            self.right_widget.set_sync_bool(False)
            self.central_widget.set_sync_bool(False)


    def reset_zoom(self):
        self.reset_zoom_btn.setChecked(False)
        self.right_widget.sync_zoom(1)
        self.central_widget.sync_zoom(1)
        self.right_widget.set_delta_pixmap(0, 0)
        self.central_widget.set_delta_pixmap(0, 0)


#---------------------------------------------------------------
#---------------------MENU BAR SETUP----------------------------
#---------------------------------------------------------------
    def save_img(self, directory):
        print('not yet')

    def show_legend(self):
        print('not yet')

    def hide_legend(self):
        print('not yet')


    def delete_labels(self):
        pass