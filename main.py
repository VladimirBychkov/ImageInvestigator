import sys
import cv2
import numpy as np
from pathlib import Path
from PyQt6 import QtCore, QtGui, QtWidgets
from PyQt6 import uic

from main_window import Ui_MainWindow


IMG_EXTENSIONS = [".png", ".bmp", ".tif", ".tiff", ".jpg", ".jpeg"]


class MainWindow(QtWidgets.QMainWindow):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.ui.selectFolderButton.clicked.connect(self.open_dialog)
        self.ui.listWidget.itemSelectionChanged.connect(self.select_image)
        self.ui.RedChannelBox.clicked.connect(self.select_red_channel)
        self.ui.GreenChannelBox.clicked.connect(self.select_green_channel)
        self.ui.BlueChannelBox.clicked.connect(self.select_blue_channel)

        self.scene = QtWidgets.QGraphicsScene(self)

        self.current_image = None
        self.original_image = None
        self.red_channel_selected = self.ui.RedChannelBox.isChecked()
        self.green_channel_selected = self.ui.GreenChannelBox.isChecked()
        self.blue_channel_selected = self.ui.BlueChannelBox.isChecked()

    @QtCore.pyqtSlot()
    def open_dialog(self):
        directory = str(QtWidgets.QFileDialog.getExistingDirectory(self, "Select Directory"))
        path = Path(directory)

        self.ui.listWidget.clear()
        self.ui.lineEdit.setText(str(path))
        for ext in IMG_EXTENSIONS:
            for img_file in path.glob(f"*{ext}"):
                self.ui.listWidget.addItem(img_file.name)

    @QtCore.pyqtSlot()
    def select_image(self):
        if len(self.ui.listWidget.selectedItems()) == 0:
            return

        selected_image_name = self.ui.listWidget.selectedItems()[0].text()
        selected_image_path = Path(self.ui.lineEdit.text()).joinpath(selected_image_name)

        self.original_image = cv2.imread(str(selected_image_path))
        self.original_image = cv2.cvtColor(self.original_image, cv2.COLOR_BGR2RGB)
        self.current_image = self.original_image.copy()

        self.update()

    def select_red_channel(self):
        self.red_channel_selected = self.ui.RedChannelBox.isChecked()
        self.update()

    def select_green_channel(self):
        self.green_channel_selected = self.ui.GreenChannelBox.isChecked()
        self.update()

    def select_blue_channel(self):
        self.blue_channel_selected = self.ui.BlueChannelBox.isChecked()
        self.update()

    def update(self):
        if self.current_image is None or self.original_image is None:
            return

        self.current_image = self.original_image.copy()
        for idx, selected_channel in enumerate([self.red_channel_selected, self.green_channel_selected, self.blue_channel_selected]):
            if not selected_channel:
                self.current_image[..., idx] = 0

        self.scene.clear()
        q_image = QtGui.QImage(self.current_image.data.tobytes(),
                               self.current_image.shape[1],
                               self.current_image.shape[0],
                               self.current_image.strides[0],
                               QtGui.QImage.Format.Format_RGB888)
        pixmap = QtGui.QPixmap.fromImage(q_image)

        self.scene.setSceneRect(0, 0, pixmap.width(), pixmap.height())
        self.scene.addPixmap(pixmap)
        self.ui.graphicsView.setAlignment(QtCore.Qt.AlignmentFlag.AlignTop | QtCore.Qt.AlignmentFlag.AlignLeft)
        self.ui.graphicsView.setScene(self.scene)


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = MainWindow()
    window.show()
    app.exec()
