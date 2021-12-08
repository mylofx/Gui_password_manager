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
        self.table_w = []
        self.edited_data = []
        self.all_data = []
        self.edit_on = False
        self.load_data_to_table()
        self.edit_button.clicked.connect(self.edit)

    def load_data_to_table(self):
        cur.execute("select * from passwords")
        self.all_data = cur.fetchall()
        self.tableWidget.setRowCount(len(self.all_data))
        i = 0

        for row in self.all_data:
            self.table_w.append((QtWidgets.QTableWidgetItem(row[0]), QtWidgets.QTableWidgetItem(row[1]), QtWidgets.QTableWidgetItem(row[2])))
            self.tableWidget.setItem(i, 0, self.table_w[i][0])
            self.table_w[i][0].setFlags(self.table_w[i][0].flags() | Qt.ItemIsSelectable)
            self.table_w[i][0].setFlags(self.table_w[i][0].flags() & ~ Qt.ItemIsEditable)
            self.tableWidget.setItem(i, 1, self.table_w[i][1])
            self.table_w[i][1].setFlags(self.table_w[i][1].flags() | Qt.ItemIsSelectable)
            self.table_w[i][1].setFlags(self.table_w[i][1].flags() & ~ Qt.ItemIsEditable)
            self.tableWidget.setItem(i, 2, self.table_w[i][2])
            self.table_w[i][2].setFlags(self.table_w[i][2].flags() | Qt.ItemIsSelectable)
            self.table_w[i][2].setFlags(self.table_w[i][2].flags() & ~ Qt.ItemIsEditable)
            i += 1

    def edit(self):
        if not self.edit_on:
            for i in range(len(self.table_w)):
                self.table_w[i][0].setFlags(self.table_w[i][0].flags() | Qt.ItemIsEditable)
                self.table_w[i][1].setFlags(self.table_w[i][1].flags() | Qt.ItemIsEditable)
                self.table_w[i][2].setFlags(self.table_w[i][2].flags() | Qt.ItemIsEditable)
            self.edit_on = True
            self.edit_button.setText("Done")
        else:
            for i in range(len(self.table_w)):
                self.table_w[i][0].setFlags(self.table_w[i][0].flags() & ~ Qt.ItemIsEditable)
                self.table_w[i][1].setFlags(self.table_w[i][1].flags() & ~ Qt.ItemIsEditable)
                self.table_w[i][2].setFlags(self.table_w[i][2].flags() & ~ Qt.ItemIsEditable)
                self.edited_data.append((self.table_w[i][0].text(), self.table_w[i][1].text(), self.table_w[i][2].text()))
                if self.all_data[i][0] != self.edited_data[i][0] or self.all_data[i][1] != self.edited_data[i][1] or self.all_data[i][2] != self.edited_data[i][2]:
                    cur.execute("UPDATE passwords SET name = ?, login = ?, password = ? WHERE name = ? and login = ? and password = ?", (self.edited_data[i][0],  self.edited_data[i][1], self.edited_data[i][2], self.all_data[i][0], self.all_data[i][1], self.all_data[i][2]))
                    con.commit()
                    con.close()
            self.all_data = self.edited_data
            self.edited_data = []
            self.edit_on = False
            self.edit_button.setText("Edit")

        def search():
            pass


app = QApplication(sys.argv)
main_screen = MainScreen()
widget = QtWidgets.QStackedWidget()
widget.addWidget(main_screen)
widget.setFixedHeight(280)
widget.setFixedWidth(380)
widget.show()
sys.exit(app.exec())