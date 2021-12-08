import sys
import sqlite3
from PyQt5 import QtWidgets
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QDialog, QApplication, QMessageBox
from PyQt5.uic import loadUi

con = sqlite3.connect('passwords.s3db')
cur = con.cursor()
cur.execute("CREATE TABLE IF NOT EXISTS passwords (name text, login text, password text)")

class MainScreen(QDialog):
    def __init__(self):
        super().__init__()
        loadUi('UI/main_screen.ui', self)
        self.add_button.clicked.connect(self.add_password)
        self.show_button.clicked.connect(self.go_to_show_passwords)

    def add_password(self):
        cur.execute("INSERT INTO passwords(name, login, password) VALUES(?, ?, ?)", (self.name_text.text(), self.login_text.text(), self.password_text.text()))
        self.name_text.clear()
        self.login_text.clear()
        self.password_text.clear()
        con.commit()
        QMessageBox.information(self, 'Success!', "Successfully added!", QMessageBox.Ok)

    def go_to_show_passwords(self):
        show_screen = PasswordListScreen()
        widget.addWidget(show_screen)
        widget.setCurrentIndex(widget.currentIndex() + 1)
        widget.setFixedHeight(410)
        widget.setFixedWidth(630)


class PasswordListScreen(QDialog):
    def __init__(self):
        super().__init__()
        loadUi('UI/show_screen.ui', self)
        self.tableWidget.setColumnWidth(0, 200)
        self.tableWidget.setColumnWidth(1, 200)
        self.tableWidget.setColumnWidth(2, 200)
        self.load_data_to_table()

    def load_data_to_table(self):
        cur.execute("select * from passwords")
        all_data = cur.fetchall()
        self.tableWidget.setRowCount(len(all_data))
        i = 0
        table_w = []
        for row in all_data:
            table_w.append((QtWidgets.QTableWidgetItem(row[0]), QtWidgets.QTableWidgetItem(row[1]), QtWidgets.QTableWidgetItem(row[2])))
            self.tableWidget.setItem(i, 0, table_w[i][0])
            table_w[i][0].setFlags(Qt.ItemIsSelectable)
            self.tableWidget.setItem(i, 1, table_w[i][1])
            table_w[i][1].setFlags(Qt.ItemIsSelectable)
            self.tableWidget.setItem(i, 2, table_w[i][2])
            table_w[i][2].setFlags(Qt.ItemIsSelectable)
            i += 1

app = QApplication(sys.argv)
main_screen = MainScreen()
widget = QtWidgets.QStackedWidget()
widget.addWidget(main_screen)
widget.setFixedHeight(280)
widget.setFixedWidth(380)
widget.show()
sys.exit(app.exec())