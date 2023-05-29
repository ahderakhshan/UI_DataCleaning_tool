from PyQt5.QtWidgets import QFileDialog

from UI import Ui_Form
import os, json, traceback
from functools import partial
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import Qt

class LabelStatus():
    def __init__(self):
        self.label = ""
        self.edited = False

    def set_label(self, label):
        self.label = label

    def edit(self):
        self.edited = True


def get_new_label(newlabel):
    result = newlabel
    if result == 'kharab':
        result = 'w'
    elif result == 'salem':
        return 'h'
    return result


def label_process(label):
    label = label.split(' ')
    if label.__len__() == 1:
        return label[0]
    else:
        return label[0]+'\n'+label[1]


def get_object_number_and_path_of_image(file_name, number):
    file = open(file_name, 'r')
    file_lines = file.readlines()
    file_lines = file_lines[number + 1].split('/')
    folder_name = file_lines[6]
    make_json_file_name = file_lines[9].split('_')
    json_file_path = json_files_path + '/' + folder_name + '/' + make_json_file_name[0] + '_' + make_json_file_name[
        1] + \
                     '_' + make_json_file_name[2] + '_' + make_json_file_name[3] + '.json'
    object_number = int(make_json_file_name[4]) - 1
    file.close()
    return (json_file_path, object_number)


def chang_label_in_json_file(json_file_path, object_number, newlabel):
    json_file = open(json_file_path, 'r')
    json_data_read = json.load(json_file)
    json_data_read['shapes'][object_number]['label'] = get_new_label(newlabel)
    json_file.close()
    json_file = open(json_file_path, 'w')
    json.dump(json_data_read, json_file, indent=1)
    json_file.close()

def show_label_process(label):
    result =""
    for part in label.split(' '):
        result+=f'{part}\n'
    return result

def change_label_in_label_file_for_validation(counter, newlabel):
    label_file = open(data_path + '/' + files[counter] + '/labels.txt', 'r')
    sample_labels = label_file.readlines()
    valid_labels = sample_labels[0].split('_')
    correct = valid_labels[0]
    predict = valid_labels[1]
    change_to = newlabel
    sample_labels[0] = correct+'_'+predict+'_'+change_to+'\n'
    label_file.close()
    label_file = open(data_path + '/' + files[counter] + '/labels.txt', 'w')
    label_file.writelines(sample_labels)
    label_file.close()


def change_label_in_label_file_for_trains(counter, number, newlabel):
    label_file = open(data_path + '/' + files[counter] + '/labels.txt', 'r')
    sample_labels = label_file.readlines()
    sample_labels[number + 1] = newlabel + '\n'
    label_file.close()
    label_file = open(data_path + '/' + files[counter] + '/labels.txt', 'w')
    label_file.writelines(sample_labels)
    label_file.close()


class Myui(Ui_Form):
    def retranslateUi(self, MainWindow):
        super(Myui, self).retranslateUi(MainWindow)
        self.preprocess()

    def preprocess(self):
        # hide train images
        self.first_show_error = True
        self.all_train_images = [
            self.trainimage,
            self.trainimage_2,
            self.trainimage_3,
            self.trainimage_4,
            self.trainimage_5,
            self.trainimage_6,
            self.trainimage_7,
            self.trainimage_8,
            self.trainimage_9,
            self.trainimage_10,
            self.trainimage_11,
            self.trainimage_12
        ]
        i = 0
        for train_image in self.all_train_images:
            train_image.hide()
            train_image.mousePressEvent = partial(self.image_click, i)
            i+=1
        i=0

        # hide error buttons
        self.all_error_buttons = [
            self.nextbutton,
            self.previousbutton,
            self.gotobutton,
            self.imagecounter,
        ]

        for error_button in self.all_error_buttons:
            error_button.hide()

        self.validimage.hide()
        self.train.setDisabled(True)
        self.showmetrics.setDisabled(True)

        self.showerror.clicked.connect(self.showerror_clicked)
        self.nextbutton.clicked.connect(self.click_next)
        self.previousbutton.clicked.connect(self.click_previous)
        self.counter = 0
        self.gotobutton.clicked.connect(self.goto_clicked)

        # hide all current labels
        self.all_current_labels = [
            self.label,
            self.label_2,
            self.label_3,
            self.label_4,
            self.label_5,
            self.label_6,
            self.label_7,
            self.label_8,
            self.label_9,
            self.label_10,
            self.label_11,
            self.label_12,
            self.valid_label
        ]

        for current_label in self.all_current_labels:
            current_label.hide()
        self.totaledit = 0
        self.totaledit_label.hide()
        self.totaledit_count.hide()
        self.all_status = []
        self.first_time = []
        #self.result_button.clicked.connect(self.result_path_clicked)
        self.json_button.clicked.connect(self.configure_json_path)
        self.result_button.clicked.connect(self.configure_result_path)
        self.validimage.mousePressEvent = self.valid_click

    # show items in a menu with right click for validation image
    def valid_click(self,e):
        if e.button() == QtCore.Qt.RightButton:
            self.menu = QtWidgets.QMenu(self.frame)
            for label in labels:
                actn = QtWidgets.QAction(label, self.menu, checkable=True)
                actn.triggered.connect(partial(self.valid_done_click, label))
                self.menu.addAction(actn)
                self.menu.move(self.validimage.mapToGlobal((e.pos())))
            self.menu.show()

    # show items in a menu with right click for similar train images
    def image_click(self, i, e):
        if e.button() == QtCore.Qt.RightButton:
            self.menu = QtWidgets.QMenu(self.frame)
            for label in labels:
                actn = QtWidgets.QAction(label, self.menu, checkable=True)
                actn.triggered.connect(partial(self.done_click, i, label))
                self.menu.addAction(actn)
                self.menu.move(self.all_train_images[i].mapToGlobal((e.pos())))
            self.menu.show()

    def goto_clicked(self):
        self.counter = int(self.imagecounter.text()) -1
        self.showerror_clicked()

    def change(self, number):
        self.all_train_images[number].setStyleSheet("border: 3px solid gray;")

    def valid_done_click(self, newlabel):
        # get object number and path of image
        json_file_path, object_number = get_object_number_and_path_of_image(self.info_file, -1)
        chang_label_in_json_file(json_file_path, object_number, get_new_label(newlabel))
        change_label_in_label_file_for_validation(self.counter, newlabel)
        # change color of changed items
        self.validimage.setStyleSheet("border: 5px solid green;")
        self.valid_label.setStyleSheet("background-color: lightgreen;")
        self.valid_label.setText(label_process(newlabel))
        self.all_status[self.counter][13].label = (newlabel)
        if not self.all_status[self.counter][13].edited:
            self.totaledit += 1
        self.totaledit_count.display(str(self.totaledit))
        self.all_status[self.counter][13].edit()

    def done_click(self, number, newlabel):
        json_file_path, object_number = get_object_number_and_path_of_image(self.info_file, number)
        chang_label_in_json_file(json_file_path, object_number, get_new_label(newlabel))
        change_label_in_label_file_for_trains(self.counter, number, newlabel)
        self.all_train_images[number].setStyleSheet("border: 5px solid green;")
        self.all_current_labels[number].setStyleSheet("background-color: lightgreen;")
        self.all_current_labels[number].setText(label_process(newlabel))
        self.all_status[self.counter][number].label = (newlabel)
        if not self.all_status[self.counter][number].edited:
            self.totaledit += 1
        self.totaledit_count.display(str(self.totaledit))
        self.all_status[self.counter][number].edit()

    # change hide item to show
    def show_item(self):
        for train_image in self.all_train_images:
            train_image.show()
        for error_button in self.all_error_buttons:
            error_button.show()
        for current_label in self.all_current_labels:
            current_label.show()
        self.validimage.show()
        self.totaledit_count.show()
        self.totaledit_label.show()
        self.totaledit_label.setAlignment(Qt.AlignRight)
        palette = self.totaledit_count.palette()
        palette.setColor(palette.Background, QtGui.QColor(255,128,0))
        palette.setColor(palette.WindowText, QtGui.QColor(255,128,0))
        palette.setColor(palette.Dark, QtGui.QColor(255,128,0))
        palette.setColor(palette.Light, QtGui.QColor(255,128,0))
        self.totaledit_count.setPalette(palette)

    def showerror_clicked(self):
        # make border color
        global files
        files = os.listdir(data_path)
        files.sort(key=lambda x: float(x.split('_')[1]), reverse=True)
        for train_image in self.all_train_images:
            train_image.setStyleSheet("border: 3px solid gray;")
        for current_label in self.all_current_labels:
            current_label.setStyleSheet("")

        if self.first_show_error:
            self.show_item()
            self.max_counter = len(files)
            for i in range(self.max_counter):
                # False means not edited
                self.first_time.append(True)
                self.all_status.append([LabelStatus() for j in range(14)])
        self.first_show_error = False
        self.info_file = data_path+'/'+files[self.counter]+'/info.txt'
        label_file = open(data_path+'/'+files[self.counter]+'/labels.txt', 'r')
        sample_labels = label_file.readlines()
        if self.first_time[self.counter]:
            for i in range(len(sample_labels)-1):
                self.all_status[self.counter][i].set_label(sample_labels[i+1])
        self.first_time[self.counter]=False
        image_paths = []
        for i in range(1,13):
            try:
                image_paths.append(data_path+'/'+files[self.counter]+'/'+f'{i}.png')
            except:
                break
        train_show_counter = 0
        for img in image_paths:
            pix = QPixmap(img)
            self.all_train_images[train_show_counter].setPixmap(pix)
            self.all_train_images[train_show_counter].setAlignment(Qt.AlignCenter)
            set_label = self.all_status[self.counter][train_show_counter].label.split(' ')
            if set_label.__len__() == 1:
                self.all_current_labels[train_show_counter].setText(set_label[0])
            else:
                self.all_current_labels[train_show_counter].setText(set_label[0] + '\n' + set_label[1])
            if self.all_status[self.counter][train_show_counter].edited:
                self.all_current_labels[train_show_counter].setStyleSheet("background-color: lightgreen;")
                self.all_train_images[train_show_counter].setStyleSheet("border: 5px solid green;")
            self.all_current_labels[train_show_counter].setAlignment(Qt.AlignCenter)

            train_show_counter+=1
            if train_show_counter == 12:
                break
        pix = QPixmap(data_path+'/'+files[self.counter]+'/validation.png')

        self.validimage.setPixmap(pix)
        valid_label_text = sample_labels[0].split('_')
        valid_text = f"correct label:\n"
        valid_text = f"first label:\n {show_label_process(valid_label_text[0])} \n change to: \n " \
                     f"{show_label_process(valid_label_text[2])} \n predict: " \
                     f" \n {show_label_process(valid_label_text[1])}"
        self.valid_label.setText(valid_text)
        # if valid_label_text.__len__() == 1:
        #     self.valid_label.setText(valid_label_text[0])
        # else:
        #     self.valid_label.setText(valid_label_text[0]+'\n'+valid_label_text[1])
        if not self.all_status[self.counter][13].edited:
            self.validimage.setStyleSheet("border: 3px solid gray;")
        else:
            self.validimage.setStyleSheet("border: 5px solid green;")
            self.valid_label.setStyleSheet("background-color: lightgreen;")
        self.validimage.setAlignment(Qt.AlignCenter)

        self.imagecounter.setValue(self.counter+1)
        self.totaledit_count.display(str(self.totaledit))

    def click_next(self):
        self.counter += 1
        self.counter %= self.max_counter
        self.showerror_clicked()

    def click_previous(self):
        self.counter -= 1
        self.counter %= self.max_counter
        self.showerror_clicked()

    def configure_json_path(self):
        qdialog = QFileDialog()
        global json_files_path
        json_files_path = str(qdialog.getExistingDirectory())

    def configure_result_path(self):
        qdialog = QFileDialog()
        global data_path
        data_path = str(qdialog.getExistingDirectory())


def error(exc_type, exc_value, exc_tb):
    error_dialog = QtWidgets.QErrorMessage()
    error_dialog.setWindowTitle('ERROR')
    error_dialog.showMessage(f"It seems that Result or json path are not set correctly\n This two directiores should be in exe directory"
                       )
    print(exc_type)
    print(exc_value)
    print(exc_tb)
    error_dialog.exec_()

if __name__=='__main__':
    import sys

    global files
    global data_path
    data_path = './Results_Similars'

    global labels
    labels = ['salem', 'mashkook salem', 'mashkook kharab', 'kharab']
    global json_files_path
    json_files_path = './jsons'
    app = QtWidgets.QApplication(sys.argv)
    app.setStyleSheet("QLabel{font-size: 12pt;}")
    Form = QtWidgets.QWidget()
    ui = Myui()
    ui.setupUi(Form)
    Form.show()
    #sys.exit(app.exec_())
    sys.excepthook = error
    ret = app.exec_()
    sys.exit(ret)

