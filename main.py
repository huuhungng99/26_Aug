import os
import sys
import threading
import multiprocessing

from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

import cv2 as cv
import numpy as np
import shutil

from tral_val_division import tral_val_division
from changecoco128 import changecoco128
from VideoToImageThread import VideoToImageThread
from mark_image import MarkImageThread
from yolov5_master.train import training

import configparser
import subprocess
from datetime import date
import datetime
import imghdr
from PIL import Image
import random
import unicodedata
import ast
from class_for_build_function import CustomListWidgetItem
import time
# from StartWindow import StartWindow             # start window = cua so dieu kien bat dau kiem tra
from check_module_func import check_func
# from yolov5_master.check_screw import Yolov5
from detect_object_window import detect_func
from drag_drop_block import Dialog_01
from yolov5_master.single_checkpoint_detecting_module import detect2
import sqlite3

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setGeometry(100, 100, 800, 600)

        # Variables for tab 1: slice_image_tab_UI
        self.folder_path_source = ''
        self.folder_path_save = ''
        self.count_image = 0
        self.frame = 1

        # Variables for tab 2: mark image tab UI
        self.folder_path_source_tab2 = ''
        self.folder_path_save_tab2 = ''
        self.pt1 = (0, 0)
        self.pt2 = (0, 0)
        self.drawing = False
        self.top_left_clicked = False
        self.bottom_right_clicked = False
        self.delete_rectangle = False
        self.select_mode = True

        # Variables for tab 4: Train_Val_Division
        self.image_folder_path_tab4 = ''
        self.label_folder_path_tab4 = ''
        self.save_folder_path_tab4 = ''

        # Variables for tab 5: Train
        self.select_weights_tab5 = ''
        self.epochs = 0
        self.batch_size = 0
        self.folder_path_tab5 = ''
        self.train_image_folder_tab5 = ''
        self.val_image_folder_tab5 = ''

        self.mark_image_thread = None
        self.tral_val_division_thread = None

        # Variables for tab 8: Motion check
        self.delete_rectangle_tab8 = False
        self.select_mode_tab8 = True
        self.image_tab8 = None

        self.setWindowFlags(self.windowFlags() & ~Qt.WindowMaximizeButtonHint)
        self.setWindowIcon(QIcon('logo.png'))
        self.setWindowTitle('Sample Interface for motion checking - MTD')

        # Tạo menu
        self.create_menu()

        # Tạo ra một layout chính
        main_layout = QVBoxLayout()
        self.central_widget = QWidget()
        self.central_widget.setLayout(main_layout)
        self.setCentralWidget(self.central_widget)

        # Tạo ra một stack widget
        self.stack_widget = QStackedWidget()
        main_layout.addWidget(self.stack_widget)

        # Tạo ra các widget cho mỗi menu
        self.create_widgets()

        # Hiển thị menu 1 ban đầu
        self.switch_menu(0)

    def create_menu(self):
        # Tạo menu
        bar = self.menuBar()
        file = bar.addMenu("File")
        take_data = bar.addMenu("Take Data")
        train_detect = bar.addMenu("Training - Detect")
        build_function = bar.addMenu("Build Function")
        display = bar.addMenu("Display")

        # Tạo các action trong menu
        layout0_action = QAction("Record video", self)
        layout0_action.triggered.connect(lambda: self.switch_menu(0))
        layout1_action = QAction("Slice Image", self)
        layout1_action.triggered.connect(lambda: self.switch_menu(1))
        layout2_action = QAction("Mark Image", self)
        layout2_action.triggered.connect(lambda: self.switch_menu(2))
        layout3_action = QAction("Label Image", self)
        layout3_action.triggered.connect(lambda: self.switch_menu(3))
        layout4_action = QAction("Train Val Division", self)
        layout4_action.triggered.connect(lambda: self.switch_menu(4))
        layout5_action = QAction("Training", self)
        layout5_action.triggered.connect(lambda: self.switch_menu(5))
        layout6_action = QAction("Detect", self)
        layout6_action.triggered.connect(lambda: self.switch_menu(6))
        layout7_action = QAction("Build function", self)
        layout7_action.triggered.connect(lambda: self.switch_menu(7))
        layout8_action = QAction("New file", self)
        layout8_action.triggered.connect(lambda: self.switch_menu(8))
        layout9_action = QAction("Save file", self)
        layout9_action.triggered.connect(lambda: self.switch_menu(9))
        layout10_action = QAction("Save file as", self)
        layout10_action.triggered.connect(lambda: self.switch_menu(10))
        layout11_action  = QAction("Import weight file", self)
        layout11_action.triggered.connect(self.import_file)

        file.addAction(layout8_action)
        file.addAction(layout9_action)
        file.addAction(layout10_action)
        file.addAction(layout11_action)

        take_data.addAction(layout0_action)
        take_data.addAction(layout1_action)
        take_data.addAction(layout2_action)
        take_data.addAction(layout3_action)
        take_data.addAction(layout4_action)

        train_detect.addAction(layout5_action)
        train_detect.addAction(layout6_action)

        build_function.addAction(layout7_action)

    def create_widgets(self):
        # Tạo ra các widget cho mỗi menu
        self.menu_widgets = []

        #######################################################################################
        # Layout 0: Record video
        layout0_widget = QWidget()

        self.layout_tab0 = QFormLayout()

        self.label1_tab0 = QLabel("IP Camera")
        self.field1_tab0 = QLineEdit()

        self.label2_tab0 = QLabel("Username ")
        self.field2_tab0 = QLineEdit()

        self.label3_tab0 = QLabel("Password  ")
        self.field3_tab0 = QLineEdit()

        self.button4_tab0 = QPushButton('Record video')
        self.button4_tab0.setFixedSize(240, 25)
        self.button4_tab0.setStyleSheet("background-color: blue; color: white;")
        #self.button4_tab0.clicked.connect(self.test_live_cam)

        self.hbox1_tab0 = QHBoxLayout()
        self.hbox1_tab0.addWidget(self.label1_tab0)
        self.hbox1_tab0.addWidget(self.field1_tab0)

        self.hbox2_tab0 = QHBoxLayout()
        self.hbox2_tab0.addWidget(self.label2_tab0)
        self.hbox2_tab0.addWidget(self.field2_tab0)

        self.hbox3_tab0 = QHBoxLayout()
        self.hbox3_tab0.addWidget(self.label3_tab0)
        self.hbox3_tab0.addWidget(self.field3_tab0)

        self.hbox4_tab0 = QHBoxLayout()
        self.hbox4_tab0.addWidget(self.button4_tab0)
        self.hbox4_tab0.setAlignment(self.button4_tab0, Qt.AlignCenter)

        self.layout_tab0.addRow(self.hbox1_tab0)
        self.layout_tab0.addRow(self.hbox2_tab0)
        self.layout_tab0.addRow(self.hbox3_tab0)
        self.layout_tab0.addRow(self.hbox4_tab0)

        layout0_widget.setLayout(self.layout_tab0)

        self.menu_widgets.append(layout0_widget)
        self.stack_widget.addWidget(layout0_widget)

        #######################################################################################
        # Layout1
        layout1_widget = QWidget()

        self.layout_tab1 = QFormLayout()
        self.label1_tab1 = QLabel("Source path")
        self.field1_tab1 = QLineEdit()
        self.button1_tab1 = QPushButton("Browser...")
        self.button1_tab1.clicked.connect(self.select_folder_path)

        self.save_fixed_address_tab1 = QLabel("Save to fixed address")
        self.save_fixed_address_checkbox = QCheckBox()
        self.save_fixed_address_checkbox.stateChanged.connect(self.disable_widgets_tab1)

        self.mode_save_tab1 = QLabel("Save Mode")
        self.replace_tab1 = QRadioButton("Complete replacement")
        self.replace_tab1.setChecked(True)
        self.save_additional_tab1 = QRadioButton("Save additional")

        self.label2_tab1 = QLabel("Save path   ")
        self.field2_tab1 = QLineEdit()
        self.button2_tab1 = QPushButton("Browser...")
        self.button2_tab1.clicked.connect(self.select_save_folder_path)

        self.label3_tab1 = QLabel("Custom Frame")
        self.field3_tab1 = QSpinBox()
        self.field3_tab1.setMinimum(1)
        self.field3_tab1.setMaximum(999999999)
        self.field3_tab1.setFixedSize(80, 20)

        self.button4_tab1 = QPushButton('Slice Image')
        self.button4_tab1.setFixedSize(180, 25)
        self.button4_tab1.setStyleSheet("background-color: blue; color: white;")
        self.button4_tab1.clicked.connect(self.create_files)

        self.hbox1_tab1 = QHBoxLayout()
        self.hbox1_tab1.addWidget(self.label1_tab1)
        self.hbox1_tab1.addWidget(self.field1_tab1)
        self.hbox1_tab1.addWidget(self.button1_tab1)

        self.hbox1a_tab1 = QHBoxLayout()
        self.hbox1a_tab1.addWidget(self.save_fixed_address_tab1)
        self.hbox1a_tab1.addWidget(self.save_fixed_address_checkbox)

        self.hbox2_tab1 = QHBoxLayout()
        self.hbox2_tab1.addWidget(self.label2_tab1)
        self.hbox2_tab1.addWidget(self.field2_tab1)
        self.hbox2_tab1.addWidget(self.button2_tab1)

        self.hbox2a_tab1 = QHBoxLayout()
        self.hbox2a_tab1.addWidget(self.mode_save_tab1)
        self.hbox2a_tab1.addWidget(self.replace_tab1)
        self.hbox2a_tab1.addWidget(self.save_additional_tab1)

        self.hbox3_tab1 = QHBoxLayout()
        self.hbox3_tab1.addWidget(self.label3_tab1)
        self.hbox3_tab1.addWidget(self.field3_tab1)
        self.hbox3_tab1.setAlignment(Qt.AlignLeft)

        # hbox3a tạo ra để cách xa một chút
        self.hbox3a_tab1 = QHBoxLayout()
        self.label3a1_tab1 = QLabel()
        self.hbox3a_tab1.addWidget(self.label3a1_tab1)
        self.label3a2_tab1 = QLabel()
        self.hbox3a_tab1.addWidget(self.label3a2_tab1)

        self.hbox4_tab1 = QHBoxLayout()
        self.hbox4_tab1.addWidget(self.button4_tab1)
        self.hbox4_tab1.setAlignment(self.button4_tab1, Qt.AlignCenter)

        self.layout_tab1.addRow(self.hbox1_tab1)
        self.layout_tab1.addRow(self.hbox1a_tab1)
        self.layout_tab1.addRow(self.hbox2_tab1)
        self.layout_tab1.addRow(self.hbox2a_tab1)
        self.layout_tab1.addRow(self.hbox3_tab1)
        self.layout_tab1.addRow(self.hbox3a_tab1)
        self.layout_tab1.addRow(self.hbox4_tab1)

        layout1_widget.setLayout(self.layout_tab1)

        self.menu_widgets.append(layout1_widget)
        self.stack_widget.addWidget(layout1_widget)

        #######################################################################################
        # Layout 2
        layout2_widget = QWidget()

        self.layout_tab2 = QFormLayout()
        self.label1_tab2 = QLabel("Source path")
        self.field1_tab2 = QLineEdit()
        self.button1_tab2 = QPushButton("Browser...")
        self.button1_tab2.clicked.connect(self.select_folder_path_tab2)

        self.save_fixed_address_tab2 = QLabel("Save to fixed address")
        self.save_fixed_address_checkbox_tab2 = QCheckBox()
        self.save_fixed_address_checkbox_tab2.stateChanged.connect(self.disable_widgets_tab2)

        self.mode_save_tab2 = QLabel("Save Mode")
        self.mode_save_radio_button_group = QButtonGroup()
        self.replace_tab2 = QRadioButton("Complete replacement")
        self.replace_tab2.setChecked(True)
        self.save_additional_tab2 = QRadioButton("Save additional")
        self.mode_save_radio_button_group.addButton(self.replace_tab2)
        self.mode_save_radio_button_group.addButton(self.save_additional_tab2)

        self.select_area_mode = QLabel("Select Area Mode")
        self.select_area_button_group = QButtonGroup()
        self.draw_mode = QRadioButton("Draw")
        self.draw_mode.clicked.connect(self.disable_spinbox)
        self.draw_mode.setChecked(True)
        self.enter_coordinates_mode = QRadioButton("Enter Coordinates")
        self.select_area_button_group.addButton(self.draw_mode)
        self.select_area_button_group.addButton(self.enter_coordinates_mode)
        self.enter_coordinates_mode.clicked.connect(self.disable_button)

        self.x1 = QLabel("X1 :")
        self.x1_spin_box = QSpinBox()
        self.x1_spin_box.setMaximum(999999999)
        self.x1_spin_box.setFixedSize(80, 20)
        self.x1_spin_box.setEnabled(False)
        self.y1 = QLabel("Y1 :")
        self.y1_spin_box = QSpinBox()
        self.y1_spin_box.setMaximum(999999999)
        self.y1_spin_box.setFixedSize(80, 20)
        self.y1_spin_box.setEnabled(False)

        self.x2 = QLabel("X2 :")
        self.x2_spin_box = QSpinBox()
        self.x2_spin_box.setMaximum(999999999)
        self.x2_spin_box.setFixedSize(80, 20)
        self.x2_spin_box.setEnabled(False)
        self.y2 = QLabel("Y2 :")
        self.y2_spin_box = QSpinBox()
        self.y2_spin_box.setMaximum(999999999)
        self.y2_spin_box.setFixedSize(80, 20)
        self.y2_spin_box.setEnabled(False)

        self.label2_tab2 = QLabel("Save path   ")
        self.field2_tab2 = QLineEdit()
        self.button2_tab2 = QPushButton("Browser...")
        self.button2_tab2.clicked.connect(self.select_save_folder_path_tab2)

        self.button3_tab2 = QPushButton('Select Area')
        self.button3_tab2.setFixedSize(180, 25)
        self.button3_tab2.setStyleSheet("background-color: blue; color: white;")
        self.button3_tab2.clicked.connect(self.choose_area)

        self.button4_tab2 = QPushButton('Mark Image')
        self.button4_tab2.setFixedSize(180, 25)
        self.button4_tab2.setStyleSheet("background-color: blue; color: white;")
        self.button4_tab2.clicked.connect(self.create_mark_image)

        self.hbox1_tab2 = QHBoxLayout()
        self.hbox1_tab2.addWidget(self.label1_tab2)
        self.hbox1_tab2.addWidget(self.field1_tab2)
        self.hbox1_tab2.addWidget(self.button1_tab2)

        self.hbox1a_tab2 = QHBoxLayout()
        self.hbox1a_tab2.addWidget(self.save_fixed_address_tab2)
        self.hbox1a_tab2.addWidget(self.save_fixed_address_checkbox_tab2)

        self.hbox1b_tab2 = QHBoxLayout()
        self.hbox1b_tab2.addWidget(self.mode_save_tab2)
        self.hbox1b_tab2.addWidget(self.replace_tab2)
        self.hbox1b_tab2.addWidget(self.save_additional_tab2)

        self.hbox1c_tab2 = QHBoxLayout()
        self.hbox1c_tab2.addWidget(self.select_area_mode)
        self.hbox1c_tab2.addWidget(self.draw_mode)
        self.hbox1c_tab2.addWidget(self.enter_coordinates_mode)

        self.hbox1d_tab2 = QHBoxLayout()
        self.hbox1d_tab2.addWidget(self.x1)
        self.hbox1d_tab2.addWidget(self.y1_spin_box)
        self.hbox1d_tab2.addWidget(self.y1)
        self.hbox1d_tab2.addWidget(self.x1_spin_box)

        self.hbox1e_tab2 = QHBoxLayout()
        self.hbox1e_tab2.addWidget(self.x2)
        self.hbox1e_tab2.addWidget(self.y2_spin_box)
        self.hbox1e_tab2.addWidget(self.y2)
        self.hbox1e_tab2.addWidget(self.x2_spin_box)

        self.hbox2_tab2 = QHBoxLayout()
        self.hbox2_tab2.addWidget(self.label2_tab2)
        self.hbox2_tab2.addWidget(self.field2_tab2)
        self.hbox2_tab2.addWidget(self.button2_tab2)

        self.hbox3_tab2 = QHBoxLayout()
        self.hbox3_tab2.addWidget(self.button3_tab2)
        self.hbox3_tab2.setAlignment(self.button3_tab2, Qt.AlignCenter)

        self.hbox4_tab2 = QHBoxLayout()
        self.hbox4_tab2.addWidget(self.button4_tab2)
        self.hbox4_tab2.setAlignment(self.button4_tab2, Qt.AlignCenter)

        self.layout_tab2.addRow(self.hbox1_tab2)
        self.layout_tab2.addRow(self.hbox1a_tab2)
        self.layout_tab2.addRow(self.hbox1b_tab2)
        self.layout_tab2.addRow(self.hbox1c_tab2)
        self.layout_tab2.addRow(self.hbox1d_tab2)
        self.layout_tab2.addRow(self.hbox1e_tab2)
        self.layout_tab2.addRow(self.hbox2_tab2)
        self.layout_tab2.addRow(self.hbox3_tab2)
        self.layout_tab2.addRow(self.hbox4_tab2)

        layout2_widget.setLayout(self.layout_tab2)
        self.menu_widgets.append(layout2_widget)
        self.stack_widget.addWidget(layout2_widget)

        #######################################################################################
        # Layout 3
        layout3_widget = QWidget()

        self.layout_tab3 = QGridLayout()

        self.class_name_label_tab3 = QLabel("Class Name")

        self.class_name_edit_tab3 = QTextEdit()

        with open("object.txt", "r", encoding="utf-8") as file:
            text = file.read()
        self.class_name_edit_tab3.setText(text)

        self.class_name_edit_tab3.setFixedSize(700, 300)

        self.button_tab3 = QPushButton('Open Label Image Program')
        self.button_tab3.setFixedSize(300, 25)
        self.button_tab3.setStyleSheet("background-color: blue; color: white;")
        self.button_tab3.clicked.connect(self.run_labelImg)

        self.layout_tab3.addWidget(self.class_name_label_tab3, 1, 1, 1, 1)
        self.layout_tab3.addWidget(self.class_name_edit_tab3, 1, 2, 1, 1)
        self.layout_tab3.addWidget(self.button_tab3, 2, 2, 1, 1)

        layout3_widget.setLayout(self.layout_tab3)
        self.menu_widgets.append(layout3_widget)
        self.stack_widget.addWidget(layout3_widget)

        #######################################################################################
        # Layout 4
        layout4_widget = QWidget()

        self.layout_tab4 = QFormLayout()

        self.label1_tab4 = QLabel("Image Folder")
        self.field1_tab4 = QLineEdit()
        self.button1_tab4 = QPushButton("Browser...")
        self.button1_tab4.clicked.connect(self.select_image_folder_path_tab4)

        self.label2_tab4 = QLabel("Txt Folder     ")
        self.field2_tab4 = QLineEdit()
        self.button2_tab4 = QPushButton("Browser...")
        self.button2_tab4.clicked.connect(self.select_label_folder_path_tab4)

        self.save_fixed_address_tab4 = QLabel("Save to fixed address")
        self.save_fixed_address_checkbox_tab4 = QCheckBox()
        self.save_fixed_address_checkbox_tab4.stateChanged.connect(self.disable_widgets_tab4)

        self.label3_tab4 = QLabel("Save Folder  ")
        self.field3_tab4 = QLineEdit()
        self.button3_tab4 = QPushButton("Browser...")
        self.button3_tab4.clicked.connect(self.select_save_folder_path_tab4)

        self.button4_tab4 = QPushButton('Train - Val Division')
        self.button4_tab4.setFixedSize(240, 25)
        self.button4_tab4.setStyleSheet("background-color: blue; color: white;")
        self.button4_tab4.clicked.connect(self.tral_val_division_func)

        self.hbox1_tab4 = QHBoxLayout()
        self.hbox1_tab4.addWidget(self.label1_tab4)
        self.hbox1_tab4.addWidget(self.field1_tab4)
        self.hbox1_tab4.addWidget(self.button1_tab4)

        self.hbox2_tab4 = QHBoxLayout()
        self.hbox2_tab4.addWidget(self.label2_tab4)
        self.hbox2_tab4.addWidget(self.field2_tab4)
        self.hbox2_tab4.addWidget(self.button2_tab4)

        self.hbox2a_tab4 = QHBoxLayout()
        self.hbox2a_tab4.addWidget(self.save_fixed_address_tab4)
        self.hbox2a_tab4.addWidget(self.save_fixed_address_checkbox_tab4)

        self.hbox3_tab4 = QHBoxLayout()
        self.hbox3_tab4.addWidget(self.label3_tab4)
        self.hbox3_tab4.addWidget(self.field3_tab4)
        self.hbox3_tab4.addWidget(self.button3_tab4)

        self.hbox4_tab4 = QHBoxLayout()
        self.hbox4_tab4.addWidget(self.button4_tab4)
        self.hbox4_tab4.setAlignment(self.button4_tab4, Qt.AlignCenter)

        self.layout_tab4.addRow(self.hbox1_tab4)
        self.layout_tab4.addRow(self.hbox2_tab4)
        self.layout_tab4.addRow(self.hbox2a_tab4)
        self.layout_tab4.addRow(self.hbox3_tab4)
        self.layout_tab4.addRow(self.hbox4_tab4)

        layout4_widget.setLayout(self.layout_tab4)
        self.menu_widgets.append(layout4_widget)
        self.stack_widget.addWidget(layout4_widget)

        #######################################################################################
        # Layout 5
        layout5_widget = QWidget()

        self.layout_tab5 = QGridLayout()

        self.label1_tab5 = QLabel("Weights")
        self.layout_tab5.addWidget(self.label1_tab5, 1, 1)

        self.label2_tab5 = QLabel("Epochs ")
        self.layout_tab5.addWidget(self.label2_tab5, 2, 1)

        self.label3_tab5 = QLabel("Batch-size")
        self.layout_tab5.addWidget(self.label3_tab5, 3, 1)

        self.label4_tab5 = QLabel("Path Folder")
        self.layout_tab5.addWidget(self.label4_tab5, 4, 1)

        self.label7_tab5 = QLabel("Class Name")
        self.layout_tab5.addWidget(self.label7_tab5, 7, 1)

        self.field1_tab5 = QLineEdit()
        self.layout_tab5.addWidget(self.field1_tab5, 1, 2)

        self.field2_tab5 = QSpinBox()
        self.epochs = self.field2_tab5.value()
        self.layout_tab5.addWidget(self.field2_tab5, 2, 2)

        self.field3_tab5 = QSpinBox()
        self.batch_size = self.field3_tab5.value()
        self.layout_tab5.addWidget(self.field3_tab5, 3, 2)

        self.field4_tab5 = QLineEdit()
        self.layout_tab5.addWidget(self.field4_tab5, 4, 2)

        self.field7_tab5 = QTextEdit()
        self.field7_tab5.setFixedSize(585, 80)
        self.layout_tab5.addWidget(self.field7_tab5, 7, 2)

        self.button1_tab5 = QPushButton("Browser...")
        self.layout_tab5.addWidget(self.button1_tab5, 1, 3)
        self.button1_tab5.clicked.connect(self.select_weights_tab5_func)

        self.button2_tab5 = QPushButton("Browser...")
        self.layout_tab5.addWidget(self.button2_tab5, 4, 3)
        self.button2_tab5.clicked.connect(self.select_folder_path_tab5)

        self.save_fixed_address_tab5 = QLabel("Save to fixed address")
        self.save_fixed_address_checkbox_tab5 = QCheckBox()
        self.save_fixed_address_checkbox_tab5.stateChanged.connect(self.disable_widgets_tab5)
        self.layout_tab5.addWidget(self.save_fixed_address_tab5, 8, 1)
        self.layout_tab5.addWidget(self.save_fixed_address_checkbox_tab5, 8, 2)

        self.address_label_tab5 = QLabel("Save folder")
        self.address_field_tab5 = QLineEdit()
        self.address_button_tab5 = QPushButton("Browser...")
        self.address_button_tab5.clicked.connect(self.select_save_folder_tab5)
        self.layout_tab5.addWidget(self.address_label_tab5, 9, 1)
        self.layout_tab5.addWidget(self.address_field_tab5, 9, 2)
        self.layout_tab5.addWidget(self.address_button_tab5, 9, 3)

        self.button5_tab5 = QPushButton('Train Model')
        self.button5_tab5.setFixedSize(585, 25)
        self.button5_tab5.setStyleSheet("background-color: blue; color: white;")
        self.layout_tab5.addWidget(self.button5_tab5, 10, 2)
        self.button5_tab5.clicked.connect(self.train_model)

        layout5_widget.setLayout(self.layout_tab5)
        self.menu_widgets.append(layout5_widget)
        self.stack_widget.addWidget(layout5_widget)

        ###########################################################################################
        # Layout 6
        layout6_widget = QWidget()

        self.layout_tab6 = QGridLayout()

        self.label1_tab6 = QLabel("Weights")
        self.layout_tab6.addWidget(self.label1_tab6, 1, 1)

        self.label2_tab6 = QLabel("Source")
        self.layout_tab6.addWidget(self.label2_tab6, 4, 1)

        self.label3_tab6 = QLabel("Confidence threshold")
        self.layout_tab6.addWidget(self.label3_tab6, 5, 1)

        self.label4_tab6 = QLabel("Detect Mode")
        self.layout_tab6.addWidget(self.label4_tab6, 2, 1)

        self.label7_tab6 = QLabel("Class Name")
        self.layout_tab6.addWidget(self.label7_tab6, 7, 1)

        self.check_box_label_tab6 = QLabel("Save to fixed address")
        self.layout_tab6.addWidget(self.check_box_label_tab6, 8, 1)

        self.save_check_box_tab6 = QCheckBox()
        self.save_check_box_tab6.stateChanged.connect(self.disable_widgets_tab6)
        self.layout_tab6.addWidget(self.save_check_box_tab6, 8, 2)

        self.label8_tab6 = QLabel("Project save path")
        self.layout_tab6.addWidget(self.label8_tab6, 9, 1)

        self.label9_tab6 = QLabel("Project Name")
        self.layout_tab6.addWidget(self.label9_tab6, 10, 1)

        self.field1_tab6 = QComboBox()
        self.layout_tab6.addWidget(self.field1_tab6, 1, 2)
        self.update_combobox_tab6()

        self.field2_tab6 = QLineEdit()
        self.layout_tab6.addWidget(self.field2_tab6, 4, 2)

        self.field3_tab6 = QDoubleSpinBox()
        self.field3_tab6.setRange(0.0, 1.0)
        self.field3_tab6.setSingleStep(0.01)
        self.field3_tab6.setValue(0.7)
        self.layout_tab6.addWidget(self.field3_tab6, 5, 2)

        self.field4_tab6 = QRadioButton("Detect Image")
        self.layout_tab6.addWidget(self.field4_tab6, 2, 2)

        self.field7_tab6 = QTextEdit()
        self.field7_tab6.setFixedSize(590, 90)
        self.layout_tab6.addWidget(self.field7_tab6, 7, 2)

        self.field8_tab6 = QLineEdit()
        self.layout_tab6.addWidget(self.field8_tab6, 9, 2)

        self.field9_tab6 = QLineEdit()
        self.layout_tab6.addWidget(self.field9_tab6, 10, 2)

        self.button1_tab6 = QPushButton("Browser...")
        self.layout_tab6.addWidget(self.button1_tab6, 1, 3)
        self.button1_tab6.clicked.connect(self.select_weights_tab6)

        self.button2a_tab6 = QPushButton("Browser...")
        self.layout_tab6.addWidget(self.button2a_tab6, 4, 3)
        self.button2a_tab6.clicked.connect(self.select_source_path)

        self.field4a_tab6 = QRadioButton("Detect Video")
        self.layout_tab6.addWidget(self.field4a_tab6, 3, 2)

        self.button8_tab6 = QPushButton("Browser...")
        self.layout_tab6.addWidget(self.button8_tab6, 9, 3)
        self.button8_tab6.clicked.connect(self.select_project_save_path)

        self.button5_tab6 = QPushButton('Detect Model')
        #self.button5_tab6.setFixedSize(590, 30)
        self.button5_tab6.setStyleSheet("background-color: blue; color: white;")
        self.layout_tab6.addWidget(self.button5_tab6, 11, 2)
        self.button5_tab6.clicked.connect(self.detect_model)

        layout6_widget.setLayout(self.layout_tab6)
        self.menu_widgets.append(layout6_widget)
        self.stack_widget.addWidget(layout6_widget)

        #######################################################################################
        # Layout 7
        layout7_widget = QWidget()

        self.source_label = QLabel("Source")
        self.record_video_radio = QRadioButton("Record video")
        self.record_video_radio.setChecked(True)
        self.record_video_radio.clicked.connect(self.enable_record_video)
        self.ip_camera_radio = QRadioButton("IP camera")
        self.ip_camera_radio.clicked.connect(self.enable_ip_camera)

        self.line1 = QHBoxLayout()
        self.line1.addWidget(self.source_label)
        self.line1.addWidget(self.record_video_radio)
        self.line1.addWidget(self.ip_camera_radio)

        # Thêm label, QLineEdit và QPushButton mới
        self.record_video_path_label = QLabel("Record video path")
        self.record_video_path_edit = QLineEdit()
        self.record_video_path_button = QPushButton("Browse")
        self.record_video_path_button.clicked.connect(self.select_file)

        self.line2 = QHBoxLayout()
        self.line2.addWidget(self.record_video_path_label)
        self.line2.addWidget(self.record_video_path_edit)
        self.line2.addWidget(self.record_video_path_button)

        self.ip_camera_label = QLabel("IP camera             ")
        self.ip_camera_edit = QLineEdit()
        self.ip_camera_button = QPushButton("Enter")

        self.line3 = QHBoxLayout()
        self.line3.addWidget(self.ip_camera_label)
        self.line3.addWidget(self.ip_camera_edit)
        self.line3.addWidget(self.ip_camera_button)

        self.weight_label = QLabel("Weight                 ")
        self.weight_edit = QLineEdit()
        self.weight_button = QPushButton("Browse")
        self.weight_button.clicked.connect(self.select_weight)

        self.line3b = QHBoxLayout()
        self.line3b.addWidget(self.weight_label)
        self.line3b.addWidget(self.weight_edit)
        self.line3b.addWidget(self.weight_button)

        self.edit_checkpoint_label = QLabel("Edit checkpoint")

        self.line4 = QHBoxLayout()
        self.line4.addWidget(self.edit_checkpoint_label)

        self.drag_drop_widget = Dialog_01()

        self.run_button = QPushButton("Run program")
        self.run_button.setStyleSheet("background-color: blue; color: white;")
        self.run_button.clicked.connect(self.run_block_program)

        self.setGeometry(300, 350, 650, 400)

        self.vboxlayout = QVBoxLayout()
        self.hboxlayout = QHBoxLayout()

        self.vboxlayout.addLayout(self.line1)
        self.vboxlayout.addLayout(self.line2)
        self.vboxlayout.addLayout(self.line3)
        self.vboxlayout.addLayout(self.line3b)
        self.vboxlayout.addLayout(self.line4)

        self.vboxlayout.addWidget(self.drag_drop_widget)
        self.vboxlayout.addWidget(self.run_button)

        # Khai bao cac bien xu ly
        self.screw_check = False
        self.grease_check = False
        self.slitring_check = False

        # Thong so mac dinh
        self.ip_camera_edit.setDisabled(True)
        self.ip_camera_button.setDisabled(True)
        self.record_video_path_edit.setEnabled(True)
        self.record_video_path_button.setEnabled(True)

        self.video = None

        layout7_widget.setLayout(self.vboxlayout)
        self.menu_widgets.append(layout7_widget)
        self.stack_widget.addWidget(layout7_widget)

        ##########################################################################
        # Layout 8:
        layout8_widget = QWidget()
        self.layout_tab8 = QGridLayout()
        self.new_label_tab8 = QLabel("Class Name")
        self.edit_field_tab8 = QLineEdit()

        self.layout_tab8.addWidget(self.new_label_tab8)
        self.layout_tab8.addWidget(self.edit_field_tab8)

        layout8_widget.setLayout(self.layout_tab8)
        self.menu_widgets.append(layout8_widget)
        self.stack_widget.addWidget(layout8_widget)

    def switch_menu(self, index):
        # Xóa widget hiện tại
        current_widget = self.stack_widget.currentWidget()
        self.stack_widget.removeWidget(current_widget)

        # Hiển thị widget mới
        new_widget = self.menu_widgets[index]
        self.stack_widget.addWidget(new_widget)
        self.stack_widget.setCurrentWidget(new_widget)

    def import_file(self):
        # Mở cửa sổ chọn file
        file_dialog = QFileDialog(self)
        file_dialog.setNameFilter("All Files (*)")
        if file_dialog.exec_():
            selected_file = file_dialog.selectedFiles()[0]

            # Tạo thư mục 'weights' nếu chưa tồn tại
            current_dir = os.getcwd()
            weights_dir = os.path.join(current_dir, "weights")
            if not os.path.exists(weights_dir):
                os.makedirs(weights_dir)

            # Sao chép file đã chọn vào thư mục 'weights'
            new_file_path = os.path.join(weights_dir, os.path.basename(selected_file))
            shutil.copy(selected_file, new_file_path)
            print(f"Imported file: {new_file_path}")
            self.update_combobox_tab6()
    # Add cac function xu ly cho cac tab

    ########################################################################################################################################
    # Function xu ly cho tab 0
    def test_live_cam(self):
        # Định nghĩa các biến chứa thông tin cần thiết
        username = self.field2_tab0.text()
        password = self.field3_tab0.text()
        ip_address = self.field1_tab0.text()
        print("username = ", username)
        print("password = ", password)
        print("ip = ", ip_address)
        port = "port"
        ip_camera_url = f"rtsp://{username}:{password}@{ip_address}:{port}/stream"

        # Tạo folder lưu video
        parent_folder = r"C:\Motion tracking by MTD"
        os.makedirs(parent_folder, exist_ok=True)
        today = date.today()
        new_folder_name = today.strftime("%Y-%m-%d")
        new_folder_path = os.path.join(parent_folder, new_folder_name, 'Output Video')
        os.makedirs(new_folder_path, exist_ok=True)
        file_path = os.path.join(new_folder_path, 'output.avi')

        # Tạo đối tượng VideoCapture
        cap = cv.VideoCapture(ip_camera_url)

        # Kiểm tra nếu kết nối thành công
        if not cap.isOpened():
            #print("Can't connect to camera IP.")
            exit()

        # Định nghĩa thông số video
        fourcc = cv.VideoWriter_fourcc(*'XVID')
        out = cv.VideoWriter(file_path, fourcc, 30.0, (int(cap.get(3)), int(cap.get(4))))

        while True:
            # Đọc frame từ camera
            ret, frame = cap.read()

            if not ret:
                #print("Không thể đọc frame từ camera.")
                break

            # Lưu frame vào file video
            out.write(frame)

            # Hiển thị frame
            cv.imshow("IP Camera", frame)

            # Thoát khỏi vòng lặp khi nhấn 'q'
            if cv.waitKey(1) & 0xFF == ord('q'):
                break

        #Giải phóng tài nguyên
        cap.release()
        out.release()
        cv.destroyAllWindows()

    ########################################################################################################################################
    # Function xu ly cho tab 1
    def disable_widgets_tab1(self, state):
        if self.save_fixed_address_checkbox.isChecked():
            if state == Qt.Checked:
                self.field2_tab1.setEnabled(False)
                self.button2_tab1.setEnabled(False)
                parent_folder = r"C:\Motion tracking by MTD"
                os.makedirs(parent_folder, exist_ok=True)
                today = date.today()
                new_folder_name = today.strftime("%Y-%m-%d")
                new_folder_path = os.path.join(parent_folder, new_folder_name, 'Slice image')
                os.makedirs(new_folder_path, exist_ok=True)
                print(new_folder_path)
                self.folder_path_save = new_folder_path
                self.field2_tab1.setText(new_folder_path)
        else:
            self.field2_tab1.setEnabled(True)
            self.button2_tab1.setEnabled(True)

    def normalize_path(self, path):
        """Chuẩn hóa đường dẫn bằng cách loại bỏ dấu tiếng Việt"""
        normalized_parts = []
        for part in path.split(os.path.sep):
            normalized_part = unicodedata.normalize('NFKD', part).encode('ascii', 'ignore').decode('ascii')
            normalized_parts.append(normalized_part)
        return os.path.join(*normalized_parts)

    def select_folder_path(self):
        self.folder_path_source = QFileDialog.getExistingDirectory(self, "Choose folder")
        self.field1_tab1.setText(self.folder_path_source)

    def select_save_folder_path(self):
        self.folder_path_save = QFileDialog.getExistingDirectory(self, "Choose folder")
        self.field2_tab1.setText(self.folder_path_save)

    def create_files(self):
        if self.field1_tab1.text()  != '':
            self.folder_path_source = self.field1_tab1.text()
        if self.field2_tab1.text() != '':
            self.folder_path_save = self.field2_tab1.text()
        source_path = self.folder_path_source.replace("\\", "/")
        save_path = self.folder_path_save.replace("\\", "/")
        print("source_path = ", source_path)
        print("save_path = ", save_path)
        temp1_tab1 = source_path
        source_path = self.normalize_path(temp1_tab1)
        print("source_path new = ", source_path)
        frame = self.field3_tab1.value()
        if self.replace_tab1.isChecked():
            self.count_image = 0
            for file in os.listdir(save_path):
                file_path = os.path.join(save_path, file)
                if os.path.isfile(file_path):
                    try:
                        #with Image.open(file_path) as img:
                            # Nếu file là ảnh, xóa nó
                            os.remove(file_path)
                            #print(f"Đã xóa file ảnh: {file_path}")
                    except (IOError, OSError):
                        # Nếu file không phải là ảnh, bỏ qua
                        pass
                else:
                    # Nếu file không tồn tại, bỏ qua
                    pass
        if self.save_additional_tab1.isChecked():
            self.count_image =len(os.listdir(save_path))
        self.create_files_thread = VideoToImageThread(source_path, save_path,frame, self.count_image)          # khởi tạo class để khởi chạy luồng tạo file
        self.create_files_thread.progress_updated.connect(self.update_progress_bar)
        self.create_files_thread.finished.connect(self.show_completion_message)                                # luồng chạy xong thì hiển thị show_completion_message
        self.create_files_thread.finished.connect(self.create_files_thread.deleteLater)                        # xóa luông chạy create_files_thread
        self.create_files_thread.start()                                                                       # bắt đầu chạy luồng

        self.waiting_message = QDialog(self)
        self.waiting_message.setWindowTitle("Creating Files")
        layout = QVBoxLayout()
        label = QLabel("Please wait while the files are being created...")
        layout.addWidget(label)

        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)                                                         # Chuyển sang chế độ không xác định
        self.progress_bar.setFixedSize(300, 20)
        layout.addWidget(self.progress_bar)
        self.waiting_message.setLayout(layout)

        self.waiting_message.exec()

    def update_progress_bar(self, progress):

        self.progress_bar.setValue(progress)
        if progress == 100:
            self.waiting_message.close()

    def show_completion_message(self):
        completion_message = QMessageBox(self)
        completion_message.setIcon(QMessageBox.Information)
        completion_message.setWindowTitle("Files Created")
        completion_message.setText("The files have been created successfully.")
        infor = f'Save folder {self.folder_path_save}'
        completion_message.setInformativeText(infor)
        completion_message.setStandardButtons(QMessageBox.Ok)
        completion_message.accepted.connect(completion_message.close)                        # bấm nút OK thi đóng hộp thoại
        completion_message.finished.connect(self.show)                                       # show cửa sổ chính hoăc cửa sổ khác
        completion_message.exec()

    ##################################################################################################################################################
    # Function xu ly cho tab 2
    def disable_spinbox(self):
        self.x1_spin_box.setEnabled(False)
        self.y1_spin_box.setEnabled(False)
        self.x2_spin_box.setEnabled(False)
        self.y2_spin_box.setEnabled(False)
        self.button3_tab2.setEnabled(True)
        self.button3_tab2.setStyleSheet("background-color: blue; color: white;")
        self.select_mode = True

    def disable_button(self):
        self.x1_spin_box.setEnabled(True)
        self.y1_spin_box.setEnabled(True)
        self.x2_spin_box.setEnabled(True)
        self.y2_spin_box.setEnabled(True)
        self.button3_tab2.setEnabled(False)
        self.button3_tab2.setStyleSheet("background-color: gray; color: white;")
        self.select_mode = False

        self.y1_spin_box.setValue(self.pt1[0])
        self.x1_spin_box.setValue(self.pt1[1])
        self.y2_spin_box.setValue(self.pt2[0])
        self.x2_spin_box.setValue(self.pt2[1])

    def disable_widgets_tab2(self, state):
        if self.save_fixed_address_checkbox_tab2.isChecked():
            if state == Qt.Checked:
                self.field2_tab2.setEnabled(False)
                self.button2_tab2.setEnabled(False)
                parent_folder = r"C:\Motion tracking by MTD"
                os.makedirs(parent_folder, exist_ok=True)
                today = date.today()
                new_folder_name = today.strftime("%Y-%m-%d")
                new_folder_path = os.path.join(parent_folder, new_folder_name, 'Mark image')
                os.makedirs(new_folder_path, exist_ok=True)
                print(new_folder_path)
                self.folder_path_save_tab2 = new_folder_path
                self.field2_tab2.setText(new_folder_path)
        else:
            self.field2_tab2.setEnabled(True)
            self.button2_tab2.setEnabled(True)
    def select_folder_path_tab2(self):
        self.folder_path_source_tab2 = QFileDialog.getExistingDirectory(self, "Choose folder")
        self.field1_tab2.setText(self.folder_path_source_tab2)

    def select_save_folder_path_tab2(self):
        self.folder_path_save_tab2 = QFileDialog.getExistingDirectory(self, "Choose folder")
        self.field2_tab2.setText(self.folder_path_save_tab2)

    def choose_area(self):
        if self.field1_tab2.text() != '':
            self.folder_path_source_tab2 = self.field1_tab2.text()
        print("self.folder_path_source_tab2 = ", self.folder_path_source_tab2)
        source = self.folder_path_source_tab2.replace("\\", "/")
        print("source = ", source)
        files = os.listdir(source)
        path = source + '/' + files[0]

        def draw_rectangle(event, x, y, flags, param):
            # Sự kiện chuột trái được nhấn
            if event == cv.EVENT_LBUTTONDOWN:
                if not self.top_left_clicked:
                    self.pt1 = (x, y)
                    self.top_left_clicked = True

                elif not self.bottom_right_clicked:
                    self.pt2 = (x, y)
                    self.bottom_right_clicked = True

        # Khởi tạo cửa sổ
        cv.namedWindow('Draw Rectangle')

        # Đọc ảnh
        image = cv.imread(path)

        # Sao chép ảnh gốc để vẽ hình chữ nhật lên đó
        clone = image.copy()

        # Khởi tạo các biến toàn cục
        # Kết nối hàm callback với cửa sổ
        cv.setMouseCallback('Draw Rectangle', draw_rectangle)

        while True:
            # Hiển thị ảnh và hình chữ nhật
            cv.imshow('Draw Rectangle', image)

            # Đợi phím nhấn
            key = cv.waitKey(1) & 0xFF

            # Xóa hình chữ nhật nếu nhấn phím ESC
            if key == 27:  # 27 là mã ASCII của phím ESC
                self.pt1 = (0, 0)
                self.pt2 = (0, 0)
                self.top_left_clicked = False
                self.bottom_right_clicked = False
                self.delete_rectangle = True

            # Nếu đã nhấn cả hai điểm và không yêu cầu xóa, vẽ hình chữ nhật
            if self.top_left_clicked and self.bottom_right_clicked and not self.delete_rectangle:
                image = clone.copy()
                print('self.top_left_clicked = ', self.pt1)
                print('self.bottom_right_clicked = ', self.pt2)
                cv.rectangle(image, self.pt1, self.pt2, (0, 255, 0), 2)

            # Reset trạng thái xóa nếu đã vẽ lại hình chữ nhật
            if self.delete_rectangle and not self.drawing:
                self.delete_rectangle = False

            if key == ord('s'):
                if self.top_left_clicked and self.bottom_right_clicked:
                    object_image = clone[self.pt1[1]:self.pt2[1], self.pt1[0]:self.pt2[0]]
                    cv.imwrite('object.jpg', object_image)
                    print("Saved object.jpg")

            # Thoát khỏi vòng lặp nếu nhấn phím q
            if key == ord('q'):
                break

        cv.destroyAllWindows()

    def create_mark_image(self):
        if self.field1_tab2.text()  != '':
            self.folder_path_source_tab2 = self.field1_tab2.text()
        if self.field2_tab2.text() != '':
            self.folder_path_save_tab2 = self.field2_tab2.text()
        source_path = self.folder_path_source_tab2.replace("\\", "/")
        save_path = self.folder_path_save_tab2.replace("\\", "/")
        if self.select_mode ==  True:
            pt1 = self.pt1
            pt2 = self.pt2
        else:
            pt1 = (self.y1_spin_box.value(), self.x1_spin_box.value())
            pt2 = (self.y2_spin_box.value(), self.x2_spin_box.value())

        if self.replace_tab2.isChecked():
            self.count_image = 0                                                                         # Biến đếm số lượng file trong folder
            for file in os.listdir(save_path):
                file_path = os.path.join(save_path, file)
                if os.path.isfile(file_path):
                    try:
                        # with Image.open(file_path) as img:
                            # Nếu file là ảnh, xóa nó
                            os.remove(file_path)
                            print(f"Đã xóa file ảnh: {file_path}")
                    except (IOError, OSError):
                        # Nếu file không phải là ảnh, bỏ qua
                        pass
                else:
                    # Nếu file không tồn tại, bỏ qua
                    pass
        if self.save_additional_tab2.isChecked():
            self.count_image = len(os.listdir(save_path))                                                # Biến đếm số lượng file trong folder

        self.mark_image_thread = MarkImageThread(pt1, pt2, source_path, save_path, self.count_image)     # khởi tạo class để khởi chạy luồng tạo file
        self.mark_image_thread.progress_updated.connect(self.update_progress_bar_tab2)
        self.mark_image_thread.finished.connect(self.show_completion_message_tab2)                       # luồng chạy xong thì hiển thị show_completion_message
        self.mark_image_thread.finished.connect(self.mark_image_thread.deleteLater)                      # xóa luông chạy create_files_thread
        self.mark_image_thread.start()  # bắt đầu chạy luồng

        self.waiting_message_tab2 = QDialog(self)
        self.waiting_message_tab2.setWindowTitle("Creating Files")
        layout = QVBoxLayout()
        label = QLabel("Please wait while the files are being created...")
        layout.addWidget(label)

        self.progress_bar_tab2 = QProgressBar()
        self.progress_bar_tab2.setRange(0, 100)                                             # Chuyển sang chế độ không xác định
        self.progress_bar_tab2.setFixedSize(300, 20)
        layout.addWidget(self.progress_bar_tab2)
        self.waiting_message_tab2.setLayout(layout)

        self.waiting_message_tab2.exec()

    def update_progress_bar_tab2(self, progress):
        self.progress_bar_tab2.setValue(progress)
        if progress == 100:
            self.waiting_message_tab2.close()

    def show_completion_message_tab2(self):
        completion_message = QMessageBox(self)
        completion_message.setIcon(QMessageBox.Information)
        completion_message.setWindowTitle("Files Created")
        completion_message.setText("The files have been created successfully.")
        infor = f'Save folder {self.folder_path_save_tab2}'
        completion_message.setInformativeText(infor)
        completion_message.setStandardButtons(QMessageBox.Ok)
        completion_message.accepted.connect(completion_message.close)  # bấm nút OK thi đóng hộp thoại
        completion_message.finished.connect(self.show)  # show cửa sổ chính hoăc cửa sổ khác
        completion_message.exec()

    ########################################################################################################################################
    # Function xu ly cho tab 3
    def run_labelImg(self):
        text = self.class_name_edit_tab3.toPlainText()

        # Ghi nội dung vào file object.txt
        with open("object.txt", "w", encoding="utf-8") as file:
            file.write(text)

        parent_folder = r"C:\Motion tracking by MTD"
        os.makedirs(parent_folder, exist_ok=True)
        today = date.today()
        new_folder_name = today.strftime("%Y-%m-%d")
        new_folder_path = os.path.join(parent_folder, new_folder_name, 'Label All')
        os.makedirs(new_folder_path, exist_ok=True)

        lines = text.splitlines()

        # Tạo các thư mục trong ổ C theo nội dung từng dòng và ngày tháng năm
        for i, line in enumerate(lines, start=1):
            directory = os.path.join(new_folder_path, str(line.replace(' ', '_')) )
            #directory = f"C:\\Motion tracking by MTD\\{today}\\Label All\\Folder_{line.replace(' ', '_')}"
            if not os.path.exists(directory):
                os.makedirs(directory)

            # Tạo file classes.txt và sao chép nội dung từ object.txt
            classes_file_path = os.path.join(directory, "classes.txt")
            with open(classes_file_path, "w", encoding="utf-8") as classes_file:
                classes_file.write(text)

        program_path = os.path.join("02.labelImg-master", "labelImg.py")
        os.system(f"python {program_path}")

    ########################################################################################################################################
    # Function xu ly cho tab 4
    def disable_widgets_tab4(self, state):
        if self.save_fixed_address_checkbox_tab4.isChecked():
            if state == Qt.Checked:
                self.field3_tab4.setEnabled(False)
                self.button3_tab4.setEnabled(False)
                parent_folder = r"C:\Motion tracking by MTD"
                os.makedirs(parent_folder, exist_ok=True)
                today = date.today()
                new_folder_name = today.strftime("%Y-%m-%d")
                new_folder_path = os.path.join(parent_folder, new_folder_name, 'Tral_Val_Division')
                os.makedirs(new_folder_path, exist_ok=True)
                print(new_folder_path)
                self.save_folder_path_tab4 = new_folder_path
                self.field3_tab4.setText(new_folder_path)
        else:
            self.field3_tab4.setEnabled(True)
            self.button3_tab4.setEnabled(True)

    def select_image_folder_path_tab4(self):
        self.image_folder_path_tab4 = QFileDialog.getExistingDirectory(self, "Choose folder")
        self.field1_tab4.setText(self.image_folder_path_tab4)

    def select_label_folder_path_tab4(self):
        self.label_folder_path_tab4 = QFileDialog.getExistingDirectory(self, "Choose folder")
        self.field2_tab4.setText(self.label_folder_path_tab4)

    def select_save_folder_path_tab4(self):
        self.save_folder_path_tab4 = QFileDialog.getExistingDirectory(self, "Choose folder")
        self.field3_tab4.setText(self.save_folder_path_tab4)

    def tral_val_division_func(self):
        if self.field1_tab4.text()  != '':
            self.image_folder_path_tab4 = self.field1_tab4.text()
        if self.field2_tab4.text() != '':
            self.label_folder_path_tab4 = self.field2_tab4.text()
        if self.field3_tab4.text() != '':
            self.save_folder_path_tab4 = self.field3_tab4.text()

        image_folder = self.image_folder_path_tab4.replace("\\", "/")
        label_folder = self.label_folder_path_tab4.replace("\\", "/")
        save_folder = self.save_folder_path_tab4.replace("\\", "/")
        print("image_folder = ", image_folder)
        print("label_folder = ", label_folder)
        print("save_folder = ", save_folder)
        self.tral_val_division_thread = tral_val_division(image_folder, label_folder, save_folder)     # khởi tạo class để khởi chạy luồng tạo file
        self.tral_val_division_thread.progress_updated.connect(self.update_progress_bar_tab4)
        self.tral_val_division_thread.finished.connect(self.show_completion_message_tab4)              # luồng chạy xong thì hiển thị show_completion_message
        self.tral_val_division_thread.finished.connect(self.tral_val_division_thread.deleteLater)      # xóa luông chạy create_files_thread
        self.tral_val_division_thread.start()                                                          # bắt đầu chạy luồng

        self.waiting_message_tab4 = QDialog(self)
        self.waiting_message_tab4.setWindowTitle("Alert")
        layout = QVBoxLayout()
        label = QLabel("Please wait while the files are being created...")
        layout.addWidget(label)

        self.progress_bar_tab4 = QProgressBar()
        self.progress_bar_tab4.setRange(0, 100)  # Chuyển sang chế độ không xác định
        self.progress_bar_tab4.setFixedSize(300, 20)
        layout.addWidget(self.progress_bar_tab4)
        self.waiting_message_tab4.setLayout(layout)

        self.waiting_message_tab4.exec()

    def update_progress_bar_tab4(self, progress):
        self.progress_bar_tab4.setValue(progress)
        if progress == 100:
            self.waiting_message_tab4.close()
    def show_completion_message_tab4(self):
        completion_message = QMessageBox(self)
        completion_message.setIcon(QMessageBox.Information)
        completion_message.setWindowTitle("Files Created")
        completion_message.setText("The files have been created successfully.")
        infor = f'Save folder {self.save_folder_path_tab4}'
        completion_message.setInformativeText(infor)
        completion_message.setStandardButtons(QMessageBox.Ok)
        completion_message.accepted.connect(completion_message.close)  # bấm nút OK thi đóng hộp thoại
        completion_message.finished.connect(self.show)  # show cửa sổ chính hoăc cửa sổ khác
        completion_message.exec()

    ########################################################################################################################################
    # Function xu ly cho tab 5

    def select_weights_tab5_func(self):
        self.select_weights_tab5, _ = QFileDialog.getOpenFileName(self, "Choose file")
        self.field1_tab5.setText(self.select_weights_tab5)

    def select_weights_tab5(self):
        self.select_weights_tab5, _ = QFileDialog.getOpenFileName(self, "Choose file")
        self.field1_tab5.setText(self.select_weights_tab5)

    def select_folder_path_tab5(self):
        self.folder_path_tab5 = QFileDialog.getExistingDirectory(self, "Choose folder")
        self.field4_tab5.setText(self.folder_path_tab5)

    def select_image_train_folder_tab5(self):
        self.train_image_folder_tab5 = QFileDialog.getExistingDirectory(self, "Choose folder")
        self.field5_tab5.setText(self.train_image_folder_tab5)

    def select_image_val_folder_tab5(self):
        self.val_image_folder_tab5 = QFileDialog.getExistingDirectory(self, "Choose folder")
        self.field6_tab5.setText(self.val_image_folder_tab5)

    def select_save_folder_tab5(self):
        self.save_folder_tab5 = QFileDialog.getExistingDirectory(self, "Choose folder")
        self.address_field_tab5.setText(self.save_folder_tab5)

    def disable_widgets_tab5(self, state):
        if self.save_fixed_address_checkbox_tab5.isChecked():
            if state == Qt.Checked:
                self.address_field_tab5.setEnabled(False)
                self.address_button_tab5.setEnabled(False)
                parent_folder = r"C:\Motion tracking by MTD"
                os.makedirs(parent_folder, exist_ok=True)
                today = date.today()
                new_folder_name = today.strftime("%Y-%m-%d")
                new_folder_path = os.path.join(parent_folder, new_folder_name, 'Train')
                os.makedirs(new_folder_path, exist_ok=True)
                print(new_folder_path)
                self.folder_path_save_tab2 = new_folder_path
                self.address_field_tab5.setText(new_folder_path)
        else:
            self.address_field_tab5.setEnabled(True)
            self.address_button_tab5.setEnabled(True)
    def train_model(self):
        print("self.folder_path_tab5 = ", self.folder_path_tab5)
        train_path = os.path.join(self.folder_path_tab5,"images/train")
        temp = train_path.replace("\\", "/")
        train_path = temp
        val_path = os.path.join(self.folder_path_tab5,"images/val")
        temp = val_path.replace("\\", "/")
        val_path = temp
        print("train_path = ",train_path)
        print("val_path = ", val_path)
        self.coco128_file = changecoco128(self.folder_path_tab5, train_path, val_path, self.field7_tab5.toPlainText())
        self.coco128_file.change()

        self.epochs = self.field2_tab5.value()
        self.batch_size = self.field3_tab5.value()

        self.training_thread = training(self.select_weights_tab5, self.epochs, self.batch_size, self.address_field_tab5.text())
        self.training_thread.progress_updated.connect(self.update_progress_bar_tab5)
        self.training_thread.finished.connect(self.show_completion_message_tab5)
        self.training_thread.finished.connect(self.training_thread.deleteLater)
        self.training_thread.start()

        self.waiting_message_tab5 = QDialog(self)
        self.waiting_message_tab5.setWindowTitle("Training data")
        layout = QVBoxLayout()
        label = QLabel("Please wait while training data ...")
        layout.addWidget(label)

        self.progress_bar_tab5 = QProgressBar()
        self.progress_bar_tab5.setRange(0, 100)
        self.progress_bar_tab5.setValue(0)
        self.progress_bar_tab5.setFixedSize(300, 20)

        self.training_start_time = time.time()
        self.time_label = QLabel("Training time: 0 seconds")
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_training_time)
        self.timer.start(1000)  # Cập nhật mỗi giây

        layout.addWidget(self.progress_bar_tab5)
        layout.addWidget(self.time_label)
        self.waiting_message_tab5.setLayout(layout)

        self.waiting_message_tab5.exec()

    def update_training_time(self):
        elapsed_time = time.time() - self.training_start_time
        hours = int(elapsed_time // 3600)
        minutes = int((elapsed_time % 3600) // 60)
        seconds = int(elapsed_time % 60)
        self.time_label.setText(f"Training time: {hours:02d}:{minutes:02d}:{seconds:02d}")
    def update_progress_bar_tab5(self, progress):
        self.progress_bar_tab5.setValue(progress)
        if progress == 100:
            self.waiting_message_tab5.close()

    def show_completion_message_tab5(self):
        completion_message = QMessageBox(self)
        completion_message.setIcon(QMessageBox.Information)
        completion_message.setWindowTitle("Files Created")
        completion_message.setText("The files have been created successfully.")
        #infor = f'Save folder {self.folder_path_save}'
        infor = f'Done'
        completion_message.setInformativeText(infor)
        completion_message.setStandardButtons(QMessageBox.Ok)
        completion_message.accepted.connect(completion_message.close)  # bấm nút OK thi đóng hộp thoại
        completion_message.finished.connect(self.show)  # show cửa sổ chính hoăc cửa sổ khác
        completion_message.exec()

    ########################################################################################################################################
    # Function xu ly cho tab 6
    def update_combobox_tab6(self):
        # Đọc danh sách các file trong thư mục 'weights'
        current_dir = os.getcwd()
        weights_dir = os.path.join(current_dir, "weights")
        file_names = os.listdir(weights_dir)

        # Cập nhật QComboBox với danh sách file
        self.field1_tab6.clear()
        self.field1_tab6.addItem("Select a file")
        self.field1_tab6.addItems(file_names)
    def disable_widgets_tab6(self, state):
        if self.save_check_box_tab6.isChecked():
            if state == Qt.Checked:
                self.field8_tab6.setEnabled(False)
                self.field9_tab6.setEnabled(False)
                self.button8_tab6.setEnabled(False)
                parent_folder = r"C:\Motion tracking by MTD"
                os.makedirs(parent_folder, exist_ok=True)
                today = date.today()
                new_folder_name = today.strftime("%Y-%m-%d")
                new_folder_path = os.path.join(parent_folder, new_folder_name, 'Detect')
                os.makedirs(new_folder_path, exist_ok=True)
                print(new_folder_path)
                self.folder_path_save = new_folder_path
                self.select_project_save_path = new_folder_path
                self.field8_tab6.setText(new_folder_path)
                self.field9_tab6.setText("exp")
        else:
            self.field8_tab6.setEnabled(True)
            self.field9_tab6.setEnabled(True)
            self.button8_tab6.setEnabled(True)

    def select_weights_tab6(self):
        self.select_weights_tab6, _ = QFileDialog.getOpenFileName(self, "Choose file")
        self.field1_tab6.setItemText(0, self.select_weights_tab6)

    def select_source_path(self):
        if self.field4a_tab6.isChecked():
        #self.folder_source_path = QFileDialog.getExistingDirectory(self, "Choose folder")
            self.folder_source_path, _ = QFileDialog.getOpenFileName(self, "Choose file")
        if self.field4_tab6.isChecked():
            self.folder_source_path = QFileDialog.getExistingDirectory(self, "Choose folder")
        self.field2_tab6.setText(self.folder_source_path)

    def select_project_save_path(self):
        self.select_project_save_path = QFileDialog.getExistingDirectory(self, "Choose folder")
        self.field8_tab6.setText(self.select_project_save_path)

    def detect_model(self):
        print('self.select_weights_tab6 = ',self.select_weights_tab6)
        print('self.folder_source_path = ',self.folder_source_path)
        self.confidence_threshold = self.field3_tab6.value()
        print('self.confidence_threshold = ', self.confidence_threshold)
        #print('txt auto save = ', self.field5_tab6.isChecked())
        print("Image view = ", self.field4_tab6.isChecked())
        print("Video view = ", self.field4a_tab6.isChecked())
        print("self.select_project_save_path = ", self.select_project_save_path)
        print("Content class name = ",self.field7_tab6.toPlainText())
        print("Project name = ", self.field9_tab6.text())
        self.project_name = self.field9_tab6.text()

        config_detect = configparser.ConfigParser()
        config_detect.add_section('Section1')
        config_detect.set('Section1', 'select_weights_tab6', self.select_weights_tab6)
        config_detect.set('Section1', 'folder_source_path' , self.folder_source_path)
        config_detect.set('Section1', 'confidence_threshold ' , str(self.confidence_threshold))
        config_detect.set('Section1', 'Image_view ', str(self.field4_tab6.isChecked()))
        config_detect.set('Section1', 'Video_view ', str(self.field4a_tab6.isChecked()))
        #config_detect.set('Section1', 'txt_auto_save ', str(self.field5_tab6.isChecked()))
        config_detect.set('Section1', 'class_name ', self.field7_tab6.toPlainText())
        config_detect.set('Section1', 'Project_save_path ', self.select_project_save_path)
        config_detect.set('Section1', 'Project_name ', str(self.project_name))

        with open('config_detect.ini', 'w') as configfile_detect:
            config_detect.write(configfile_detect)

        program_path_tab6 = os.path.join("yolov5_master", "detect.py")
        os.system(f"python {program_path_tab6}")

    ########################################################################################################################################
    # Function xu ly cho tab 7
    def enable_record_video(self):
        self.ip_camera_edit.setDisabled(True)
        self.ip_camera_button.setDisabled(True)
        self.record_video_path_edit.setEnabled(True)
        self.record_video_path_button.setEnabled(True)

    def enable_ip_camera(self):
        self.ip_camera_edit.setDisabled(False)
        self.ip_camera_button.setDisabled(False)
        self.record_video_path_edit.setEnabled(False)
        self.record_video_path_button.setEnabled(False)

    def select_file(self):
        self.video, _ = QFileDialog.getOpenFileName(self, "Choose file")
        self.record_video_path_edit.setText(self.video)

    def select_weight(self):
        self.weight, _ = QFileDialog.getOpenFileName(self, "Choose file")
        self.weight_edit.setText(self.weight)

    def dragEnterEvent(self, event):
        if event.source() == self.myListWidget1:
            event.accept()
        else:
            event.ignore()

    def dropEvent(self, event):
        if event.source() == self.myListWidget1:
            item = self.myListWidget1.itemAt(event.pos())
            new_item = CustomListWidgetItem(item.text())

            # Kiểm tra xem item đã tồn tại trong self.myListWidget1 chưa
            if self.myListWidget1.findItems(new_item.text(), Qt.MatchExactly):
                # Nếu đã tồn tại, xóa item cũ
                row = self.myListWidget1.row(item)
                self.myListWidget1.takeItem(row)

            if event.destination() == self.myListWidget2:
                self.myListWidget2.addItem(new_item)
            else:
                event.ignore()
        else:
            event.ignore()

    def show_context_menu1(self, pos):
        if self.sender() == self.myListWidget1:
            listwidget = self.myListWidget1
        else:
            listwidget = self.myListWidget2

        item = listwidget.itemAt(pos)

    def show_context_menu2(self, pos):
        if self.sender() == self.myListWidget1:
            listwidget = self.myListWidget1
        else:
            listwidget = self.myListWidget2

        item = listwidget.itemAt(pos)
        if item:
            menu = QMenu()
            menu.addAction("Edit parameter")
            menu.addAction("Delete")
            menu.addAction("Rename")
            action = menu.exec_(listwidget.mapToGlobal(pos))

            if action == menu.actions()[1]:
                self.delete_item_from_listwidget2()

            if action == menu.actions()[0]:
                self.open_new_window(item)

            if action == menu.actions()[2]:
                self.rename_item_in_list()

    def open_new_window(self, item):
        if item.data(Qt.UserRole) == 1000:
            self.new_window = detect_func()
            self.new_window.show()
            result = self.new_window.exec()
            # if result == QDialog.Accepted:
            #     self.new_window.on_button_click()

        if item.data(Qt.UserRole) == 1002:
            self.new_window = check_func()
            self.new_window.show()
            result = self.new_window.exec()
            # if result == QDialog.Accepted:
            #     self.new_window.on_button_click()

        if item.data(Qt.UserRole) == 1001:
            self.new_window = check_func()
            self.new_window.show()
            result = self.new_window.exec()

    def run_block_program(self):
        # self.count_detect_module = 0
        # for i in range(self.myListWidget2.count()):
        #     item_id = self.myListWidget2.item(i).data(Qt.UserRole)
        #     if item_id == 1000:
        #         self.count_detect_module += 1
        # print("Detect items = ", self.count_detect_module)
        self.record_video_path_edit_path = self.record_video_path_edit.text()
        self.weight_path = self.weight_edit.text()

        # Dem so o trong trong database
        self.conn = sqlite3.connect('database.db')
        self.cursor = self.conn.cursor()

        # Đếm số ô trống tại những dòng có name_code = 1001
        print('-------------------------------------------')
        self.cursor.execute("SELECT COUNT(*) FROM commands WHERE command_code = 1001 AND x1 IS NULL")
        result = self.cursor.fetchone()
        print(f"Số ô trống: {result[0]}")

        if not self.record_video_path_edit_path or not self.weight_path or result[0] != 0:
            QMessageBox.information(None, "Alert", "Check the input data again!")
        else:
            detect_func = detect2(self.weight_path, self.record_video_path_edit_path)
            opt = detect_func.parse_opt()
            detect_func.main(opt)

def main():
    app = QApplication([])
    window = MainWindow()
    window.resize(800, 450)
    window.show()
    app.exec_()

if __name__ == '__main__':
    main()

