import cv2
from PyQt5.QtCore import QObject, pyqtSignal, QThread, QMutex, QTimer
import numpy as np
from PIL import Image

import os, time
import threading, queue

from models.FRCNN import inference_FRCNN_test as frcnn_inf
from  models.Inference_lunules import infer as lunule_inf
from models.Inference_veins import EAB_Demo as vein_inf
from models.Inference_tatoos.inference import TatooInference as tatoos_inf



class CamWorker(QThread):
    def __init__(self, main_window, tattoo_model, vein_model_rgb, vein_model_infrared, 
                 lunule_model, flk_model, fps=10, infrared=False):
        super(CamWorker, self).__init__()
        self.running = False
        self.tattoo_model = tattoo_model
        self.vein_model_rgb = vein_model_rgb
        self.vein_model_infrared = vein_model_infrared
        self.lunule_model = lunule_model
        self.flk_model = flk_model
        self.main_window = main_window
        self.infrared = False
        self.fps = 1
        self.timer_interval = int(1000 / self.fps)
        self.timer = QTimer()
        self.timer.timeout.connect(self.run)

    frame_mask_signal = pyqtSignal(np.ndarray, np.ndarray, str, np.ndarray)
    frame_flk_signal = pyqtSignal(dict, dict, np.ndarray)

    def get_cropped_img(self, img, box):
        xmin = int(box[0])
        ymin = int(box[1])
        xmax = int(box[2])
        ymax = int(box[3])

        try:
            xmin = max(0, xmin)
            ymin = max(0, ymin)
            xmax = min(img.shape[1], xmax)
            ymax = min(img.shape[0], ymax)
            return img[ymin:ymax, xmin:xmax]
        except:
            return None

    def run(self):
        # cap = cv2.VideoCapture('/homeself.vein_model/hunique/Desktop/output_with_frame_numbers.mp4')
        # cap = cv2.VideoCapture('/home/hunique/Desktop/test.png')
        # cap = cv2.VideoCapture('/home/hunique/Desktop/hand_live_test.mp4')
        cap = cv2.VideoCapture('/home/hunique/Desktop/hand_test_1.mov')

        # cap = cv2.VideoCapture(0)
        if self.infrared:
            cap_infrared = cv2.VideoCapture(2)
            cap_infrared.set(cv2.CAP_PROP_FPS, self.fps)
            cap_infrared.set(cv2.CAP_PROP_FRAME_WIDTH, 100)
            cap_infrared.set(cv2.CAP_PROP_FRAME_HEIGHT, 100)

        # cap = cv2.VideoCapture(0)
        # cap.set(cv2.CAP_PROP_FPS, self.fps)
        # cap.set(cv2.CAP_PROP_FRAME_WIDTH, 100)
        # cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 100)
        # cap.set(cv2.CAP_PROP_FPS, self.fps)
        
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, 3840)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 2160)
        cam_w = cap.get(cv2.CAP_PROP_FRAME_WIDTH)
        cam_h = cap.get(cv2.CAP_PROP_FRAME_HEIGHT)
        print('resolution:', cam_w, cam_h)

        # infrared resolution
        if self.infrared:
            cap_infrared.set(cv2.CAP_PROP_FRAME_WIDTH, 3840)
            cap_infrared.set(cv2.CAP_PROP_FRAME_HEIGHT, 2160)
            cam_w = cap_infrared.get(cv2.CAP_PROP_FRAME_WIDTH)
            cam_h = cap_infrared.get(cv2.CAP_PROP_FRAME_HEIGHT)
            print('resolution infrared:', cam_w, cam_h)

        self.running = True
        while self.running:
            ret, frame = cap.read()

            if self.infrared:
                ret_infrared, frame_infrared = cap_infrared.read()

            if ret:
                frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                frame = cv2.flip(frame, 1)
                # frame = frame[:, frame.shape[1]//5:4*frame.shape[1]//5]

                
                # frame = cv2.flip(frame, 1)
                if self.main_window.get_active_tab() == 'decorations':
                    print('decorations')
                    tattoo_mask = self.tattoo_model.inference(frame)
                    self.frame_mask_signal.emit(frame, tattoo_mask, 'decorations', frame)

                elif self.main_window.get_active_tab() == 'vein':
                    print('vein')
                    vein_mask_rgb = vein_inf.process_image(self.vein_model_rgb, frame)
                    vein_mask_infrared = np.zeros_like(vein_mask_rgb)
                    if self.infrared:
                        print('INFRARED THREAD')
                        if ret_infrared:
                            frame_infrared = cv2.cvtColor(frame_infrared, cv2.COLOR_BGR2RGB)
                            frame_infrared = cv2.flip(frame_infrared, 1)
                            frame_infrared = frame_infrared[:, frame_infrared.shape[1]//5:4*frame_infrared.shape[1]//5]
                            vein_mask_infrared = vein_inf.process_image(self.vein_model_infrared, frame)
                   
                    self.frame_mask_signal.emit(vein_mask_rgb, vein_mask_infrared, 'vein', frame)

                elif self.main_window.get_active_tab() == 'lunule' or self.main_window.get_active_tab() == 'flk':
                    try:
                        result_dict, fingers, angles = frcnn_inf.start_frcnn(frame, self.main_window.get_hand_side_flk_tab(), self.main_window.get_hand_position_flk_tab())

                        if self.main_window.get_active_tab() == 'flk':
                            print('flk thred live')
                            self.frame_flk_signal.emit(result_dict, angles, frame)
                            self.msleep(100)
                        else:
                            print('lunule-'+str(self.main_window.get_lunule_index()))
                            cropped_frame = self.get_cropped_img(frame, fingers[self.main_window.get_lunule_index()])
                            lunule_mask = self.lunule_model.inference(cropped_frame)
                            self.frame_mask_signal.emit(cropped_frame, lunule_mask, 'lunule-'+str(self.main_window.get_lunule_index()), frame)
                    except TypeError:
                        print('no hand detected')

        cap.release()
        if self.infrared:
            cap_infrared.release()

    def stop(self):
        self.running = False
        self.timer.stop()
        self.quit()

class Vein_model_thread(QThread):
    inference_done = pyqtSignal(np.ndarray, np.ndarray) 
    def __init__(self, model_rgb, model_infrared, img_rgb, img_infrared = None):
        super().__init__()
        self.model_infrared = model_infrared
        self.model_rgb = model_rgb
        self.img_rgb = img_rgb
        self.img_infrared = img_infrared
        # cap = cv2.VideoCapture('/homeself.vein_model/hunique/Desktop/output_with_frame_numbers.mp4')
        # cap = cv2.VideoCapture('/home/hunique/Desktop/test.png')
        # cap = cv2.VideoCapture('/home/hunique/Desktop/hand_live_test.mp4')
        # cap = cv2.VideoCapture('/home/hunique/Desktop/hand_test_1.mov')

        # cap = cv2.VideoCapture(0)ed = img_infrared
        self.running = True

    def run(self):
        while self.running:
            print('thread VEIN--picture--')

            vein_mask_rgb = vein_inf.process_image(self.model_rgb, self.img_rgb)
            if self.img_infrared is not None:
                vein_mask_infrared = vein_inf.process_image(self.model_infrared, self.img_infrared)
            else:
                vein_mask_infrared = np.zeros_like(vein_mask_rgb)

            self.inference_done.emit(vein_mask_rgb, vein_mask_infrared)
            self.running = False  
            self.quit()  

    def stop(self):
        self.running = False


class Tattoo_model_thread(QThread):
    inference_done = pyqtSignal(np.ndarray, np.ndarray)  # Signal to notify when inference is done
    def __init__(self, model, img, capture_queue = None):
        super().__init__()
        self.model = model
        self.img = img
        self.running = True

    def run(self):
        while self.running:
            print('tatoo start')
            tatoos_mask = self.model.inference(self.img)
            self.inference_done.emit(tatoos_mask, self.img)
            self.running = False  # Set the running flag to False
            self.quit()  # Stop the thread execution

    def stop(self):
        self.running = False
        self.quit()
        self.wait()


class Lunule_model_thread(QThread):
    inference_done = pyqtSignal(np.ndarray)  # Signal to notify when inference is done

    def __init__(self, model, img, finger_nb, capture_queue = None):
        super().__init__()
        self.model = model
        self.img = img
        self.finger_nb = finger_nb
        self.capture_queue = capture_queue
        self.running = True
        self.lunule_mask_dict = {}
        self.mutex = QMutex()

    def run(self):
        while self.running:
            print('lunule_start_', self.finger_nb)
            self.mutex.lock()
            lunule_mask = self.model.inference(self.img)
            self.lunule_mask_dict[self.finger_nb] = lunule_mask
        # cap = cv2.VideoCapture('/homeself.vein_model/hunique/Desktop/output_with_frame_numbers.mp4')
        # cap = cv2.VideoCapture('/home/hunique/Desktop/test.png')
        # cap = cv2.VideoCapture('/home/hunique/Desktop/hand_live_test.mp4')
        # cap = cv2.VideoCapture('/home/hunique/Desktop/hand_test_1.mov')

        # cap = cv2.VideoCapture(0)_mask_dict[self.finger_nb] = lunule_mask
            self.mutex.unlock()
            self.running = False  # Set the running flag to False
            self.quit()  # Stop the thread execution

    def stop(self):
        self.running = False



class FRCNN_model_thread(QThread):
    inference_done = pyqtSignal(dict, dict, dict)  # Signal to notify when inference is done

    def __init__(self, model, model_name, img, handside, hadnposition, threshold, capture_queue = None):
        super().__init__()
        self.model = model  # Your AI model instance
        self.model_name = model_name
        self.img = img
        self.hand_side = handside
        self.hand_position = hadnposition
        self.threshold = threshold
        self.capture_queue = capture_queue
        self.running = True


    def run(self):
        # Main logic for running the AI model inference
        while self.running:
            final_dict, fingers, angles = frcnn_inf.start_frcnn(self.img, self.hand_side, self.hand_position, self.threshold)
            print('frcnn done')
            self.inference_done.emit(final_dict, fingers, angles)
            self.running = False  # Set the running flag to False
            self.quit()  # Stop the thread execution

    def stop(self):
        self.running = False


# This class is responsible for managing the models.
class ModelManager:
    def __init__(self, main_class, flk_class_instance, vain_pattern_class_instance, lunule_class_instance, decorations_class_instance, jewellery_class_instance):
        self._main_class = main_class
        self.flk_class_instance = flk_class_instance
        self.vein_pattern_class_instance = vain_pattern_class_instance
        self.lunule_class_instance = lunule_class_instance
        self.decorations_class_instance = decorations_class_instance
        self.jewellery_class_instance = jewellery_class_instance
        self.threads = []
        self.completed_threads = []
        self.lunule_inf_class = lunule_inf.LunuleInference()
        self.image = np.array([])
        self.lunule_inf_class.build_model('/home/hunique/Desktop/GUI/gui_application_test/program/models/inference_code/lunule.pth')

        self.vein_model_rgb = vein_inf.initialize_model('rgb')
        self.vein_model_infrared = vein_inf.initialize_model('infrared')
        self.tatoos_model = tatoos_inf()
        self.tatoos_model.build_model()

        self.cam_worker = CamWorker(self._main_class, self.tatoos_model, self.vein_model_rgb,
                                    self.vein_model_infrared, self.lunule_inf_class, self.flk_class_instance, 20)
        self.img  = None
        self.cam_worker.frame_mask_signal.connect(self.load_img_np_array_liveCam)
        self.cam_worker.frame_flk_signal.connect(self.load_flk_tab_liveCam)



        # ------------------
        # TODO: add this
        # ------------------
        self.flk_threshold = 0.3



        # self.lunule_inf_class.build_model('path_here')

        self.frcnn_output = None

    def save_results(self, save_path):
        pass

    def start_live_feed(self):
        self.cam_worker.start()

    def set_current_tab_showing(self, tab):
        self.current_tab_showing = tab

    def stop_live_feed(self):
        self.cam_worker.stop()



    def get_live_feed(self):
        return self.cam_worker.running

    # ------------------
    # TODO: add this
    # ------------------
    def set_confidence_threshold_flk(self, threshold):
        self.flk_threshold = threshold


    def load_img_np_array_liveCam(self, img, mask, active_tab, orig_img):
        self._main_class.set_img_to_model_output_per_tab(orig_img, active_tab)
        self.img = img

        if active_tab == 'vein':
            # in this instance, the variables are changed:
            # vein_mask_rgb, vein_mask_infrared, 'vein', frame
            # img = vein_mask_rgb
            # mask = vein_mask_infrared
            self.vein_pattern_class_instance.set_img_to_labels(img, orig_img, mask)
        elif active_tab == 'decorations':
            self.decorations_class_instance.set_img_to_labels(mask, img)
        elif 'lunule' in active_tab:
            self.lunule_class_instance.set_single_lunle(mask, img, int(active_tab.split('-')[1]))


    def load_flk_tab_liveCam(self, result_dict, angles, img):
        self._main_class.set_img_to_model_output_per_tab(img, 'flk')
        self.flk_class_instance.set_photo_labels(result_dict, img, angles)

    def load_image_from_np_array(self, img):

        self._main_class.set_images_to_model_output_labels(img)
        self.img = img

        self._main_class.photo_ready = True
        self.flk_class_instance.img_ready = False
        self.flk_class_instance.add_bndboxes.setChecked(False)
        self.flk_class_instance.set_photo_ready(False)
        self.vein_pattern_class_instance.img_ready = False
        self.lunule_class_instance.img_ready = False
        self.decorations_class_instance.img_ready = False
        self.jewellery_class_instance.img_ready = False

        self.frcnn_thread = FRCNN_model_thread(self, 'frcnn', img,
                                               self._main_class.get_hand_side_flk_tab(),
                                               self._main_class.get_hand_position_flk_tab(),
                                               self.flk_threshold)
        self.frcnn_thread.inference_done.connect(self.update_flk_tab)
        self.frcnn_thread.start()

        self.vein_thread = Vein_model_thread(self.vein_model, img)
        self.vein_thread.inference_done.connect(self.update_vein_tab)
        self.vein_thread.start()

        self.tatto_thread = Tattoo_model_thread(self.tatoos_model, img)
        self.tatto_thread.inference_done.connect(self.update_tatoos_tab)
        self.tatto_thread.start()




    # method  to load the image and start the models
    def load_image(self, image_path):
        '''
        Load image from the given path.
        '''

        lunule_inference_dict = {}
        self.flk_class_instance.img_ready = False
        self.flk_class_instance.add_bndboxes.setChecked(False)
        self.flk_class_instance.set_photo_ready(False)

        if image_path == '':
            return

        self.time_start  = time.time()

        img = Image.open(image_path)
        img = np.array(img)
        self.img = img

        self._main_class.set_images_to_model_output_labels(img)

        self.frcnn_thread = FRCNN_model_thread(self, 'frcnn', img,
                                               self._main_class.get_hand_side_flk_tab(),
                                               self._main_class.get_hand_position_flk_tab(),
                                               self.flk_threshold)
        self.frcnn_thread.inference_done.connect(self.update_flk_tab)
        self.frcnn_thread.start()

        self.vein_thread = Vein_model_thread(self.vein_model_rgb, self.vein_model_infrared, img, img)
        self.vein_thread.inference_done.connect(self.update_vein_tab)
        self.vein_thread.start()

        self.tatto_thread = Tattoo_model_thread(self.tatoos_model, img)
        self.tatto_thread.inference_done.connect(self.update_tatoos_tab)
        self.tatto_thread.start()



    def update_flk_tab(self, result_dict, fingers, angles):
        self.flk_class_instance.set_photo_labels(result_dict, self.img, angles)
        self.frcnn_thread.stop()

        self.lunule_threads = []
        self.cropped_fingers = {}
        self.cropped_finger_coords = fingers
        if fingers[1] is not None:
            cropped_array = self.get_cropped_img(self.img, fingers[1])
            self.cropped_fingers[1] = cropped_array
            lunule_thread_1 = Lunule_model_thread(self.lunule_inf_class, cropped_array, 1)
            lunule_thread_1.start()
            self.lunule_threads.append(lunule_thread_1)
        if fingers[2] is not None:
            cropped_array = self.get_cropped_img(self.img, fingers[2])
            self.cropped_fingers[2] = cropped_array
            lunule_thread_2 = Lunule_model_thread(self.lunule_inf_class, cropped_array, 2)
            lunule_thread_2.start()
            self.lunule_threads.append(lunule_thread_2)
        if fingers[3] is not None:
            cropped_array = self.get_cropped_img(self.img, fingers[3])
            self.cropped_fingers[3] = cropped_array
            lunule_thread_3 = Lunule_model_thread(self.lunule_inf_class, cropped_array, 3)
            lunule_thread_3.start()
            self.lunule_threads.append(lunule_thread_3)
        if fingers[4] is not None:
            cropped_array = self.get_cropped_img(self.img, fingers[4])
            self.cropped_fingers[4] = cropped_array
            lunule_thread_4 = Lunule_model_thread(self.lunule_inf_class, cropped_array, 4)
            lunule_thread_4.start()
            self.lunule_threads.append(lunule_thread_4)
        if fingers[5] is not None:
            cropped_array = self.get_cropped_img(self.img, fingers[5])
            self.cropped_fingers[5] = cropped_array
            lunule_thread_5 = Lunule_model_thread(self.lunule_inf_class, cropped_array, 5)
            lunule_thread_5.start()
            self.lunule_threads.append(lunule_thread_5)

        self.timer = QTimer()
        self.timer.timeout.connect(self.check_lunule_dict)
        self.timer.start(50)


    def check_lunule_dict(self):
        lunule_dict = {}
        for thread in self.lunule_threads:
            thread.mutex.lock()
            lunule_dict[thread.finger_nb] = thread.lunule_mask_dict[thread.finger_nb]
            thread.mutex.unlock()

        for finger in [1,2,3,4,5]:
            if finger in lunule_dict and lunule_dict[finger] is not None:
                continue
            else:
                lunule_dict[finger] = None

        if not any([thread.running for thread in self.lunule_threads]):
            self.lunule_class_instance.input_lunule_dict(lunule_dict, self.cropped_fingers, self.cropped_finger_coords)



    def update_vein_tab(self, mask, mask_infrared):
        self.vein_pattern_class_instance.set_img_to_labels(mask, self.img, mask_infrared)

    def update_tatoos_tab(self, mask, img):
        self.decorations_class_instance.set_img_to_labels(mask, img)




    # called after an image is inputed in the GUI to start the FRCNN model
    def start_mode_frcnn(self, image_path):
        return frcnn_inf.start_frcnn(image_path, self._main_class.get_hand_side_flk_tab(), self._main_class.get_hand_position_flk_tab())

    def get_cropped_img(self, img, box):
        xmin = int(box[0])
        ymin = int(box[1])
        xmax = int(box[2])
        ymax = int(box[3])

        try:
            xmin = max(0, xmin)
            ymin = max(0, ymin)
            xmax = min(img.shape[1], xmax)
            ymax = min(img.shape[0], ymax)
            return img[ymin:ymax, xmin:xmax]
        except:
            return None














