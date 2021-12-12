import sys
import sqlite3
from PyQt5 import QtWidgets
from PyQt5.QtCore import Qt, QRect
from PyQt5.QtWidgets import QDialog, QApplication, QMessageBox
from PyQt5.uic import loadUi

con = sqlite3.connect('passwords.s3db')
cur = con.cursor()
cur.execute("CREATE TABLE IF NOT EXISTS passwords (name text, login text, password text)")


class SearchLine(QtWidgets.QLineEdit):
    """Reinterpretation of class QLineEdit
    to add special behaviour on focus event
    to make better search text field
    """
    def focusInEvent(self, event):
        """QLineEdit behaviour on focusInEvent overwritten
        """
        if self.text() == "Type something to search...":
            self.clear()
        super().focusInEvent(event)

    def focusOutEvent(self, event):
        """QLineEdit behaviour on focusOutEvent overwritten
        """
        if not self.text():
            self.setText("Type something to search...")
        super().focusOutEvent(event)


class MainScreen(QDialog):
    """Class that owns main screen UI
    """
    def __init__(self):
        super().__init__()
        loadUi('UI/main_screen.ui', self)
        self.add_button.clicked.connect(self.add_password)
        self.show_button.clicked.connect(self.go_to_show_passwords)
        self.password_text.setEchoMode(QtWidgets.QLineEdit.Password)

    def add_password(self):
        """Function that adds password data to db.
        """
        cur.execute("INSERT INTO passwords(name, login, password) VALUES(?, ?, ?)",
                    (self.name_text.text(), self.login_text.text(), self.password_text.text()))
        self.name_text.clear()
        self.login_text.clear()
        self.password_text.clear()
        con.commit()
        QMessageBox.information(self, 'Success!', "Successfully added!", QMessageBox.Ok)

    def go_to_show_passwords(self):
        """Fuction that changes screen
        """
        show_screen = PasswordListScreen()
        widget.addWidget(show_screen)
        widget.setCurrentIndex(widget.currentIndex() + 1)
        widget.setFixedHeight(410)
        widget.setFixedWidth(630)


class PasswordListScreen(QDialog):
    """Class that own showing passwords screen
    """
    def __init__(self):
        super().__init__()
        loadUi('UI/show_screen.ui', self)
        self.tableWidget.setColumnWidth(0, 210)     # increase
        self.tableWidget.setColumnWidth(1, 210)     # columns
        self.tableWidget.setColumnWidth(2, 210)     # size
        self.table_w = []   # variable which store table widgets to allow us edit flags like: Qt.ItemIsEditable etc.
        self.edited_data = []   # variable which store edited date which wasn't yet added to database
        self.all_data = []  # variable which store the actual data
        self.edit_on = False    # flag to tell it Edit mode is on
        self.search_text = SearchLine(self)                     # making
        self.search_text.setObjectName(u"search_text")          # a magic search LineEdit
        self.search_text.setGeometry(QRect(70, 280, 521, 21))   # from a my own class that inherit from QLineEdit class
        self.search_text.setText("Type something to search...")
        self.edit_button.clicked.connect(self.edit)
        self.add_button.clicked.connect(self.add)
        self.remove_button.clicked.connect(self.remove)
        self.search_text.textEdited.connect(self.search)
        self.s_by_login_checkbox.stateChanged.connect(self.checked)
        self.s_by_password_checkbox.stateChanged.connect(self.checked)
        self.load_data_to_table()

    def load_data_to_table(self):
        """Function that loading data from the db,
        next making tableWidgetsItems from it and adds them to
        table_w[list] and set flags to allow only select
        and finally it adds all Items to the TableWidget
        """
        cur.execute("select * from passwords")
        self.all_data = cur.fetchall()
        self.tableWidget.setRowCount(len(self.all_data))

        i = 0

        for row in self.all_data:
            self.table_w.append((QtWidgets.QTableWidgetItem(row[0]), QtWidgets.QTableWidgetItem(row[1]),
                                 QtWidgets.QTableWidgetItem(row[2])))
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
        self.tableWidget.verticalHeader().hide()
        self.tableWidget.horizontalHeader().setStyleSheet("QHeaderView::section { background-color: blue; font: 87 12pt \"Inconsolata Condensed Black\"; }");

    def edit(self):
        """functions that edits data and update the db
        """
        if not self.all_data:
            return
        if not self.edit_on:
            for i in range(len(self.table_w)):
                self.table_w[i][0].setFlags(self.table_w[i][0].flags() | Qt.ItemIsEditable)
                self.table_w[i][1].setFlags(self.table_w[i][1].flags() | Qt.ItemIsEditable)
                self.table_w[i][2].setFlags(self.table_w[i][2].flags() | Qt.ItemIsEditable)
            self.edit_on = True
            self.edit_button.setText("Done")
            self.all_data.clear()
            for i in range(len(self.table_w)):
                self.all_data.append((self.table_w[i][0].text(), self.table_w[i][1].text(),
                                         self.table_w[i][2].text()))
        else:
            for i in range(len(self.table_w)):
                self.table_w[i][0].setFlags(self.table_w[i][0].flags() & ~ Qt.ItemIsEditable)
                self.table_w[i][1].setFlags(self.table_w[i][1].flags() & ~ Qt.ItemIsEditable)
                self.table_w[i][2].setFlags(self.table_w[i][2].flags() & ~ Qt.ItemIsEditable)
                self.edited_data.append((self.table_w[i][0].text(), self.table_w[i][1].text(),
                                         self.table_w[i][2].text()))
                if self.all_data[i][0] != self.edited_data[i][0] or self.all_data[i][1] != self.edited_data[i][1] or self.all_data[i][2] != self.edited_data[i][2]:
                    cur.execute("UPDATE passwords SET name = ?, login = ?, password = ? WHERE name = ? and login = ? and password = ?",(self.edited_data[i][0],  self.edited_data[i][1], self.edited_data[i][2], self.all_data[i][0], self.all_data[i][1], self.all_data[i][2]))
                    con.commit()
            cur.execute("SELECT * FROM passwords")
            self.all_data = cur.fetchall()
            self.edited_data = []
            self.edit_on = False
            self.edit_button.setText("Edit")

    def search(self):
        """Function that clears tableWidget items,
        searchs data in all_data[list], and appends
        to the tableWidget items matching results.
        """
        self.tableWidget.clear()
        self.tableWidget.setRowCount(0)
        z = 0
        if self.s_by_login_checkbox.isChecked():
            search_mode = 1
        elif self.s_by_password_checkbox.isChecked():
            search_mode = 2
        else:
            search_mode = 0
        self.table_w = []
        for i in self.all_data:
            if i[search_mode][:len(self.search_text.text())] == self.search_text.text():
                self.table_w.append((QtWidgets.QTableWidgetItem(i[0]), QtWidgets.QTableWidgetItem(i[1]),
                                     QtWidgets.QTableWidgetItem(i[2])))
                self.tableWidget.insertRow(self.tableWidget.rowCount())
                self.tableWidget.setItem(z, 0, self.table_w[z][0])
                self.tableWidget.setItem(z, 1, self.table_w[z][1])
                self.tableWidget.setItem(z, 2, self.table_w[z][2])
                z += 1
        self.tableWidget.setHorizontalHeaderLabels("Name;Login;Password".split(";"))


    def checked(self):
        """Simple Function that blocks unchecked checkBox
        when one of two is checked and unblocks all checkBoxes
        when no one is checked.
        """
        if self.s_by_password_checkbox.isChecked():
            self.s_by_login_checkbox.setEnabled(False)
        elif self.s_by_login_checkbox.isChecked():
            self.s_by_password_checkbox.setEnabled(False)
        else:
            self.s_by_password_checkbox.setEnabled(True)
            self.s_by_login_checkbox.setEnabled(True)

    def remove(self):
        if self.edit_on or not self.all_data:
            return

        rows = set()
        """Function that remove data from db and form tableWidget
        """
        for item in self.tableWidget.selectedItems():
            row = item.row()
            rows.add(row)
            cur.execute("DELETE FROM passwords WHERE name = ? and login = ? and password = ? ", (self.table_w[row][0].text(), self.table_w[row][1].text(), self.table_w[row][2].text()))
        for r in rows:
            self.tableWidget.removeRow(row)
        con.commit()
        cur.execute("SELECT * FROM passwords")
        self.all_data = cur.fetchall()

    def add(self):
        """Will be a functions that allows to add data from show passwords screen,
        but now it only backs to the main screen(or maybe it can stay like this
        it's not bad i think)
        """
        widget.removeWidget(self)
        widget.setFixedHeight(280)
        widget.setFixedWidth(380)


app = QApplication(sys.argv)
app.setStyleSheet("QLineEdit {background-color: rgba(0, 0, 0, 0); font: 87 12pt \"Inconsolata Condensed Black\";; }"
                  "QTableWidgetItem {background-color: rgba(0, 0, 0, 0);;;}"
                  "QWidget#Password_manager{background-color: qlineargradient(spread:pad, x1:0, y1:0, x2:1, y2:1, stop:0 rgba(64, 83, 255, 255), stop:1 rgba(179, 199, 255, 255));}"
                  "QWidget#show_passowrds{ background-color: qlineargradient(spread:pad, x1:0, y1:0, x2:1, y2:1, stop:0 rgba(64, 83, 255, 255), stop:1 rgba(179, 199, 255, 255));}"
                  "QPushButton {background-color: qlineargradient(spread:pad, x1:0, y1:0, x2:1, y2:1, stop:0 rgba(255, 0, 0, 255), stop:1 rgba(85, 85, 255, 255));}"
                  "QCheckBox {color: qlineargradient(spread:pad, x1:0, y1:0, x2:1, y2:1, stop:0 rgba(255, 0, 0, 255), stop:1 rgba(85, 85, 255, 255));}")

main_screen = MainScreen()
widget = QtWidgets.QStackedWidget()
widget.addWidget(main_screen)
widget.setFixedHeight(280)
widget.setFixedWidth(380)
widget.show()
sys.exit(app.exec())
