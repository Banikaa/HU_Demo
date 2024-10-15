import os, shutil, time

from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *


from widgets.labels import PhotoDescriptionLabel as photo_descript_lbl
from widgets.labels import Label as lbl
from widgets.buttons import CheckBox as check_box



class FlkTab(QLabel):

    def __init__(self, main_window):

        super(FlkTab, self).__init__()
        self.setObjectName('flk_tab')
        self.photo_viewer_label = None
        self.photo_ready = False
        self.screen_widget = QWidget()
        self.main_window = main_window
        self.img_np_array = None
        self.model_output = None

        self.hand_side = 'left'
        self.hand_position = 'dorsal'

        # setting up the main tab layout
        screen_widget_layout = QVBoxLayout()
        screen_widget_layout.setContentsMargins(0, 0, 0, 0)
        screen_widget_layout.setSpacing(0)

        self.label_height = 400
        self.label_width = 300

        screen_widget_layout.setStretch(0, 1)
        screen_widget_layout.setStretch(1, 9)

        screen_widget_layout.addWidget(self.tool_bar(), stretch=1)

        image_grid = QWidget()
        self.grid_layout = QGridLayout(self)

        scroll_area = QScrollArea(self)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scroll_area.setWidgetResizable(True)

        self.set_initial_state_labels()

        image_grid.setLayout(self.grid_layout)
        scroll_area.setWidget(image_grid)
        screen_widget_layout.addWidget(scroll_area, stretch=9)
        self.screen_widget.setLayout(screen_widget_layout)

    def set_photo_ready(self, photo_ready):
        self.photo_ready = photo_ready


    # setting up the labels in the tab that will contain each feature subimage after localization
    def set_initial_state_labels(self):
        self.finger_1 = photo_descript_lbl.PhotoDescriptionLabel(
            'finger_1', 'Finger 1', 'red', False, stretch=True)
        self.finger_2 = photo_descript_lbl.PhotoDescriptionLabel(
            'finger_2', 'Finger 2', 'red', True, stretch=True)
        self.finger_3 = photo_descript_lbl.PhotoDescriptionLabel(
            'finger_3', 'Finger 3', 'red', True, stretch=True)
        self.finger_4 = photo_descript_lbl.PhotoDescriptionLabel(
            'finger_4', 'Finger 4', 'red', True, stretch=True)
        self.finger_5 = photo_descript_lbl.PhotoDescriptionLabel(
            'finger_5', 'Finger 5', 'red', True, stretch=True)

        self.knuckle_m_1 = photo_descript_lbl.PhotoDescriptionLabel(
            'knuckle_m_1', 'DIP 1', 'green', True, stretch=True)
        self.knuckle_m_2 = photo_descript_lbl.PhotoDescriptionLabel(
            'knuckle_m_2', 'DIP 2', 'green', True, stretch=True)
        self.knuckle_m_3 = photo_descript_lbl.PhotoDescriptionLabel(
            'knuckle_m_3', 'DIP 3' , 'green', True, stretch=True)
        self.knuckle_m_4 = photo_descript_lbl.PhotoDescriptionLabel(
            'knuckle_m_4', 'DIP 4' , 'green', True, stretch=True)
        self.knuckle_m_5 = photo_descript_lbl.PhotoDescriptionLabel(
            'knuckle_m_5', 'DIP 5' , 'green', True, stretch=True)

        self.knuckle_M_5 = photo_descript_lbl.PhotoDescriptionLabel(
            'knuckle_M_5', 'PIP 5', '#40E0D0' , True, stretch=True)
        self.knuckle_M_4 = photo_descript_lbl.PhotoDescriptionLabel(
            'knuckle_M_4', 'PIP 4', '#40E0D0' , True, stretch=True)
        self.knuckle_M_3 = photo_descript_lbl.PhotoDescriptionLabel(
            'knuckle_M_3', 'PIP 3', '#40E0D0', True , stretch=True)
        self.knuckle_M_2 = photo_descript_lbl.PhotoDescriptionLabel(
            'knuckle_M_2', 'PIP 2', '#40E0D0' , True, stretch=True)
        self.knuckle_M_1 = photo_descript_lbl.PhotoDescriptionLabel(
            'knuckle_M_1', 'PIP 1', '#40E0D0' , True, stretch=True)

        self.knuckle_b_1 = photo_descript_lbl.PhotoDescriptionLabel(
            'knuckle_b_1', 'MCP 1', 'purple', True, stretch=True)
        self.knuckle_b_2 = photo_descript_lbl.PhotoDescriptionLabel(
            'knuckle_b_2', 'MCP 2', 'purple', True, stretch=True)
        self.knuckle_b_3 = photo_descript_lbl.PhotoDescriptionLabel(
            'knuckle_b_3', 'MCP 3', 'purple', True, stretch=True)
        self.knuckle_b_4 = photo_descript_lbl.PhotoDescriptionLabel(
            'knuckle_b_4', 'MCP 4', 'purple', True, stretch=True)
        self.knuckle_b_5 = photo_descript_lbl.PhotoDescriptionLabel(
            'knuckle_b_5', 'MCP 5', 'purple', True, stretch=True)

        self.fingers = [self.finger_1, self.finger_2, self.finger_3, self.finger_4, self.finger_5]
        self.knuckles_m = [self.knuckle_m_1, self.knuckle_m_2, self.knuckle_m_3, self.knuckle_m_4, self.knuckle_m_5]
        self.knuckles_M = [self.knuckle_M_1, self.knuckle_M_2, self.knuckle_M_3, self.knuckle_M_4, self.knuckle_M_5]
        self.knuckles_b = [self.knuckle_b_1, self.knuckle_b_2, self.knuckle_b_3, self.knuckle_b_4, self.knuckle_b_5]

        height = self.label_height
        width = self.label_width
        for label in self.fingers:
            label.set_height(height)
            label.set_width(width)
        for label in self.knuckles_m:
            label.set_height(height)
            label.set_width(width)
        for label in self.knuckles_M:
            label.set_height(height)
            label.set_width(width)
        for label in self.knuckles_b:
            label.set_height(height)
            label.set_width(width)

    # set the viever label variable to the current photo shown
    def set_photo_viewer_label(self, photo_viewer_label):
        self.photo_viewer_label = photo_viewer_label

    # get the viewer label variable
    def get_photo_viewer_label(self):
        return self.photo_viewer_label


    # retrurn the widget that contains the whole tab
    def get_tab(self):
        return self.screen_widget




    # set all the labels to the correct subimages
    # after frcnn is run on the image and the subimage coordanes are found
    def set_photo_labels(self, model_output, img_np_array, finger_angles_dict):
        self.time_start = time.time()
        self.finger_angles_dict = finger_angles_dict
        self.img_np_array = img_np_array
        self.model_output = model_output
        self.delete_labels()
        self.set_initial_state_labels()
        self.photo_ready = True
        self.set_img_from_bndbox_dict(model_output, img_np_array, finger_angles_dict)


    # set all the labels to the correct subimages
    def set_img_from_bndbox_dict(self, bdnbox_dict, img_np_array, finger_angles_dict):
        self.bndbox_dict = bdnbox_dict
        self.fingers_box = [bdnbox_dict['f1'], bdnbox_dict['f2'], bdnbox_dict['f3'], bdnbox_dict['f4'], bdnbox_dict['f5']]
        # self.lunules_box = [bdnbox_dict['l1'], bdnbox_dict['l2'], bdnbox_dict['l3'], bdnbox_dict['l4'], bdnbox_dict['l5']]
        self.knuckles_m_box = [bdnbox_dict['k_m1'], bdnbox_dict['k_m2'], bdnbox_dict['k_m3'], bdnbox_dict['k_m4']]
        self.knuckles_M_box = [bdnbox_dict['k_M1'], bdnbox_dict['k_M2'], bdnbox_dict['k_M3'], bdnbox_dict['k_M4'], bdnbox_dict['k_M5']]
        self.knuckles_b_box = [bdnbox_dict['k_b1'], bdnbox_dict['k_b2'], bdnbox_dict['k_b3'], bdnbox_dict['k_b4'], bdnbox_dict['k_b5']]

        self.set_images(img_np_array, finger_angles_dict)
        self.all_included.setChecked(True)
        self.paint_buttons()

        print('time for flk tab', time.time() - self.time_start)



    def set_images(self, img_np_array, finger_angles_dict):
        for ct in [0, 1, 2, 3, 4]:
            if self.fingers_box[ct] is not None:
                self.fingers[ct].set_image_cropped(
                    self.fingers_box[ct][0], self.fingers_box[ct][1], self.fingers_box[ct][2], self.fingers_box[ct][3],
                    img_np_array, finger_angles_dict[ct + 1])
            if ct < 4:
                if self.knuckles_m_box[ct] is not None:
                    self.knuckles_m[ct].set_image_cropped(
                        self.knuckles_m_box[ct][0], self.knuckles_m_box[ct][1], self.knuckles_m_box[ct][2],
                        self.knuckles_m_box[ct][3], img_np_array, finger_angles_dict[ct + 1])
            if self.knuckles_M_box[ct] is not None:
                self.knuckles_M[ct].set_image_cropped(
                    self.knuckles_M_box[ct][0], self.knuckles_M_box[ct][1], self.knuckles_M_box[ct][2],
                    self.knuckles_M_box[ct][3], img_np_array, finger_angles_dict[ct + 1])
            if self.knuckles_b_box[ct] is not None:
                self.knuckles_b[ct].set_image_cropped(
                    self.knuckles_b_box[ct][0], self.knuckles_b_box[ct][1], self.knuckles_b_box[ct][2],
                    self.knuckles_b_box[ct][3], img_np_array, finger_angles_dict[ct + 1])


    # get the x ccordinate of the box center
    def get_box_center_x(self, box):
        return (box[0] + box[1]) / 2


    # calculate the relative position of the subimage to the main image
    def calculate_relative_position(self, image_coords, subimage_coords, margin=0):

        image_x_center = self.get_box_center_x(image_coords)
        subimage_x_center = self.get_box_center_x(subimage_coords)

        relative_min_y = image_coords[1] - subimage_coords[1]
        relative_max_y = image_coords[3] - subimage_coords[3]

        if image_x_center > subimage_x_center:
            relative_min_x = image_coords[0] - subimage_coords[0]
            relative_max_x = image_coords[2] - subimage_coords[2]
        else:
            relative_min_x = subimage_coords[0] - image_coords[0]
            relative_max_x = subimage_coords[2] - image_coords[2]
            relative_min_y *= -1
            relative_max_y *= -1

        if relative_min_x < 0:
            relative_min_x = 0
        if relative_min_y < 0:
            relative_min_y = 0 + margin

        return relative_min_x, relative_min_y, relative_max_x, relative_max_y

    # delete all the labels between each image change
    def delete_labels(self):
        self.finger_1.delete()
        self.finger_2.delete()
        self.finger_3.delete()
        self.finger_4.delete()
        self.finger_5.delete()

        self.knuckle_m_1.delete()
        self.knuckle_m_2.delete()
        self.knuckle_m_3.delete()
        self.knuckle_m_4.delete()
        self.knuckle_m_5.delete()

        self.knuckle_M_1.delete()
        self.knuckle_M_2.delete()
        self.knuckle_M_3.delete()
        self.knuckle_M_4.delete()
        self.knuckle_M_5.delete()

        self.knuckle_b_1.delete()
        self.knuckle_b_2.delete()
        self.knuckle_b_3.delete()
        self.knuckle_b_4.delete()
        self.knuckle_b_5.delete()

    # main method called for initialising the labels and the bounding boxes
    # called after each state chantes in the toolbar checkboxes
    def paint_buttons(self):

        widget_counter = 0
        if self.all_included.isChecked():
            self.finger_btn.setChecked(True)
            self.knuckle_m_btn.setChecked(True)
            self.knuckle_M_btn.setChecked(True)
            self.knuckle_b_btn.setChecked(True)
            self.all_included.setChecked(False)
            self.paint_buttons()

        if self.finger_btn.isChecked():
            self.grid_layout.addWidget(self.finger_1, widget_counter, 0)
            self.grid_layout.addWidget(self.finger_2, widget_counter, 1)
            self.grid_layout.addWidget(self.finger_3, widget_counter, 2)
            self.grid_layout.addWidget(self.finger_4, widget_counter, 3)
            self.grid_layout.addWidget(self.finger_5, widget_counter, 4)
            self.finger_1.show()
            self.finger_2.show()
            self.finger_3.show()
            self.finger_4.show()
            self.finger_5.show()
            widget_counter += 1
        else:
            self.all_included.setChecked(False)
            self.grid_layout.removeWidget(self.finger_1)
            self.grid_layout.removeWidget(self.finger_2)
            self.grid_layout.removeWidget(self.finger_3)
            self.grid_layout.removeWidget(self.finger_4)
            self.grid_layout.removeWidget(self.finger_5)
            self.finger_1.hide()
            self.finger_2.hide()
            self.finger_3.hide()
            self.finger_4.hide()
            self.finger_5.hide()

        if self.knuckle_m_btn.isChecked():
            self.grid_layout.addWidget(self.knuckle_m_1, widget_counter, 0)
            self.grid_layout.addWidget(self.knuckle_m_2, widget_counter, 1)
            self.grid_layout.addWidget(self.knuckle_m_3, widget_counter, 2)
            self.grid_layout.addWidget(self.knuckle_m_4, widget_counter, 3)
            self.knuckle_m_1.show()
            self.knuckle_m_2.show()
            self.knuckle_m_3.show()
            self.knuckle_m_4.show()
            widget_counter += 1
        else:
            self.grid_layout.removeWidget(self.knuckle_m_1)
            self.grid_layout.removeWidget(self.knuckle_m_2)
            self.grid_layout.removeWidget(self.knuckle_m_3)
            self.grid_layout.removeWidget(self.knuckle_m_4)
            self.knuckle_m_1.hide()
            self.knuckle_m_2.hide()
            self.knuckle_m_3.hide()
            self.knuckle_m_4.hide()

        if self.knuckle_M_btn.isChecked():
            self.grid_layout.addWidget(self.knuckle_M_1, widget_counter, 0)
            self.grid_layout.addWidget(self.knuckle_M_2, widget_counter, 1)
            self.grid_layout.addWidget(self.knuckle_M_3, widget_counter, 2)
            self.grid_layout.addWidget(self.knuckle_M_4, widget_counter, 3)
            self.grid_layout.addWidget(self.knuckle_M_5, widget_counter, 4)
            self.knuckle_M_5.show()
            self.knuckle_M_4.show()
            self.knuckle_M_3.show()
            self.knuckle_M_2.show()
            self.knuckle_M_1.show()
            widget_counter += 1
        else:
            self.grid_layout.removeWidget(self.knuckle_M_1)
            self.grid_layout.removeWidget(self.knuckle_M_2)
            self.grid_layout.removeWidget(self.knuckle_M_3)
            self.grid_layout.removeWidget(self.knuckle_M_4)
            self.grid_layout.removeWidget(self.knuckle_M_5)
            self.knuckle_M_5.hide()
            self.knuckle_M_4.hide()
            self.knuckle_M_3.hide()
            self.knuckle_M_2.hide()
            self.knuckle_M_1.hide()

        if self.knuckle_b_btn.isChecked():
            self.grid_layout.addWidget(self.knuckle_b_1, widget_counter, 0)
            self.grid_layout.addWidget(self.knuckle_b_2, widget_counter, 1)
            self.grid_layout.addWidget(self.knuckle_b_3, widget_counter, 2)
            self.grid_layout.addWidget(self.knuckle_b_4, widget_counter, 3)
            self.grid_layout.addWidget(self.knuckle_b_5, widget_counter, 4)
            self.knuckle_b_1.show()
            self.knuckle_b_2.show()
            self.knuckle_b_3.show()
            self.knuckle_b_4.show()
            self.knuckle_b_5.show()
            widget_counter += 1
        else:
            self.grid_layout.removeWidget(self.knuckle_b_1)
            self.grid_layout.removeWidget(self.knuckle_b_2)
            self.grid_layout.removeWidget(self.knuckle_b_3)
            self.grid_layout.removeWidget(self.knuckle_b_4)
            self.grid_layout.removeWidget(self.knuckle_b_5)
            self.knuckle_b_1.hide()
            self.knuckle_b_2.hide()
            self.knuckle_b_3.hide()
            self.knuckle_b_4.hide()
            self.knuckle_b_5.hide()

        self.main_window.flk_label.remove_bounding_box()

        # draw the bounding boxes on the main image label for each feature if that specific checkbox in checked
        if self.add_bndboxes.isChecked():
            if self.photo_ready:
                height_r = self.main_window.flk_label.get_height_ratio()
                width_r = self.main_window.flk_label.get_width_ratio()
                if self.finger_btn.isChecked():
                    ct = 0
                    for finger in self.fingers_box:
                        if finger:
                            self.main_window.flk_label.add_bounding_box((finger[0]+ 7.5) * height_r, (finger[1]+ 7.5) * width_r,
                                                                                (finger[2]+ 7.5) * height_r, (finger[3]+ 7.5) * width_r,
                                                                                'red', 'f' + str(ct + 1))
                            ct+=1

                if self.knuckle_m_btn.isChecked():
                    ct = 0
                    for knuckle_m in self.knuckles_m_box:
                        if knuckle_m:
                            self.main_window.flk_label.add_bounding_box((knuckle_m[0]+ 7.5) * height_r,
                                                                                 (knuckle_m[1]+ 7.5) * width_r,
                                                                                 (knuckle_m[2]+ 7.5) * height_r,
                                                                                 (knuckle_m[3]+ 7.5) * width_r,
                                                                                 'green', 'dip' + str(ct + 1))
                        ct += 1

                if self.knuckle_M_btn.isChecked():
                    ct = 0
                    for knuckle_M in self.knuckles_M_box:
                        if knuckle_M:
                            self.main_window.flk_label.add_bounding_box((knuckle_M[0]+ 7.5) * height_r,
                                                                                 (knuckle_M[1]+ 7.5) * width_r,
                                                                                 (knuckle_M[2]+ 7.5) * height_r,
                                                                                 (knuckle_M[3]+ 7.5) * width_r,
                                                                                 '#40E0D0', 'pip' + str(ct + 1))
                        ct+=1
                if self.knuckle_b_btn.isChecked():
                    ct = 0
                    for knuckle_b in self.knuckles_b_box:
                        if knuckle_b:
                            self.main_window.flk_label.add_bounding_box((knuckle_b[0]+ 7.5) * height_r,
                                                                                 (knuckle_b[1]+ 7.5) * width_r,
                                                                                 (knuckle_b[2]+ 7.5) * height_r,
                                                                                 (knuckle_b[3]+ 7.5) * width_r,
                                                                                 'purple', 'mcp' + str(ct + 1))
                        ct+=1
        else:
            self.main_window.flk_label.remove_bounding_box()


#------------------------------------------------------------------------
#----------------------  METHODS FOR THE MENU BAR -------------------------
#------------------------------------------------------------------------

    # show the legend on the main image label
    # each feature name with the color of the bounding box
    def show_legend(self):
        self.main_window.flk_label.draw_text('Fingernails', 'red')
        self.main_window.flk_label.draw_text('Knuckles minor', 'green')
        self.main_window.flk_label.draw_text('Knuckles Major', '#40E0D0')
        self.main_window.flk_label.draw_text('Knuckles base', 'purple')

    # hide the legend on the main image label
    def hide_legend(self):
        self.main_window.flk_label.delete_text()

# ------------------------------------------------------------------------
# ----------------------  METHODS FOR THE MENU BAR -------------------------
# ------------------------------------------------------------------------

    def change_label_dimension(self):
        sender = self.sender().objectName()
        if self.small_labels.isChecked() and sender == 'small_labels':
            self.medium_labels.setChecked(False)
            self.large_labels.setChecked(False)
            height = 400
            width = 300
        elif self.medium_labels.isChecked() and sender == 'medium_labels':
            self.small_labels.setChecked(False)
            self.large_labels.setChecked(False)
            height = 550
            width = 400
        elif self.large_labels.isChecked() and sender == 'large_labels':
            self.small_labels.setChecked(False)
            self.medium_labels.setChecked(False)
            height = 750
            width = 600
        else:
            return
        self.small_labels.setDisabled(True)
        self.medium_labels.setDisabled(True)
        self.large_labels.setDisabled(True)

        self.label_height = height
        self.label_width = width

        if self.photo_ready:
            self.set_photo_labels(self.model_output, self.img_np_array, self.finger_angles_dict)
        else:
            for label in self.fingers:
                label.set_height(height)
                label.set_width(width)
            for label in self.knuckles_m:
                label.set_height(height)
                label.set_width(width)
            for label in self.knuckles_M:
                label.set_height(height)
                label.set_width(width)
            for label in self.knuckles_b:
                label.set_height(height)
                label.set_width(width)


        self.small_labels.setDisabled(False)
        self.medium_labels.setDisabled(False)
        self.large_labels.setDisabled(False)


    def toggle_hand_side(self, checked):
        if not checked:
            self.togle_left_right.setText("Right")
            self.hand_side = 'right'
        else:
            self.togle_left_right.setText("Left")
            self.hand_side = 'left'

    def toggle_palmar_position(self, checked):
        if checked:
            self.toggle_palmar_dorsal.setText("Palmar")
            self.hand_position = 'palmar'
        else:
            self.toggle_palmar_dorsal.setText("Dorsal")
            self.hand_position = 'dorsal'

    def get_hand_side(self):
        return self.hand_side

    def get_hand_position(self):
        return self.hand_position


    def set_conf_threshold(self):
        self.main_window.set_confidence_threshold_flk(float(self.input_conf_threshold.text()))

    # initialise the toolbar containing the checkboxes
    def tool_bar(self):
        tool_bar =  QToolBar()
        tool_bar.setMovable(False)
        self.finger_btn = check_box.CheckBox('finger_check', 'Fingers', self)
        self.knuckle_m_btn = check_box.CheckBox('knuckle_m_check','Knuckles minor', self)
        self.knuckle_M_btn = check_box.CheckBox('knuckle_M_check','Knuckles major', self)
        self.knuckle_b_btn = check_box.CheckBox('knuckle_b_check','Knuckles base', self)
        self.all_included = check_box.CheckBox('all_included', 'Select all', self)
        self.add_bndboxes = check_box.CheckBox('add_bndboxes', 'Add Bounding Boxes', self)
        self.small_labels = check_box.CheckBox('small_labels', 'Small Labels', self)
        self.medium_labels = check_box.CheckBox('medium_labels', 'Medium Labels', self)
        self.large_labels = check_box.CheckBox('large_labels', 'Large Labels', self)
        self.input_conf_threshold = QLineEdit()
        self.input_conf_threshold.setPlaceholderText('Confidence Threshold')
        self.input_conf_threshold.setFixedWidth(150)
        self.input_conf_threshold.setFixedHeight(30)
        self.input_conf_threshold.setFont(QFont('Arial', 15))

        self.conf_button = QPushButton('Set Threshold')
        self.conf_button.clicked.connect(self.set_conf_threshold)

        self.togle_left_right = QAction("Right", self)
        self.togle_left_right.setFont(QFont('Arial', 15))
        self.togle_left_right.setCheckable(True)
        self.togle_left_right.triggered.connect(self.toggle_hand_side)

        self.small_labels.setChecked(True)
        self.all_included.setChecked(True)

        self.finger_btn.stateChanged.connect(self.paint_buttons)
        self.knuckle_m_btn.stateChanged.connect(self.paint_buttons)
        self.knuckle_M_btn.stateChanged.connect(self.paint_buttons)
        self.knuckle_b_btn.stateChanged.connect(self.paint_buttons)
        self.all_included.stateChanged.connect(self.paint_buttons)
        self.add_bndboxes.stateChanged.connect(self.paint_buttons)
        self.small_labels.stateChanged.connect(self.change_label_dimension)
        self.medium_labels.stateChanged.connect(self.change_label_dimension)
        self.large_labels.stateChanged.connect(self.change_label_dimension)


        tool_bar.addWidget(self.finger_btn)
        tool_bar.addWidget(self.knuckle_m_btn)
        tool_bar.addWidget(self.knuckle_M_btn)
        tool_bar.addWidget(self.knuckle_b_btn)
        tool_bar.addWidget(self.all_included)
        tool_bar.addWidget(self.add_bndboxes)
        tool_bar.addWidget(self.small_labels)
        tool_bar.addWidget(self.medium_labels)
        tool_bar.addWidget(self.large_labels)
        tool_bar.addAction(self.togle_left_right)
        tool_bar.addWidget(self.input_conf_threshold)
        tool_bar.addWidget(self.conf_button)

        return tool_bar







