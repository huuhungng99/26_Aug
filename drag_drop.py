import sys, copy

from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
import sqlite3

from detect_object_window import detect_func

class MyClassA(object):
    def __init__(self):
        super(MyClassA, self).__init__()

class MyClassB(object):
    def __init__(self):
        super(MyClassB, self).__init__()
        self.DataObjectCopy = None

class ThumbListWidget(QListWidget):
    _drag_info = []
    dropped = pyqtSignal(list)

    def __init__(self, type, name, parent=None):
        super(ThumbListWidget, self).__init__(parent)
        self.setObjectName(name)
        self.setIconSize(QSize(124, 124))
        self.setDragDropMode(QAbstractItemView.DragDrop)
        self.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self.setAcceptDrops(True)
        self._dropping = False

    def startDrag(self, actions):
        self._drag_info[:] = [str(self.objectName())]
        for item in self.selectedItems():
            self._drag_info.append(self.row(item))
        super(ThumbListWidget, self).startDrag(actions)

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            event.accept()
        else:
            super(ThumbListWidget, self).dragEnterEvent(event)

    def dragMoveEvent(self, event):
        if event.mimeData().hasUrls():
            event.setDropAction(Qt.CopyAction)
            event.accept()
        else:
            super(ThumbListWidget, self).dragMoveEvent(event)

    def dropEvent(self, event):
        if event.mimeData().hasUrls():
            event.setDropAction(Qt.CopyAction)
            event.accept()
            links = []
            for url in event.mimeData().urls():
                links.append(str(url.toLocalFile()))
            self.dropped.emit(links)
        else:
            self._dropping = True
            super(ThumbListWidget, self).dropEvent(event)
            self._dropping = False

    def rowsInserted(self, parent, start, end):
        if self._dropping:
            self._drag_info.append((start, end))
            self.dropped.emit(self._drag_info)
        super(ThumbListWidget, self).rowsInserted(parent, start, end)

class Dialog_01(QWidget):  # Đã thay đổi từ QMainWindow thành QWidget
    def __init__(self):
        super(Dialog_01, self).__init__()
        self.listItems = {}

        myBoxLayout = QHBoxLayout(self)  # Gán layout trực tiếp cho QWidget

        self.listWidgetA = ThumbListWidget(self, 'MainTree')
        self.listWidgetB = ThumbListWidget(self, 'SecondaryTree')
        self.listWidgetB.setDragDropMode(QAbstractItemView.DropOnly)
        self.listWidgetA.setDragEnabled(True)
        self.listWidgetA.setAcceptDrops(False)
        self.listWidgetB.setDragEnabled(False)
        self.listWidgetB.setAcceptDrops(True)

        command = ['Check module', 'Start cycle', 'Start - Stop point']

        for i in range(len(command)):
            listItemA = QListWidgetItem()
            listItemA.setText(command[i])
            self.listWidgetA.addItem(listItemA)

            myClassInstA = MyClassA()
            listItemA.setData(Qt.UserRole, myClassInstA)

            listItemB = QListWidgetItem()
            myClassInstB = MyClassB()
            listItemB.setData(Qt.UserRole, myClassInstB)

        myBoxLayout.addWidget(self.listWidgetA)
        myBoxLayout.addWidget(self.listWidgetB)

        # Thêm event handler cho click chuột phải vào icon
        self.listWidgetB.setContextMenuPolicy(Qt.CustomContextMenu)
        self.listWidgetB.customContextMenuRequested.connect(self.show_context_menu2)

        self.listWidgetB.dropped.connect(self.droppedOnB)
        self.listWidgetB.itemClicked.connect(self.itemClicked)

        self.conn = sqlite3.connect('database.db')
        self.cursor = self.conn.cursor()
        self.cursor.execute("""CREATE TABLE IF NOT EXISTS commands(
                  id INTEGER PRIMARY KEY,
                  name TEXT,
                  line TEXT,
                  command_code INTEGER,
                  object_name TEXT,
                  object_id INTEGER,
                  xcen FLOAT,
                  ycen FLOAT,
                  width FLOAT,
                  height FLOAT,
                  x1 FLOAT,
                  y1 FLOAT,
                  x2 FLOAT,
                  y2 FLOAT,
                  selected)""")
        self.conn.commit()

    def normalize_string(self,s):
        s = s.strip()
        s = ' '.join(s.split())
        return s
    def droppedOnB(self, dropped_list):
        if not dropped_list or len(dropped_list) < 3:
            return

        srcIndexes = dropped_list[1:-1]
        destIndexes = dropped_list[-1]

        itemsIndxes = []
        i = 0
        for num in range(destIndexes[0], destIndexes[-1] + 1):
            itemsIndxes.append((srcIndexes[i], num))
            i += 1

        for indexSet in itemsIndxes:
            srcNum = indexSet[0]
            destIndxNum = indexSet[-1]

            srcItem = self.listWidgetA.item(srcNum)
            if not srcItem:
                continue
            srcItemData = srcItem.data(Qt.UserRole)
            if not srcItemData:
                continue
            srcItemDataObject = srcItemData

            itemDataObject_copy = copy.deepcopy(srcItemDataObject)

            droppedItem = self.listWidgetB.item(destIndxNum)
            droppedItem.setHidden(True)

            newItemName = srcItem.text()
            #Kiem tra ten da ton tai hay chua
            names = {self.listWidgetB.item(i).text() for i in range(self.listWidgetB.count())}
            # names = self.normalize_string(name)
            # print('names = ', names)

            count_list = []
            item_listA = []
            for i in range(self.listWidgetA.count()):
                count_list.append(0)
                item = self.listWidgetA.item(i).text()
                if item.startswith('Start cycle'):
                    item = ' ' * 4 + item
                if item.startswith('Start - Stop point'):
                    item = ' ' * 8 + item
                item_listA.append(item)
            #print('item_listA = ', item_listA)

            if newItemName in names:
                #print('names = ', names)
                # Neu tim thay thi kiem tra xem phan tu nao trung nhau
                for i in range (len(item_listA[i])):
                    if newItemName == self.listWidgetA.item(i).text():
                        #print('dieu kien true')
                        #print('count_list = ', count_list)
                        #count_list[i] = sum(1 for item in names if item.startswith(self.listWidgetA.item(i).text()))
                        count_list[i] = sum(1 for item in names if item.startswith(item_listA[i]))
                        #print('count_list_sau_xu_ly = ', count_list)
                        newItemName = newItemName + '(' + str(count_list[i]) + ')'
                        #print('newItemName2 = ', newItemName)
                        break

            if newItemName.startswith('Start cycle'):
                #print('-------------------')
                newItemName = ' '*4 +  newItemName
                #print('newItemName = ', newItemName)
            if newItemName.startswith('Start - Stop point'):
                newItemName = ' '*8 + newItemName
                #print('newItemName = ', newItemName)

            myClassInstB = MyClassB()
            myClassInstB.DataObjectCopy = itemDataObject_copy

            newListItem = QListWidgetItem()
            newListItem.setData(Qt.UserRole, myClassInstB)

            newListItem.setText(newItemName)
            self.listWidgetB.blockSignals(True)
            self.listWidgetB.addItem(newListItem)
            self.listWidgetB.blockSignals(False)

        self.conn = sqlite3.connect('database.db')
        self.cursor = self.conn.cursor()
        self.cursor.execute("DELETE FROM commands")

        for i in range(self.listWidgetB.count()):
            item = self.listWidgetB.item(i)
            if item.isHidden():
                continue
            itemText = item.text()
            itemDataObject = item.data(Qt.UserRole)
            if itemText.startswith('    '):
                command_code = 1001
            elif itemText.startswith('        '):
                command_code = 1002
            else:
                command_code = 1000
            self.cursor.execute("INSERT INTO commands (name, line, command_code) VALUES (?, ?, ?)",
                                (itemText, i, command_code))
            #print(f"Item {i}: {itemText}")
        self.conn.commit()

    def show_context_menu2(self, pos):
        if self.sender() == self.listWidgetA:
            listwidget = self.listWidgetA
        else:
            listwidget = self.listWidgetB

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

    def delete_item_from_listwidget2(self):
        seleted_item = self.listWidgetB.currentItem()
        row = self.listWidgetB.row(seleted_item)
        self.listWidgetB.takeItem(row)

        # Cap nhat lai toan bo database
        self.conn = sqlite3.connect('database.db')
        self.cursor = self.conn.cursor()
        self.cursor.execute("DELETE FROM commands")
        for i in range(self.listWidgetB.count()):
            item = self.listWidgetB.item(i)
            if item.isHidden():
                continue
            itemText = item.text()
            itemDataObject = item.data(Qt.UserRole)
            if itemText.startswith('    '):
                command_code = 1001
            elif itemText.startswith('        '):
                command_code = 1002
            else:
                command_code = 1000
            self.cursor.execute("INSERT INTO commands (name, line, command_code) VALUES (?, ?, ?)",
                                (itemText, i, command_code))
        self.conn.commit()

    def rename_item_in_list(self):
        selected_item = self.listWidgetB.currentItem()
        selectedIndex = self.listWidgetB.row(selected_item)
        print('selectedIndex = ', selectedIndex)
        add = ''
        if selected_item.text().startswith('    '):
            add = '    '
        if selected_item.text().startswith('        '):
            add = '        '
        names = {self.listWidgetB.item(i).text() for i in range(self.listWidgetB.count())}
        #print('names = ', names)
        new_name, ok = QInputDialog.getText(self, "Rename Item", "Enter new name (Name must not be used before): ")
        new_name = add + new_name
        while new_name in names or new_name == '    ' or new_name == '        ':
            new_name, ok = QInputDialog.getText(self, "Rename Item", "Enter new name (Name must not be used before): ")
            new_name = add + new_name
        selected_item.setText(new_name)

        #Cap nhat ten vao database
        self.conn = sqlite3.connect('database.db')
        self.cursor = self.conn.cursor()
        self.cursor.execute(f"UPDATE commands SET name = '{new_name}' WHERE line = {selectedIndex}")
        self.conn.commit()
    def itemClicked(self, item):
        dataObject = item.data(Qt.UserRole)
        #print('itemClicked(): instance type:', type(dataObject))

    def open_new_window(self, item):
        selected_item = self.listWidgetB.currentItem()
        selectedIndex = self.listWidgetB.row(selected_item)

        #Cap nhat bien selected trong database
        self.conn = sqlite3.connect('database.db')
        self.cursor = self.conn.cursor()
        self.cursor.execute(f"UPDATE commands SET selected = 'ON' WHERE line = {selectedIndex}")
        self.conn.commit()
        self.new_window = detect_func()
        self.new_window.show()

# if __name__ == '__main__':
#     app = QApplication(sys.argv)
#     dialog_1 = Dialog_01()
#     dialog_1.show()
#     dialog_1.resize(720, 480)
#     sys.exit(app.exec_())
