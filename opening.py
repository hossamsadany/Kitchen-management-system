from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QLineEdit, QPushButton, QDialog, QMessageBox, QInputDialog
from PyQt5.QtGui import QIcon, QPainter, QPalette, QBrush, QImage, QColor
from PyQt5.QtCore import Qt, QRect
import sqlite3
from operations import OperationWindow
import sys




class LoginWindow(QWidget):
    def __init__(self):
        super(LoginWindow, self).__init__()
        

        # set window properties
        self.setWindowTitle("Restaurant Management System")
        self.setWindowIcon(QIcon("Images/icon.png"))
        self.sub_window = OperationWindow()
        
        # set background image
        palette = QPalette()
        palette.setBrush(QPalette.Background, QBrush(QImage("Images/food.png")))
        self.setPalette(palette)

        # create a label for the title
        title_label, username_label , password_label = QLabel(self), QLabel(self), QLabel(self)
        title_label.setText("Kitchen Management System")
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setGeometry(QRect(400, 200, 600, 100))
        
        title_label.setStyleSheet("background-color: rgba(0, 0, 0, 0); font-size: 32px; color: white; font-weight: bold;")
        
        # create username and password labels and line edits
        username_label.setText("Username:")
        username_label.setGeometry(QRect(450, 330, 110, 30))
        username_label.setStyleSheet("background-color: rgba(0, 0, 0, 0); font-size: 20px;; color: white; font-weight: bold;")

        self.username_edit, self.password_edit = QLineEdit(self), QLineEdit(self)
        self.username_edit.setGeometry(QRect(600, 330, 200, 30))
        self.username_edit.setStyleSheet("background-color: white; font-size: 20px;")

        password_label.setText("Password:")
        password_label.setGeometry(QRect(450, 380, 110, 30))
        password_label.setStyleSheet("background-color: rgba(0, 0, 0, 0); font-size: 20px;; color: white; font-weight: bold;")

        self.password_edit.setGeometry(QRect(600, 380, 200, 30))
        self.password_edit.setStyleSheet("background-color: white; font-size: 20px;")
        self.password_edit.setEchoMode(QLineEdit.Password)

        # create login and sign up buttons
        login_button , signup_button = QPushButton("Login", self), QPushButton("Sign Up", self)
        login_button.setGeometry(QRect(600, 450, 200, 50))
        login_button.setStyleSheet("background-color: white; font-size: 20px;")
        login_button.clicked.connect(self.login)
        self.password_edit.returnPressed.connect(login_button.click)

        signup_button.setGeometry(QRect(600, 520, 200, 50))
        signup_button.setStyleSheet("background-color: white; font-size: 20px;")
        signup_button.clicked.connect(self.signup)
    
    def paintEvent(self, event):
        # draw a semi-transparent overlay over the background image
        painter = QPainter(self)
        painter.setOpacity(0.5)
        painter.fillRect(self.rect(), QColor(0, 0, 0, 128))
    def connect(self):
        try:
            conn = sqlite3.connect("restaurant_database.db")
            cursor = conn.cursor()
            return conn, cursor
        except sqlite3.Error as error:
            QMessageBox.warning(form, "Warning", error)

    def login(self):
        # connect to the database and retrieve the user's credentials
        conn, cursor = self.connect()
        cursor.execute("SELECT * FROM users WHERE username=? AND password=?",
                    (self.username_edit.text(), self.password_edit.text()))
        user = cursor.fetchone()

        if user:
            # if the user exists, show the operation window and hide the main window
            self.hide()
            self.sub_window.showMaximized()
            self.sub_window.show()
            
            
            
        else:
            # if the user doesn't exist, show an error message
            message_box = QMessageBox()
            message_box.setWindowTitle("Login Error")
            message_box.setIcon(QMessageBox.Warning)
            message_box.setText("Invalid username or password.")
            message_box.setStyleSheet("""
            QMessageBox {
                background-color: black;
                border: 1px solid #8B4513;
                border-radius: 10px;
            }
            QLabel#qt_msgbox_label {
                color: white;
                font-size: 16px;
            }
            QPushButton {
                background-color: #FF4500;
                color: white;
                padding: 5px 10px;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #FF6347;
            }
        """)
            message_box.exec_()

        # close the database connection
        conn.close()

    def signup(self):
        # create a new window for the sign up form
        signup_window = QDialog(self)
        signup_window.setWindowTitle("Sign Up")
        signup_window.setFixedSize(600, 300)

        # create labels and line edits for the sign up form
        username_label, username_edit, password_label, password_edit = QLabel(signup_window), QLineEdit(signup_window), QLabel(signup_window), QLineEdit(signup_window)
        username_label.setText("Username:")
        username_label.setGeometry(QRect(50, 50, 100, 30))
        username_label.setStyleSheet("font-size: 20px;")

        username_edit.setGeometry(QRect(300, 50, 200, 30))
        username_edit.setStyleSheet("font-size: 20px;")

        password_label.setText("Password:")
        password_label.setGeometry(QRect(50, 100, 100, 30))
        password_label.setStyleSheet("font-size: 20px;")

        password_edit.setGeometry(QRect(300, 100, 200, 30))
        password_edit.setStyleSheet("font-size: 20px;")
        password_edit.setEchoMode(QLineEdit.Password)

        confirm_label = QLabel(signup_window)
        confirm_label.setText("Confirm Password:")
        confirm_label.setGeometry(QRect(50, 150, 200, 30))
        confirm_label.setStyleSheet("font-size: 20px;")

        confirm_edit = QLineEdit(signup_window)
        confirm_edit.setGeometry(QRect(300, 150, 200, 30))
        confirm_edit.setStyleSheet("font-size: 20px;")
        confirm_edit.setEchoMode(QLineEdit.Password)

        # create a button to submit the form
        submit_button = QPushButton("Submit", signup_window)
        submit_button.setGeometry(QRect(300, 220, 100, 50))
        submit_button.setStyleSheet("font-size: 20px;")
        submit_button.clicked.connect(lambda: self.create_user(username_edit.text().lower(), password_edit.text().lower(),
                                                               confirm_edit.text().lower(), signup_window))

        # show the sign up window
        signup_window.exec_()

    def create_user(self, username, password, confirm_password, signup_window):
        # check if the passwords match
        if password != confirm_password:
            message_box = QMessageBox()
            message_box.setText("Passwords do not match.")
            message_box.exec_()
            return

        # connect to the database and check if the username is available
        conn , cursor = self.connect()
        cursor.execute("SELECT * FROM users WHERE username=?", (username,))
        existing_user = cursor.fetchone()

        if existing_user:
            message_box = QMessageBox()
            message_box.setText("Username already taken.")
            message_box.exec_()
        else:
            # create a new user in the database
            cursor.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, password))
            conn.commit()

            message_box = QMessageBox()
            message_box.setText("User created successfully.")
            message_box.exec_()

            # clear the form and close the window
            signup_window.close()

        # close the database connection
        conn.close()
    
        conn.close()
        
    def run(self):
        conn, c = self.connect()
        c.execute("SELECT validation, authorization FROM authorization")
        valid, authorization = c.fetchone()

        while True:
            if valid == "YES":
                self.showMaximized()
                self.show()
                break

            authorization_dialog = QInputDialog(self)
            authorization_dialog.setWindowTitle("Take authorization")
            authorization_dialog.setGeometry(500, 300, 300, 100)
            authorization_dialog.setInputMode(QInputDialog.TextInput)
            authorization_dialog.setLabelText("Please enter the authorization Code:")
            authorization_dialog.setTextEchoMode(QLineEdit.Password)
            ok = authorization_dialog.exec_()
            authorization_code = authorization_dialog.textValue()

            if authorization_dialog.result() == QDialog.Rejected:
                msg_box = QMessageBox(self)
                msg_box.setIcon(QMessageBox.Warning)
                msg_box.setWindowTitle("Invalid Authorization Code")
                msg_box.setText("The authorization code is invalid.")
                msg_box.setStandardButtons(QMessageBox.Retry | QMessageBox.Cancel)
                msg_box.setDefaultButton(QMessageBox.Retry)
                result = msg_box.exec_()

                if result == QMessageBox.Cancel:
                    sys.exit()
                else:
                    continue

            if authorization_code == authorization and ok:
                c.execute("UPDATE authorization SET validation = 'YES'")
                conn.commit()
                c.close()
                conn.close()
                self.showMaximized()
                self.show()
                break

            msg_box = QMessageBox(self)
            msg_box.setIcon(QMessageBox.Warning)
            msg_box.setWindowTitle("Invalid Authorization Code")
            msg_box.setText("The authorization code is invalid.")
            msg_box.setStandardButtons(QMessageBox.Retry | QMessageBox.Cancel)
            msg_box.setDefaultButton(QMessageBox.Retry)
            result = msg_box.exec_()

            if result == QMessageBox.Cancel:
                sys.exit()
                        