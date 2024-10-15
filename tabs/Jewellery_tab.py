import cv2

from tabs.Split_tab import Split_tab as Split_Tab


class Jewellery_tab(Split_Tab):

    def detect_white_points(self, image_path):
        image = cv2.imread(image_path)
        border_points = []
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        _, binary = cv2.threshold(gray, 2, 255, cv2.THRESH_BINARY)
        contours, _ = cv2.findContours(binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
        for contour in contours:
            border_points.append(contour.squeeze())
        return border_points

    def adjust_border_points(self, border_points, image):

        point_nb = -1

        for point in border_points:
            x, y = point[0], point[1]
            search_range = 10
            point_nb += 1

            image[y, x] = [255, 255, 255]

            if self.is_black(image, [x, y]):
                print('black')
                for i in range(1, search_range):
                    if self.is_white(image, (x + i, y)):
                        border_points[point_nb] = (x + i, y)
                        print(' 1')
                        break
                    if self.is_white(image, (x - i, y)):
                        border_points[point_nb] = (x - i, y)
                        print('  2')
                        break

            if self.is_white(image, [x, y]):
                print('color')
                for i in range(1, search_range):
                    if self.is_black(image, (x + i, y)):
                        border_points[point_nb] = (x + i - 1, y)
                        print('   3')
                        break
                    if self.is_black(image, (x - i, y)):
                        border_points[point_nb] = (x - i + 1, y)
                        print('    4')
                        break

        cv2.imshow('img', image)

        return border_points

        # need to see if pixel color is 0 0 0 of pixel_col[2] == 0

    def is_black(self, image, point):
        x, y = point
        pixel_color = image[y, x]
        return pixel_color[2] == 0

        # need to see if pixel_col[3] == 128

    def is_white(self, image, point):
        x, y = point
        pixel_color = image[y, x]
        return pixel_color[2] != 0

    def draw_points(self):
        self.central_widget.draw_points(self.graph_points)
        self.right_widget.draw_points(self.graph_points)

    def set_img_to_labels(self, img_fname):
        graph_output = self.get_graph_img(img_fname)
        self.graph_points = self.detect_white_points(graph_output)
        self.central_widget.draw_points(self.graph_points)
        self.right_widget.draw_points(self.graph_points)
        self.w3.setChecked(True)
        self.w3_clicked()

