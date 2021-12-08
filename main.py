import sys
import sqlite3
from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QDialog, QApplication, QMessageBox
from PyQt5.uic import loadUi

con = sqlite3.connect('passwords.s3db')
cur = con.cursor()
cur.execute("CREATE TABLE IF NOT EXISTS passwords (login text, password text)")

class MainScreen(QDialog):
    def __init__(self):
        super().__init__()
        loadUi('UI/main_screen.ui', self)
        self.Add_button.clicked.connect(self.add_password)

    def add_password(self):
        cur.execute("INSERT INTO passwords(login, password) VALUES(?, ?)", (self.login_text.text(), self.password_text.text()))
        con.commit()
        QMessageBox.information(self, 'Success!', "Successfully added!", QMessageBox.Ok)

class PasswordListScreen(QDialog):
    pass    # screen which contains exisiting passwords to add

app = QApplication(sys.argv)
main_screen = MainScreen()
widget = QtWidgets.QStackedWidget()
widget.addWidget(main_screen)
widget.setFixedHeight(280)
widget.setFixedWidth(380)
widget.show()
sys.exit(app.exec())