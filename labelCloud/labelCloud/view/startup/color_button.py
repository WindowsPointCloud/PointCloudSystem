from PyQt5 import QtGui, QtWidgets
from PyQt5.QtCore import Qt, pyqtSignal


class ColorButton(QtWidgets.QPushButton):
    """
    Custom Qt Widget to show a chosen color.

    Left-clicking the button shows the color-chooser, while
    right-clicking resets the color to None (no-color).

    Source: https://www.pythonguis.com/widgets/qcolorbutton-a-color-selector-tool-for-pyqt/
    """

    colorChanged = pyqtSignal(object)

    def __init__(self, *args, color="#FF0000", **kwargs):
        super(ColorButton, self).__init__(*args, **kwargs)

        self._color = None
        self._default = color
        self.pressed.connect(self.onColorPicker)

        # Set the initial/default state.
        self.setColor(self._default)

    def setColor(self, color):
        if color != self._color:
            self._color = color
            self.colorChanged.emit(color)

        if self._color:
            self.setStyleSheet("background-color: %s;" % self._color)
        else:
            self.setStyleSheet("")

    def color(self):
        return self._color

    def onColorPicker(self):
        """
        Show color-picker dialog to select color.

        Qt will use the native dialog by default.

        """
        dlg = QtWidgets.QColorDialog(self)
        dlg.setStyleSheet("background-color: None;")  # Set to default background
        
        # Find the QDialogButtonBox and reset the styles for its buttons
        button_box = dlg.findChild(QtWidgets.QDialogButtonBox)
        if button_box:
            for button in button_box.buttons():
                button.setStyleSheet("background-color: None;")  # Reset each button's background

        

            
        if self._color:
            dlg.setCurrentColor(QtGui.QColor(self._color))

        if dlg.exec_():
            self.setColor(dlg.currentColor().name())

    def mousePressEvent(self, e):
        if e.button() == Qt.RightButton:
            self.setColor(self._default)

        return super(ColorButton, self).mousePressEvent(e)
