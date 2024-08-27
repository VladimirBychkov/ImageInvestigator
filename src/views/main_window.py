from pathlib import Path

from PyQt6.QtWidgets import QMainWindow, QFileDialog, QGraphicsScene, QWidget
from PyQt6.QtGui import QPixmap, QImage
from PyQt6.QtCore import pyqtSlot, Qt
from PyQt6 import uic
from src.views.main_window_ui import Ui_MainWindow


IMG_EXTENSIONS = [".png", ".bmp", ".tif", ".tiff", ".jpg", ".jpeg"]


class EmployeeDlg(QWidget):
    """Employee dialog."""
    def __init__(self, parent=None):
        super().__init__(parent)
        self._an_ui = uic.loadUiType(Path("src/resources/analysis_window.ui"))[0]()
        self._an_ui.setupUi(self)

class MainView(QMainWindow):
    def __init__(self, model, controller):
        super().__init__()

        self._model = model
        self._ctrl = controller

        # self._ui = Ui_MainWindow()
        # Great option to load qt creator ui file without compile it to python code first
        self._ui = uic.loadUiType(Path("src/resources/main_window.ui"))[0]()
        self._ui.setupUi(self)

        self._ui.actionCanny_Edge_Detection.triggered.connect(self.canny_analysis)
        self._ui.actionOtsu_thresholding.triggered.connect(self.otsu_analysis)

        self.w = None
        self.w = EmployeeDlg()
        self._ui.actionAn.triggered.connect(self.an_analysis)

        self.scene = QGraphicsScene(self)

        self._ui.selectFolderButton.clicked.connect(self.open_dialog)
        self._ui.listWidget.itemSelectionChanged.connect(
            lambda: self._ctrl.select_image([self._ui.lineEdit.text(), self._ui.listWidget.selectedItems()]))
        self._ui.RedChannelBox.clicked.connect(
            lambda: self._ctrl.change_channel([0, self._ui.RedChannelBox.isChecked()]))
        self._ui.GreenChannelBox.clicked.connect(
            lambda: self._ctrl.change_channel([1, self._ui.GreenChannelBox.isChecked()]))
        self._ui.BlueChannelBox.clicked.connect(
            lambda: self._ctrl.change_channel([2, self._ui.BlueChannelBox.isChecked()]))

        self._model.changed.connect(self.on_model_change)

    def _setup_canny_analysis_section(self):
        self._ctrl.init_canny_params({'blur': self._ui.cannyBlurSlider.value(),
                                      'low': self._ui.cannyLowSlider.value(),
                                      'high': self._ui.cannyHighSlider.value(),
                                      'overlay': self._ui.overlayOriginalCanny.isChecked()})

        self._ui.cannyBlurSlider.valueChanged.connect(lambda value: self._ui.cannyBlurLabel.setText(str(value)))
        self._ui.cannyLowSlider.valueChanged.connect(lambda value: self._ui.cannyLowLabel.setText(str(value)))
        self._ui.cannyHighSlider.valueChanged.connect(lambda value: self._ui.cannyHighLabel.setText(str(value)))

        self._ui.overlayOriginalCanny.clicked.connect(
            lambda: self._ctrl.overlay_image(self._ui.overlayOriginalCanny.isChecked()))

        self._ui.cannyBlurSlider.valueChanged.connect(lambda value: self._ctrl.change_canny_param('blur', value))
        self._ui.cannyLowSlider.valueChanged.connect(lambda value: self._ctrl.change_canny_param('low', value))
        self._ui.cannyHighSlider.valueChanged.connect(lambda value: self._ctrl.change_canny_param('high', value))

    def _setup_otsu_analysis_section(self):
        self._ctrl.init_otsu_params({'blur': self._ui.otsuBlurSlider.value(),
                                     'overlay': self._ui.overlayOriginalOtsu.isChecked()})

        self._ui.otsuBlurSlider.valueChanged.connect(lambda value: self._ui.otsuBlurLabel.setText(str(value)))

        self._ui.overlayOriginalOtsu.clicked.connect(
            lambda: self._ctrl.overlay_image(self._ui.overlayOriginalOtsu.isChecked()))

        self._ui.otsuBlurSlider.valueChanged.connect(lambda value: self._ctrl.change_otsu_param('blur', value))

    @pyqtSlot()
    def canny_analysis(self):
        self._ui.AnalysisWidget.setCurrentIndex(1)
        self._setup_canny_analysis_section()

    @pyqtSlot()
    def otsu_analysis(self):
        self._ui.AnalysisWidget.setCurrentIndex(2)
        self._setup_otsu_analysis_section()

    @pyqtSlot()
    def an_analysis(self):
        # if self.w is None:
        # self.w = EmployeeDlg()
        self.w.show()
        # else:
        #     self.w.close()
        #     self.w = None


    @pyqtSlot()
    def open_dialog(self):
        # directory = str(QFileDialog.getExistingDirectory(self, "Select Directory", options=QFileDialog.Option.DontUseNativeDialog))
        directory = str(QFileDialog.getExistingDirectory(self, "Select Directory"))
        path = Path(directory)

        self._ui.listWidget.clear()
        self._ui.lineEdit.setText(str(path))
        for ext in IMG_EXTENSIONS:
            for img_file in path.glob(f"*{ext}"):
                self._ui.listWidget.addItem(img_file.name)

    @pyqtSlot()
    def on_model_change(self):
        if self._model.current is None or self._model.original is None:
            return

        self.scene.clear()
        q_image = QImage(self._model.current.data.tobytes(),
                         self._model.current.shape[1],
                         self._model.current.shape[0],
                         self._model.current.strides[0],
                         QImage.Format.Format_RGB888)
        pixmap = QPixmap.fromImage(q_image)

        self.scene.setSceneRect(0, 0, pixmap.width(), pixmap.height())
        self.scene.addPixmap(pixmap)
        self._ui.graphicsView.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft)
        self._ui.graphicsView.setScene(self.scene)
        #self._ui.graphicsView.resize(1024, 1024)
