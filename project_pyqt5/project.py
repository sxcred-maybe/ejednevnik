import sqlite3

from PyQt5.QtWidgets import QWidget, QApplication, QListWidgetItem, QMessageBox
from PyQt5.uic import loadUi
import sys

from PyQt5 import QtCore


class Window(QWidget):
    def __init__(self):
        super(Window, self).__init__()
        loadUi('main.ui', self)
        self.setWindowTitle('Твой ежедневник')
        self.calendarWidget.selectionChanged.connect(self.calendarChanged)
        self.calendarChanged()
        self.saveBttn.clicked.connect(self.save)
        self.addBttn.clicked.connect(self.newTask)
        self.clearBttn.clicked.connect(self.task_deleter)


    def calendarChanged(self):
        # here we can see a work of our debugger
        # he prints into the console which date selected now
        dateSelected = self.calendarWidget.selectedDate().toPyDate()

        print(f'the date was changed')
        print(f'date selected {dateSelected}')

        self.task_updater(dateSelected)

    def task_updater(self, date):
        # it's just an updater which just updates
        self.list_of_tasks.clear()

        db = sqlite3.connect('data.db')
        cursor = db.cursor()

        query = 'SELECT task, completed FROM tasks WHERE date = ?'
        row = (date,)
        results = cursor.execute(query, row).fetchall()

        for result in results:
            item = QListWidgetItem(str(result[0]))
            item.setFlags(item.flags() | QtCore.Qt.ItemIsUserCheckable)
            if result[1] == 'YES':
                item.setCheckState(QtCore.Qt.Checked)
            elif result[1] == 'NO':
                item.setCheckState(QtCore.Qt.Unchecked)
            self.list_of_tasks.addItem(item)

    def save(self):
        # let's save our changes
        db = sqlite3.connect('data.db')
        cursor = db.cursor()
        date = self.calendarWidget.selectedDate().toPyDate()

        for i in range(self.list_of_tasks.count()):
            item = self.list_of_tasks.item(i)
            task = item.text()
            if item.checkState() == QtCore.Qt.Checked:
                query = 'UPDATE tasks SET completed = "YES" WHERE task = ? AND date = ?'
            else:
                query = 'UPDATE tasks SET completed = "NO" WHERE task = ? AND date = ?'
            row = (task, date)
            cursor.execute(query, row)

        db.commit()

        # a little message about it's alright
        messageBox = QMessageBox()

        messageBox.setWindowTitle('Изменения')
        messageBox.setText('Изменения сохранены')
        messageBox.setStandardButtons(QMessageBox.Ok)

        messageBox.exec()

    def newTask(self):
        # wow! I can have some rest today
        db = sqlite3.connect('data.db')
        cursor = db.cursor()

        newTask = str(self.lineEdit.text())
        date = self.calendarWidget.selectedDate().toPyDate()

        query = 'INSERT INTO tasks(task, completed, date) VALUES (?,?,?)'
        row = (newTask, 'NO', date)
        cursor.execute(query, row)
        db.commit()

        self.task_updater(date)
        self.lineEdit.clear()

    def task_deleter(self):
        # we can delete tasks
        db = sqlite3.connect('data.db')
        cursor = db.cursor()
        query = f"""DELETE FROM tasks WHERE date='{self.calendarWidget.selectedDate().toPyDate()}'"""
        cursor.execute(query)
        db.commit()

        self.list_of_tasks.clear()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = Window()
    window.show()
    sys.exit(app.exec())
