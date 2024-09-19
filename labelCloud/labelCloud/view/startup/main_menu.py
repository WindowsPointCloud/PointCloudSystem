from PyQt5.QtWidgets import QMainWindow, QPushButton, QVBoxLayout, QWidget, QLabel, QGridLayout
from PyQt5.QtCore import QSize, Qt
from PyQt5 import uic
from PyQt5.QtWidgets import QApplication, QDesktopWidget
from labelCloud.control.controller import Controller
from labelCloud.view.gui import GUI
from labelCloud.view.augmentation import AugmentationController, AugmentationWindow
from labelCloud.view.training import TrainingController, TrainingWindow
from labelCloud.view.inference import InferenceController, InferenceWindow
import pkg_resources
import logging
import sys
import os
from pathlib import Path
import platform
from PyQt5.QtCore import QSettings

class MainMenu(QMainWindow):
    def __init__(self):
        super().__init__()
        
        # Determine the path to the UI file
        self.ui_path = self._get_ui_path("main_menu_interface.ui")
        uic.loadUi(self.ui_path, self)
        #uic.loadUi(
        #     pkg_resources.resource_filename(
        #        "labelCloud.resources.interfaces", #"main_menu_interface.ui"
        #     ),
        #     self,
        # )
        self.setWindowTitle("MIMOS Main Menu")
        self.setMinimumSize(QSize(500, 500))

        # Set up the layout managers
        central_widget = self.findChild(QWidget, 'centralwidget')
        main_layout = QVBoxLayout(central_widget)
        main_layout.setAlignment(Qt.AlignCenter)

        # Title label
        self.title_label = self.findChild(QLabel, 'title_label')
        self.title_label.setAlignment(Qt.AlignCenter)

        # Button layout
        button_layout = QVBoxLayout()
        button_layout.setSpacing(20)

        self.annotate_pushButton = self.findChild(QPushButton, 'annotate_pushButton')
        self.aug_pushButton = self.findChild(QPushButton, 'aug_pushButton')
        self.training_pushButton = self.findChild(QPushButton, 'training_pushButton')
        self.inf_pushButton = self.findChild(QPushButton, 'inf_pushButton')

        buttons = [self.annotate_pushButton, self.aug_pushButton, self.training_pushButton, self.inf_pushButton]
        for button in buttons:
            button.setMinimumSize(QSize(150, 50))
            button.setStyleSheet("background-color: #007AFF; color: white; border-radius: 10px;")
            button_layout.addWidget(button)

        main_layout.addWidget(self.title_label)
        main_layout.addLayout(button_layout)

        # Connect buttons to their functions
        self.annotate_pushButton.clicked.connect(lambda: self.start_application(GUI, Controller))
        self.aug_pushButton.clicked.connect(lambda: self.start_application(AugmentationWindow, AugmentationController))
        self.training_pushButton.clicked.connect(lambda: self.start_application(TrainingWindow, TrainingController))
        self.inf_pushButton.clicked.connect(lambda: self.start_application(InferenceWindow, InferenceController))

        # Apply the stylesheet
        theme = "dark" if self.is_dark_mode() else "light"
        self.setProperty("theme", theme)
        self.setStyleSheet(self.get_stylesheet())
        
    def _get_ui_path(self, ui_filename):
            """Get the path to the UI file, considering whether running in PyInstaller bundle or not."""
            if getattr(sys, 'frozen', False):
                # Running in a PyInstaller bundle
                base_path = Path(sys._MEIPASS)
            else:
                # Running in a development environment
                base_path = Path(__file__).resolve().parent.parent.parent

            
            return base_path / "resources" /"interfaces" / ui_filename

    def start_application(self, window_class, controller_class):
  
        app = QApplication.instance() or QApplication(sys.argv)

        control = controller_class()
        view = window_class(control)
        app.installEventFilter(view)
        view.show()

        app.setStyle("Fusion")
        desktop = QDesktopWidget().availableGeometry()
        width = (desktop.width() - view.width()) // 2
        height = (desktop.height() - view.height()) // 2
        view.move(width, height)


        logging.info(f"Showing {window_class.__name__} window...")

        # self.close()
        # Uncomment the following line if you want to start the event loop
        # sys.exit(app.exec_())

    def is_dark_mode(self):
        if platform.system() == "Darwin":  # macOS
            os_theme = QSettings().value("AppleInterfaceStyle", "Light")
            return os_theme == "Dark"
        # Add other platform-specific checks if necessary
        return False

    # def start_gui(self):
    #     app = QApplication.instance() or QApplication(sys.argv)

    #     # Setup Model-View-Control structure
    #     control = Controller()
    #     view = GUI(control)

    #     app.installEventFilter(view)

    #     # Start GUI
    #     view.show()

    #     app.setStyle("Fusion")
    #     desktop = QDesktopWidget().availableGeometry()
    #     width = (desktop.width() - view.width()) // 2
    #     height = (desktop.height() - view.height()) // 2
    #     view.move(width, height)

    #     # Close the main menu page when annotate_pushButton is clicked
    #     self.annotate_pushButton.clicked.connect(self.close)

    #     logging.info("Showing Annotation GUI...")
    #     # sys.exit(app.exec_())

    def get_stylesheet(self):
        return """
        QWidget {
            background-color: white;
            color: black;
        }

        QMainWindow[theme="dark"] QWidget {
            background-color: #1E1E1E;
            color: white;
        }

        QPushButton {
            background-color: #007AFF;
            color: white;
            border-radius: 10px;
        }

        QLabel {
            color: inherit;
        }
        """

