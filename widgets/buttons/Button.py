from PyQt5.QtWidgets import QPushButton, QFileDialog

# button class initialisation
class Button(QPushButton):
    '''
     parent: QLabel = the widget that will be affected by the button
     button_name: str
     button_text: str
     action_class: class =  where the action will be performed / viewed
     action: str = to select the type of action to be performed
    '''
    def __init__(self, parent, button_name, button_text, action_class = None, action = None):
        super(Button, self).__init__()
        self.parent = parent
        self.action_class = action_class
        self.button_text = button_text
        self.button_name = button_name
        self.photo_dir = ''
        self.setAcceptDrops(True)
        self.setFixedHeight(50)
        self.setText(self.button_text)
        self.setObjectName(self.button_name)
        self.setStyleSheet("border: 1px solid grey; background-color: grey; border-radius: 15px")

        if action:
            if action == 'insert_photo':
                self.photo_dir = '/home/hunique/Documents/demo_img'

            if 'insert_photo' in action:
                self.clicked.connect(self.open_photo_dir)


    # open photo directory
    def open_photo_dir(self):
        filename, _ = QFileDialog.getOpenFileName(self, 'Select Photo',
                                                  self.photo_dir,
                                                  'Images (*.png *.jpg)')
        if filename == '':
            return
        self.parent.input_photo(filename)  # set image to the label



