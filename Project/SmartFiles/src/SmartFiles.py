'''
Created on 17.05.2010

@author: valexl

Это главный исполняемый модуль программы SmartFiles. 
Нужно запускать именно его, чтобы работать с программой.
'''
from PyQt5 import QtWidgets, QtCore, QtGui
import sys
import InstallUser  # Assuming this is your custom module

class StartWindow(QtWidgets.QWidget):
    switch_user = QtCore.pyqtSignal()
    create_user = QtCore.pyqtSignal(object)
    update_user = QtCore.pyqtSignal(object)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
        self.setup_connections()
        
        try:
            InstallUser.initHomeDir()
        except InstallUser.ExceptionNoUsers as err:
            self.show_error('''Программа запущена в первый раз.
Для работы с программой необходимо зарегистрировать хотя бы одного пользователя.''')
            print(err)

    def setup_ui(self):
        layout = QtWidgets.QVBoxLayout()
        
        # Login section
        login_layout = QtWidgets.QHBoxLayout()
        login_layout.addWidget(QtWidgets.QLabel('Логин:'))
        self.edit_login = QtWidgets.QLineEdit()
        login_layout.addWidget(self.edit_login)
        layout.addLayout(login_layout)
        
        # Password section
        password_layout = QtWidgets.QHBoxLayout()
        password_layout.addWidget(QtWidgets.QLabel('Пароль:'))
        self.edit_password = QtWidgets.QLineEdit()
        self.edit_password.setEchoMode(QtWidgets.QLineEdit.Password)
        password_layout.addWidget(self.edit_password)
        layout.addLayout(password_layout)
        
        # Buttons
        button_layout = QtWidgets.QHBoxLayout()
        self.btn_ok = QtWidgets.QPushButton('Войти')
        self.btn_ok.setDefault(True)
        self.btn_exit = QtWidgets.QPushButton('Выход')
        button_layout.addWidget(self.btn_ok)
        button_layout.addWidget(self.btn_exit)
        layout.addLayout(button_layout)
        
        self.btn_add_user = QtWidgets.QPushButton('Создать пользователя')
        layout.addWidget(self.btn_add_user)
        
        self.setLayout(layout)
        self.main_window = None

    def setup_connections(self):
        self.btn_ok.clicked.connect(self.start_sf)
        self.btn_add_user.clicked.connect(self.create_user_dialog)
        self.btn_exit.clicked.connect(self.close)

    def start_sf(self):
        """Authenticate user and start main application"""
        try:
            user_name = self.edit_login.text()
            password = hash(self.edit_password.text())
            user_repo = InstallUser.identificationUser(user_name, password)
            self.start_main_window(user_repo)
            self.edit_password.clear()
        except InstallUser.ExceptionUserNotFound:
            self.show_error('Ошибка логина или пароля')
        except InstallUser.ExceptionRepoIsNull:
            self.show_error('''Не найдено ни одного пользователя в системе.
Необходимо создать пользователя''')
        except Exception as err:
            self.show_error('Неизвестная ошибка')
            print(err)

    def create_user_dialog(self):
        """Open user creation dialog"""
        try:
            edit_window = EditUserWindow()
            edit_window.createUser.connect(self.save_user)
            edit_window.show()
        except Exception as err:
            print(err)

    def save_user(self, user_repo):
        """Save new user"""
        try:
            InstallUser.addUser(user_repo)
            self.start_main_window(user_repo)
        except InstallUser.ExceptionUserExist as err:
            print(err)

    def start_main_window(self, user_repo):
        """Start main application window"""
        self.main_window = MainWindow(user_repo)
        self.main_window.switchUser.connect(self.show)
        self.main_window.createUser.connect(InstallUser.addUser)
        self.main_window.updateUser.connect(InstallUser.updateUser)
        self.main_window.show()
        self.hide()

    def show_error(self, message):
        """Show error message"""
        QtWidgets.QMessageBox.critical(self, "Ошибка", message)

class EditUserWindow(QtWidgets.QWidget):
    createUser = QtCore.pyqtSignal(object)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        # Implement user edit UI here

class MainWindow(QtWidgets.QMainWindow):
    switchUser = QtCore.pyqtSignal()
    createUser = QtCore.pyqtSignal(object)
    updateUser = QtCore.pyqtSignal(object)
    
    def __init__(self, user_repo, parent=None):
        super().__init__(parent)
        # Implement main application UI here

if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    window = StartWindow()
    window.show()
    sys.exit(app.exec_())
