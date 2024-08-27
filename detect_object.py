from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
import sys
import configparser
import subprocess
from labelImg_master.labelImg import get_main_app
import os
import shutil
from CoordinateConverter import CoordinateConverter
import sqlite3

class detect_func(QDialog):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        # Tạo layout chính
        self.main_layout = QGridLayout()
        self.object_name_label = QLabel("Enter object name")
        self.main_layout.addWidget(self.object_name_label, 1, 1, 1, 1)

        with open('object.txt', 'r') as file:
            self.items = [item.strip() for item in file.readlines()]

        self.object_name_field = QComboBox()
        self.object_name_field.addItems(self.items)
        self.object_name_field.currentIndexChanged.connect(self.combo_box_changed)
        self.main_layout.addWidget(self.object_name_field, 1, 2, 1, 3)

        self.ID_object_label = QLabel("Enter ID object")
        self.main_layout.addWidget(self.ID_object_label, 2, 1, 1, 1)

        self.ID_object_field = QSpinBox()
        self.ID_object_field.setMaximum(999999999)
        self.main_layout.addWidget(self.ID_object_field, 2, 2, 1, 3)

        self.select_mode_label = QLabel('Select mode')
        self.main_layout.addWidget(self.select_mode_label, 5, 1, 1, 1)

        self.draw_radio_button = QRadioButton("Draw Mode")
        self.draw_radio_button.setChecked(True)
        self.draw_radio_button.clicked.connect(self.disable_enter_coordinate)
        self.main_layout.addWidget(self.draw_radio_button, 5, 2, 1, 1)

        self.enter_coordinates_button = QRadioButton("Enter coordinate mode")
        self.enter_coordinates_button.clicked.connect(self.enable_enter_coordinate)
        self.main_layout.addWidget(self.enter_coordinates_button, 5, 3, 1, 1)

        self.startpoint_label = QLabel("Check Area")
        self.main_layout.addWidget(self.startpoint_label, 6, 1, 1, 1)

        self.x1_coordinates_label = QLabel("X1")
        self.main_layout.addWidget(self.x1_coordinates_label, 7, 1, 1, 1)

        self.x1_coordinates_field = QSpinBox()
        self.x1_coordinates_field.setMaximum(999999999)
        self.main_layout.addWidget(self.x1_coordinates_field, 7, 2, 1, 1)

        self. y1_coordinates_label = QLabel("                 Y1")
        self.main_layout.addWidget(self.y1_coordinates_label, 7, 3, 1, 1)

        self.y1_coordinates_field = QSpinBox()
        self.y1_coordinates_field.setMaximum(999999999)
        self.main_layout.addWidget(self.y1_coordinates_field, 7, 4, 1, 1)

        self.x2_coordinates_label = QLabel('X2')
        self.main_layout.addWidget(self.x2_coordinates_label, 8, 1, 1, 1)

        self.x2_coordinates_field = QSpinBox()
        self.x2_coordinates_field.setMaximum(999999999)
        self.main_layout.addWidget(self.x2_coordinates_field, 8, 2, 1, 1)

        self.y2_coordinates_label = QLabel("                 Y2")
        self.main_layout.addWidget(self.y2_coordinates_label, 8, 3, 1, 1)

        self.y2_coordinates_field = QSpinBox()
        self.y2_coordinates_field.setMaximum(999999999)
        self.main_layout.addWidget(self.y2_coordinates_field, 8, 4, 1, 1)

        self.select_area_button = QPushButton("Select area")
        self.main_layout.addWidget(self.select_area_button, 12, 1, 1, 1)
        self.select_area_button.clicked.connect(self.select_area)


        self.button = QPushButton("OK")
        self.main_layout.addWidget(self.button, 13, 1, 1, 1)
        self.button.clicked.connect(self.on_button_click)
        # self.button.clicked.connect(self.accept)

        # Kết nối tín hiệu của nút bấm

        self.x1_coordinates_field.setEnabled(False)
        self.y1_coordinates_field.setEnabled(False)
        self.x2_coordinates_field.setEnabled(False)
        self.y2_coordinates_field.setEnabled(False)

        self.select_area_button.setEnabled(True)

        self.selected_item = self.object_name_field.itemText(0)
        self.position = 0

        self.setLayout(self.main_layout)

        self.setWindowTitle("Detect Module Edit")
        self.resize(400, 200)

    def combo_box_changed(self, index):
        self.selected_item = self.object_name_field.itemText(index)
        self.position = self.items.index(self.selected_item)
        self.ID_object_field.setValue(self.position)

    def enable_enter_coordinate(self):
            self.x1_coordinates_field.setEnabled(True)
            self.y1_coordinates_field.setEnabled(True)
            self.x2_coordinates_field.setEnabled(True)
            self.y2_coordinates_field.setEnabled(True)
            self.select_area_button.setEnabled(False)
    def disable_enter_coordinate(self):
            self.x1_coordinates_field.setEnabled(False)
            self.y1_coordinates_field.setEnabled(False)
            self.x2_coordinates_field.setEnabled(False)
            self.y2_coordinates_field.setEnabled(False)
            self.select_area_button.setEnabled(True)

    def select_area(self):
        print('-----------------------------------------')
        print('self.selected_item = ', self.selected_item)
        print('self.position = ', self.position)
        self.conn = sqlite3.connect('database.db')
        self.cursor = self.conn.cursor()
        self.cursor.execute("UPDATE commands SET object_name = ?, object_id = ? WHERE selected = 'ON'", (self.selected_item, self.position))
        self.conn.commit()
        program_path = os.path.join("labelImg_master", "labelImg.py")
        os.system(f"python {program_path}")

    def on_button_click(self):
        QMessageBox.information(self, "Success", "Data saved successfully!")
        self.accept()
        self.conn = sqlite3.connect('database.db')
        self.cursor = self.conn.cursor()
        self.cursor.execute(f"UPDATE commands SET selected = 'OFF' WHERE selected = 'ON'")
        self.conn.commit()


