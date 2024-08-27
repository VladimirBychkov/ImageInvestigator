import cv2
from pathlib import Path
from PyQt6.QtCore import QObject, pyqtSlot


class Controller(QObject):
    def __init__(self, model):
        super().__init__()

        self._model = model

    @pyqtSlot()
    def change_channel(self, data):
        """ data - [channel idx, is_selected] """
        self._model.channels = {'index': data[0], 'value': data[1]}
        self._model.changed.emit()

    @pyqtSlot()
    def select_image(self, data):
        """ data - [image folder, list of image names] """
        if len(data[1]) == 0:
            return
        selected_image_path = str(Path(data[0]).joinpath(data[1][0].text()))

        original_image = cv2.imread(selected_image_path)
        original_image = cv2.cvtColor(original_image, cv2.COLOR_BGR2RGB)
        self._model.original = original_image.copy()
        self._model.changed.emit()

    @pyqtSlot()
    def overlay_image(self, is_checked):
        self._model.overlay = is_checked
        self._model.changed.emit()

    def init_canny_params(self, data):
        setattr(self._model.canny_params, 'blur', data['blur'])
        setattr(self._model.canny_params, 'low', data['low'])
        setattr(self._model.canny_params, 'high', data['high'])
        self._model._analysis_sections = {k: False for k in self._model._analysis_sections.keys()}
        self._model._analysis_sections['canny'] = True
        self._model.overlay = data['overlay']

    @pyqtSlot()
    def change_canny_param(self, param, value):
        match param:
            case 'blur':
                self._model.canny_params = {'param': 'blur', 'value': value}
            case 'low':
                self._model.canny_params = {'param': 'low', 'value': value}
            case 'high':
                self._model.canny_params = {'param': 'high', 'value': value}
            case _:
                return
        self._model.changed.emit()

    def init_otsu_params(self, data):
        setattr(self._model.otsu_params, 'blur', data['blur'])
        self._model._analysis_sections = {k: False for k in self._model._analysis_sections.keys()}
        self._model._analysis_sections['otsu'] = True
        self._model.overlay = data['overlay']

    @pyqtSlot()
    def change_otsu_param(self, param, value):
        match param:
            case 'blur':
                self._model.otsu_params = {'param': 'blur', 'value': value}
            case _:
                return
        self._model.changed.emit()
