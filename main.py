import shutil

from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *

import numpy as np
import cv2
import time
import os, sys


from widgets.buttons.Button import Button as btn
from widgets.labels.Label import Label as lbl
from Model_manager import ModelManager as model_manager
from widgets.labels.PhotoDescriptionLabel import PhotoDescriptionLabel as photo_lbl
from tabs.flk_tab import FlkTab as flk_tab_class
from tabs.Vein_pattern_tab import VainPatternTab as vain_pattern_tab_class
from tabs.Lunule_seg_tab import LunuleSegTab as lunule_tab_class
from tabs.Decorations_tab import DecorationsTab as decorations_tab_class
from tabs.Jewellery_tab import Jewellery_tab as jewellery_tab_class



# TODO: add the drag and drop feature ***DONE***
# TODO: add for the flk tab switches to manually set left or right hand
        # TODO: - fix the bugs in the flk tab
        # TODO: - make all the tabs visible from when loading the app
# TODO: add the resizing feature for the img viewer
# TODO: add the legend feature for the other tabs
# TODO: remake the save feature



# test class to visualize the layout
class Color(QWidget):
    def __init__(self, color):
        super(Color, self).__init__()
        self.setAutoFillBackground(True)

        palette = self.palette()
        palette.setColor(QPalette.Window, QColor(color))
        self.setPalette(palette)




class Main():

    def __init__(self):
        app = QApplication(sys.argv)

        self.active_tab = None
        self.misc_dir = '/Users/banika/H-UNIQUE/gui_update/application/misc'

        # main window basic settings
        self.main_window = QMainWindow()
        self.main_window.setWindowTitle('GUI Application')
        self.main_window.setGeometry(100, 100, 2100, 900)
        self.main_window.show()

        self.current_tab = None

        self.photo_ready = False

        self.menu_bar()

        self.legend_visible = False


        self.main_window_widget = QWidget(self.main_window)
        self.main_window.setCentralWidget(self.main_window_widget)

        self.image_viewer_layout_box = QVBoxLayout()
        self.image_viewer_layout_box.setSpacing(0)



        self.image_widget = self.image_viewer_layout()
        self.image_viewer_layout_box.addWidget(self.image_widget, 9)
        self.live_feed_button = QPushButton('Live Feed')
        self.image_viewer_layout_box.addWidget(self.live_feed_button, 1)

        # Create a toolbar
        # self.toolbar = QToolBar("ImageViewSettings")
        # self.image_viewer_layout_box.addWidget(self.toolbar)
        #
        # # Add button 1
        # button1_action = QAction("Focus", self)
        # button1_action.triggered.connect(self.button1_clicked)
        # self.toolbar.addAction(button1_action)
        #
        # # Add button 2
        # button2_action = QAction("Move", self)
        # button2_action.triggered.connect(self.button2_clicked)
        # self.toolbar.addAction(button2_action)

        # self.image_viewer_layout_box.addWidget(self.toolbar, 1)



        self.model_output = Color('#121212')

        # setting up the main layout of the application
        main_window_layout = QHBoxLayout()
        main_window_layout.setSpacing(0)
        main_window_layout.setStretch(0, 1)
        main_window_layout.setStretch(1, 2)

        # setting up the overall layout of the application
        main_window_layout.addLayout(self.image_viewer_layout_box, stretch=1)
        main_window_layout.addWidget(self.model_output, stretch=2)
        self.main_window_widget.setLayout(main_window_layout)

        self.model_output_layout()
        self.live_feed_button.clicked.connect(self.live_feed_button_clicked)

        QCoreApplication.instance().aboutToQuit.connect(self.delete_misc)
        sys.exit(app.exec_())


    def get_lunule_index(self):
        return self.lunule_tab_object.get_lunule_index()


    def delete_misc(self):
        try:
            if os.path.exists(self.misc_dir):
                shutil.rmtree(self.misc_dir)
        except Exception as e:
            print(e)

    def live_feed_button_clicked(self):
        if self.model_manager.get_live_feed():
            self.model_manager.stop_live_feed()
            self.live_feed_button.setText('Live Feed')
        else:
            self.model_manager.start_live_feed()
            self.live_feed_button.setText('Stop Live Feed')



    def model_output_layout(self):
        self.output_tabs = QTabWidget()
        tab_layout = QVBoxLayout()

        # getting instances of the tab classes to be showed in the output tab
        self.fingers_tab_object = flk_tab_class(self)
        self.fingers_tab = self.fingers_tab_object.get_tab()

        self.vain_pattern_object = vain_pattern_tab_class(self, 'Vein Pattern', 'vein')
        self.vain_pattern_tab = self.vain_pattern_object.get_tab()

        self.lunule_tab_object = lunule_tab_class(self, 'Lunule Segmentation', 'lunule')
        self.lunule_tab = self.lunule_tab_object.get_tab()

        self.decorations_tab_object = decorations_tab_class(self, 'Decorations Segmentation', 'decorations')
        self.decorations_tab = self.decorations_tab_object.get_tab()

        self.jewellery_tab_object = jewellery_tab_class(self, 'Jewellery Segmentation', 'jewellery')
        self.jewellery_tab = self.jewellery_tab_object.get_tab()

        self.model_manager = model_manager(self, self.fingers_tab_object, self.vain_pattern_object, self.lunule_tab_object, self.decorations_tab_object, self.jewellery_tab_object)

        # init the active tab
        self.active_tab = self.fingers_tab_object
        self.current_tab = 'flk'
        self.output_tabs.addTab(self.fingers_tab, 'FLK')
        self.output_tabs.addTab(self.vain_pattern_tab, 'Vein Pattern')
        self.output_tabs.addTab(self.lunule_tab, 'Lunule Segmentation')
        self.output_tabs.addTab(self.decorations_tab, 'Decorations Segmentation')
        self.output_tabs.addTab(self.jewellery_tab, 'Jewellery Segmentation')

        tab_layout.addWidget(self.output_tabs)
        self.model_output.setLayout(tab_layout)
        self.output_tabs.currentChanged.connect(self.set_viewer_label)

        # method to show the correct widgets when switching between tabs
    def set_viewer_label(self):

        if self.output_tabs.currentWidget() == self.fingers_tab:
            self.current_tab = 'flk'
            self.flk_label.set_width(self.image_widget.width())
            self.image_widget.set_image_part(self.flk_label)
        elif self.output_tabs.currentWidget() == self.vain_pattern_tab:
            self.current_tab = 'vein'
            self.vein_label.set_width(self.image_widget.width())
            self.image_widget.set_image_part(self.vein_label)
        elif self.output_tabs.currentWidget() == self.lunule_tab:
            self.current_tab = 'lunule'
            self.lunule_label.set_width(self.image_widget.width())
            self.image_widget.set_image_part(self.lunule_label)
        elif self.output_tabs.currentWidget() == self.decorations_tab:
            self.current_tab = 'decorations'
            self.decorations_label.set_width(self.image_widget.width())
            self.image_widget.set_image_part(self.decorations_label)
        elif self.output_tabs.currentWidget() == self.jewellery_tab:
            self.current_tab = 'jewellery'
            self.jewellery_label.set_width(self.image_widget.width())
            self.image_widget.set_image_part(self.jewellery_label)


        print(self.current_tab)
        self.main_window_widget.update()



    # ------------------
    # TODO: add this
    # ------------------
    def set_confidence_threshold_flk(self, value):
        if value > 0 and value < 1:
            self.model_manager.set_confidence_threshold_flk(value)
        elif value > 0 and value > 1 and value < 100:
            self.model_manager.set_confidence_threshold_flk(value/100)
        else:
            print('Invalid value for confidence threshold')


    def focus_clicked(self):
        pass


    def move_clicked(self):
        pass

    # setting up the image viewer layout
    def image_viewer_layout(self):




        photo_viewer_photo_descriptor_label = photo_lbl('photo_viewer', 'Photo Viewer', 'grey', False, False)
        image_selector_button = btn(self, 'photo_selector', 'change/select photo',
                                         None, 'insert_photo')
        image_selector_button.setStyleSheet("border: 3px solid black; background-color: grey; border-radius: 5px")
        photo_viewer_photo_descriptor_label.set_text_part_to_button(image_selector_button)

        self.flk_label = lbl('flk_label', 'Fingers, Lunule, Knuckle', parent=self, drag_and_drop=True)
        self.vein_label = lbl('vein_label', 'Vein Pattern', parent=self, drag_and_drop=True)
        self.lunule_label = lbl('lunule_label', 'Lunule Segmentation', parent=self, drag_and_drop=True)
        self.lunule_label.add_bounding_box(875, 879, 961, 979, 'red')
        self.decorations_label = lbl('decorations_label', 'Decorations Segmentation', parent=self, drag_and_drop=True)
        self.jewellery_label = lbl('jewellery_label', 'Jewellery Segmentation', parent=self, drag_and_drop=True)

        photo_viewer_photo_descriptor_label.set_image_part(self.flk_label)
        return photo_viewer_photo_descriptor_label



    # TODO: add this to workstation
    def set_images_to_model_output_labels(self, img):
        self.flk_label.set_width(self.image_widget.width())
        self.flk_label.set_height(self.image_widget.height())
        self.vein_label.set_width(self.image_widget.width())
        self.vein_label.set_height(self.image_widget.height())
        self.lunule_label.set_width(self.image_widget.width())
        self.lunule_label.set_height(self.image_widget.height())
        self.decorations_label.set_width(self.image_widget.width())
        self.decorations_label.set_height(self.image_widget.height())
        self.jewellery_label.set_width(self.image_widget.width())
        self.jewellery_label.set_height(self.image_widget.height())
        self.flk_label.set_label_img_from_np_array(img)
        self.vein_label.set_label_img_from_np_array(img)
        self.lunule_label.set_label_img_from_np_array(img)
        self.decorations_label.set_label_img_from_np_array(img)
        self.jewellery_label.set_label_img_from_np_array(img)
        self.main_window_widget.update()


    def set_img_to_model_output_per_tab(self, img, tab_name):
        if tab_name == 'flk':
            self.flk_label.set_width(self.image_widget.width())
            self.flk_label.set_height(self.image_widget.height())
            self.flk_label.set_label_img_from_np_array(img)
        elif tab_name == 'vein':
            self.vein_label.set_width(self.image_widget.width())
            self.vein_label.set_height(self.image_widget.height())
            self.vein_label.set_label_img_from_np_array(img)
        elif 'lunule' in tab_name:
            self.lunule_label.set_width(self.image_widget.width())
            self.lunule_label.set_height(self.image_widget.height())
            self.lunule_label.set_label_img_from_np_array(img)
        elif tab_name == 'decorations':
            self.decorations_label.set_width(self.image_widget.width())
            self.decorations_label.set_height(self.image_widget.height())
            self.decorations_label.set_label_img_from_np_array(img)



    def input_photo(self, img_path):
        self.photo_ready = True
        self.model_manager.load_image(img_path)


    def get_photo_ready(self):
        return self.photo_ready

    def set_photo_ready(self, value):
        self.photo_ready = value


    def get_hand_side_flk_tab(self):
        return self.fingers_tab_object.get_hand_side()

    def get_hand_position_flk_tab(self):
        return self.fingers_tab_object.get_hand_position()


#-----------------------------------------------------------------------
# MENU BAR SETUP
#-----------------------------------------------------------------------

    def menu_bar(self):
        menubar = QMenuBar(self.main_window)
        save = QAction("Save", self.main_window)
        save.triggered.connect(self.mbar_save)

        save_as = QAction("Save as", self.main_window)
        save_as.triggered.connect(self.mbar_save_as)

        self.legend = QAction("Show legend", self.main_window)
        self.legend.triggered.connect(self.mbar_show_legend)

        # Create top-level menu items
        fileMenu = menubar.addMenu("File")
        tools = menubar.addMenu("Tools")

        # Add actions to the menu items
        fileMenu.addAction(save)
        fileMenu.addAction(save_as)

        tools.addAction(self.legend)


    # TODO: add test mode to model to input gt
    # TODO: add report of confidence and other important variables

    # menu bar widget functions
    # show the legend of the active class on the image
    def mbar_show_legend(self):
        self.legend_visible = not self.legend_visible
        if self.legend_visible == True:
            self.fingers_tab_object.show_legend()
            self.legend.setText('Hide legend')
        else:
            self.fingers_tab_object.hide_legend()
            self.legend.setText('Show legend')

    # save the images outputed by the model in the directory where the app is running
    def mbar_save(self):
        directory_name, ok = QInputDialog.getText(self.main_window, 'Save', 'Enter folder name:')
        if ' ' in directory_name:
            pass
        if ok:
            os.mkdir(directory_name)
            self.model_manager.save_results('')

    # save the subimages in a selected directory
    def mbar_save_as(self):
        options = QFileDialog.Options()
        dir_name = QFileDialog.getExistingDirectory(self.main_window, "Save As",  "Select Directory", options=options)

        if self.active_tab != None:
            self.model_manager.save_results(dir_name)



    def get_active_tab(self):
        return self.current_tab

if __name__ == '__main__':
    main = Main()
