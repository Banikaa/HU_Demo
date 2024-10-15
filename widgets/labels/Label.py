import cv2
import numpy as np
from PyQt5 import QtCore, QtGui
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *

import os

class Label(QLabel):

    def __init__(self, label_name, label_description, color = 'black', parent = None, zoom_feature = False, drag_and_drop = False):
        super(Label, self).__init__()
        self.color = color
        self.parent = parent
        self.image_file = ''
        self.zoom_feature = zoom_feature
        self.drag_and_drop = drag_and_drop
        self.image_inserted = False
        self.bounding_boxes = {}
        self.bounding_boxes_text = {}
        self.graph_points = {}
        self.point_objects = []
        self.legend_text = {}
        self.ratio = 0
        self.pen_point_width = 1
        self.point_color = 'green'
        self.label_name = label_name
        self.bounding_boxes_counter = 0
        self.focal_point = None
        self.is_dragging = False
        self.zoom_sync = False
        self.np_array = np.array([])

        self.setAcceptDrops(drag_and_drop)

        self.zoom_factor = 1
        self.new_x_pos, self.new_y_pos = 0, 0
        self.delta_x, self.delta_y = 0, 0
        self.start = QPoint(0, 0)

        self.newHeight, self.newWidth = self.height(), self.width()

        self.setScaledContents(True)
        self.setText(label_description)
        self.setFont(QFont('Arial', 15))
        self.setStyleSheet("border: 4px solid " + color + "; background-color: #121212; font-size: 15pt;")
        self.setContentsMargins(0, 0, 0, 0)
        self.setAlignment(Qt.AlignCenter)
        self.setObjectName(label_name)

    def set_pen_point_width(self, width):
        self.pen_point_width = width
        self.update()

    def get_pen_point_width(self):
        return self.point_pen_width

    def change_text(self, text):
        self.setText(text)
        self.update()

    def set_height(self, height):
        height = int(height)
        self.setMaximumHeight(height)
        self.setMinimumHeight(height)
        self.update()

    def set_width(self, width):
        width = int(width)
        self.setMaximumWidth(width)
        self.setMinimumWidth(width)
        self.update()

    def set_parent(self, parent):
        self.parent = parent

    def get_parent(self):
        return self.parent


    def set_sync_bool(self, bool_val):
        self.zoom_sync = bool_val


    def sync_zoom(self, zoom_factor):
        self.zoom_factor = zoom_factor
        self.update()


    def set_delta_pixmap(self, delta_x, delta_y):
        self.new_x_pos = delta_x
        self.new_y_pos = delta_y
        self.update()

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
        else:
            event.ignore()

    # for this the parent should be the main class
    def dropEvent(self, event):
        if event.mimeData().hasUrls():
            for url in event.mimeData().urls():
                if url.isLocalFile():
                    file_path = url.toLocalFile()
                    if file_path.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp', '.gif')):
                        self.set_image(file_path)
                        self.setText("")  # Clear the text once an image is dropped
                        event.acceptProposedAction()
                        self.parent.input_photo(file_path)
                        break
        else:
            event.ignore()


    def set_label_img_from_np_array(self, img_np_array):

        if img_np_array is None:
            return

        img_np_array = np.copy(img_np_array)
        self.np_array = img_np_array
        pixmap = QPixmap()
        pixmap.convertFromImage(
            QImage(img_np_array.data, img_np_array.shape[1], img_np_array.shape[0], img_np_array.shape[1]*3, QImage.Format_RGB888))

        self.image_inserted = True
        self.image = QPixmap(pixmap)

        img_height, img_width = pixmap.height(), pixmap.width()
        
            
        if self.width() / img_width > self.height() / img_height:
            scaled_width = int(self.height() / img_height * img_width)
            self.newWidth = scaled_width
            self.newHeight = self.height()
            self.set_height(self.newHeight)
            self.set_width(self.newWidth)
            self.ratio = self.newWidth / img_width
            self.pixmap = self.image.scaled(self.newWidth, self.height(), Qt.KeepAspectRatio)
        else:
            scaled_height = int(self.width() / img_width * img_height)
            self.newHeight = scaled_height
            self.newWidth = self.width()
            self.set_height(self.newHeight)
            self.set_width(self.newWidth)
            self.ratio = self.newHeight / img_height
            self.pixmap = self.image.scaled(self.newWidth, self.height(), Qt.KeepAspectRatio)

        self.update()


    def set_image(self, image_path):
        self.image_file = image_path
        if image_path != '':
            self.image_inserted = True
            self.image = QPixmap(self.image_file)

            img_height, img_width = self.image.height(), self.image.width()

            if self.width() / img_width > self.height() / img_height:
                scaled_width = int(self.height() / img_height * img_width)
                self.newWidth = scaled_width
                self.newHeight = self.height()
                self.set_height(self.newHeight)
                self.set_width(self.newWidth)
                self.ratio = self.newWidth / self.image.width()
                self.pixmap = self.image.scaled(self.newWidth, self.height(), Qt.KeepAspectRatio)
            else:
                scaled_height = int(self.width() / img_width * img_height)
                self.newHeight = scaled_height
                self.newWidth = self.width()
                self.set_height(self.newHeight)
                self.set_width(self.newWidth)
                self.ratio = self.newHeight / self.image.height()
                self.pixmap = self.image.scaled(self.newWidth, self.height(), Qt.KeepAspectRatio)
        else:
            self.image_inserted = False
            self.pixmap = QPixmap()
            self.update()


    def wheelEvent(self, event):
        if self.zoom_feature:
            zoom_in_factor = .02
            if event.angleDelta().y() > 0:
                self.zoom_factor += zoom_in_factor
            else:
                self.zoom_factor -= zoom_in_factor
            if self.zoom_sync:
                self.parent.sync_zoom(self.zoom_factor, self.new_x_pos, self.new_y_pos)
            self.update()

    def mousePressEvent(self, event: QMouseEvent):
        if self.zoom_feature:
            if event.button() == Qt.LeftButton:
                try:
                    if self.pixmap and self.pixmap.rect().contains(event.pos()):
                        self.start = event.pos()
                        self.is_dragging = True
                except Exception as e:
                    print(e)
                    pass

    def mouseMoveEvent(self, event: QMouseEvent):
        if self.zoom_feature:
            if self.is_dragging:
                self.delta_x = event.pos().x() - self.start.x()
                self.delta_y = event.pos().y() - self.start.y()
                self.new_x_pos, self.new_y_pos = self.new_x_pos + self.delta_x, self.new_y_pos + self.delta_y
                if self.zoom_sync:
                    self.parent.sync_zoom(self.zoom_factor, self.new_x_pos, self.new_y_pos)
                self.start = event.pos()
                self.update()

    def mouseReleaseEvent(self, event: QMouseEvent):
        if self.zoom_feature:
            if event.button() == Qt.LeftButton:
                self.is_dragging = False


    def paintEvent(self, event):
        super().paintEvent(event)
        painter = QPainter(self)

        point_pen = QPen(QColor(self.point_color))
        point_pen.setWidth(self.pen_point_width)
        painter.setPen(point_pen)

        if self.image_inserted:
           
            scaled_pixmap = self.pixmap.scaled(int(self.newWidth * self.zoom_factor), int(self.newHeight * self.zoom_factor),
                                          Qt.KeepAspectRatio)
            painter.drawPixmap(self.new_x_pos, self.new_y_pos, scaled_pixmap)


        # draw boundary eg lunule segmentation
        if self.point_objects:
            for points in self.point_objects:
                for i in range(len(points)):
                    if i < len(points)-1:
                        p1 = QPointF(points[i][0] * self.zoom_factor + self.new_x_pos, points[i][1] * self.zoom_factor + self.new_y_pos)
                        p2 = QPointF(points[i+1][0] * self.zoom_factor + self.new_x_pos, points[i+1][1] * self.zoom_factor + self.new_y_pos)
                        painter.drawLine(p1, p2)
                    else:
                        p1 = QPointF(points[-1][0] * self.zoom_factor + self.new_x_pos, points[-1][1] * self.zoom_factor + self.new_y_pos)
                        p2 = QPointF(points[0][0] * self.zoom_factor + self.new_x_pos, points[0][1] * self.zoom_factor + self.new_y_pos)
                        painter.drawLine(p1, p2)

        # draw graph eg vain pattern segmentation
        for color in self.graph_points:
            for i in range(len(self.graph_points[color]) - 1):
                if self.are_points_connected(self.graph_points[color], i, i + 1):
                    p1 = QPointF(self.graph_points[color][i][0] * self.zoom_factor * self.ratio + self.new_x_pos, self.graph_points[color][i][1] * self.zoom_factor * self.ratio + self.new_y_pos)
                    p2 = QPointF(self.graph_points[color][i + 1][0] * self.zoom_factor * self.ratio + self.new_x_pos, self.graph_points[color][i + 1][1] * self.zoom_factor * self.ratio + self.new_y_pos)
                    painter.drawLine(p1, p2)
                else:
                    p1 = QPointF(self.graph_points[color][i][0] * self.zoom_factor * self.ratio + self.new_x_pos, self.graph_points[color][i][1] * self.zoom_factor * self.ratio + self.new_y_pos)
                    painter.drawPoint(p1)

        # draw bounding boxes eg fingernails, lunules, etc
        for color in self.bounding_boxes:
            for box in self.bounding_boxes[color]:
                pen = QPen(QColor(color))
                pen.setWidth(2)
                painter.setPen(pen)
                box = QRect(box.x() * self.zoom_factor + self.new_x_pos, box.y() * self.zoom_factor + self.new_y_pos,
                            box.width() * self.zoom_factor, box.height() * self.zoom_factor)
                painter.drawRect(box)
            for text in self.bounding_boxes_text[color]:
                font = QFont()
                font.setPointSize(15)
                font.setBold(False)
                painter.setFont(font)
                painter.drawText(text[1], text[2], text[0])

        if self.legend_text:
            ct = 0
            for color in self.legend_text:
                pen = QPen(QColor(color))
                painter.setPen(pen)
                font = QFont()
                font.setPointSize(15)
                font.setBold(False)
                painter.setFont(font)
                painter.drawText(10, self.height() - 10 - 20 * ct, self.legend_text[color][0])
                ct += 1


    def update_geometry(self):
        self.setMaximumHeight(self.newHeight)
        self.setMinimumHeight(self.newHeight)
        self.setMaximumWidth(self.newWidth)
        self.setMinimumWidth(self.newWidth)

    def add_bounding_box(self, minx, miny, maxx, maxy, color = '', text = None):
        self.color = color
        minx = int(minx)
        miny = int(miny)
        maxx = int(maxx)
        maxy = int(maxy)

        box = QRect(minx, miny, maxx - minx, maxy - miny)

        if color in self.bounding_boxes.keys():
            self.bounding_boxes[color].append(box)
            self.bounding_boxes_text[color].append([text, minx, miny-3])
        else:
            self.bounding_boxes[color] = [box]
            self.bounding_boxes_text[color] = [[text, minx, miny-3]]


    def draw_points(self, contours):
        self.point_objects = []

        for points in contours:
            if len(points) > 1:
                # print(points)
                try:
                    self.point_objects.append([(int(point[0] * self.ratio), int(point[1] * self.ratio)) for point in points])
                except IndexError:
                    pass

        self.update()


    def get_np_array(self):
        return self.np_array

    def draw_graph(self, points):
        # print('graph points: ', points)

        for color in points:
            self.graph_points[color] = [(int(point[0]), int(point[1])) for point in points[color]]
        self.update()

    def draw_points_no_ratio(self, points):
        for color in points:
            self.graph_points[color] = [(int(point[0]), int(point[1])) for point in points[color]]
        self.update()

    def delete_points(self):
        self.graph_points = {}
        self.point_objects = []
        self.update()

    def is_connected(self, point1, point2):
        return abs(point1[0] - point2[0]) <= 1 and abs(point1[1] - point2[1]) <= 1

    def are_points_connected(self, points, index1, index2):
        return self.is_connected(points[index1], points[index2])

    def set_point_color(self, color):
        self.point_color = color
        self.update()


    def delete(self):
        self.setParent(None)
        self.deleteLater()

    def draw_text(self, text, color):
        if color in self.legend_text.keys():
            self.legend_text[color].append(text)
        else:
            self.legend_text[color] = [text]
        self.update()


    def delete_text(self):
        self.legend_text = {}
        self.update()



    def remove_bounding_box(self):
        self.bounding_boxes = {}
        self.bounding_boxes_text = {}
        self.update()

    def get_img(self):
        return self.image_file


    def get_width_ratio(self):
        # return self.newWidth / self.image_width
        return self.ratio

    def get_height_ratio(self):
        return self.ratio


    def set_ratio(self, ratio):
        self.ratio = ratio
        self.update()


    def get__graph_points(self):
        return self.graph_points


    def get_width(self):
        return self.width()

    def get_height(self):
        return self.height()

