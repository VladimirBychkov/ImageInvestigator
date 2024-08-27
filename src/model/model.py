from PyQt6.QtCore import QObject, pyqtSignal
from collections import namedtuple
from dataclasses import dataclass
from typing import Optional
import cv2
import numpy as np
from skimage.feature import canny
from skimage.filters import threshold_otsu, rank


@dataclass
class CannyParams:
    blur: Optional[int]
    low:  Optional[int]
    high: Optional[int]


@dataclass
class OtsuParams:
    blur:  Optional[int]
    local: Optional[bool]
    size:  Optional[int]


class Model(QObject):

    changed = pyqtSignal()

    def __init__(self):
        super().__init__()

        self._original = None
        self._current = None

        # red, gree, blue
        self._channels = np.array([True, True, True])

        self._analysis_sections = {'canny': False, 'otsu': False}
        self._analysis_map = {'canny': self._perform_canny_analysis,
                              'otsu': self._perform_otsu_analysis}
        self._canny_params = CannyParams(None, None, None)
        self._otsu_params = OtsuParams(None, None, None)
        self._overlay = None

    @property
    def original(self):
        return self._original

    @original.setter
    def original(self, original):
        self._original = original
        self.update()

    @property
    def current(self):
        return self._current

    @property
    def channels(self):
        return self._channels

    @channels.setter
    def channels(self, data):
        self._channels[data['index']] = data['value']
        self.update()

    @property
    def overlay(self):
        return self._overlay

    @overlay.setter
    def overlay(self, value):
        self._overlay = value
        self.update()

    @property
    def canny_params(self):
        return self._canny_params

    @canny_params.setter
    def canny_params(self, data):
        setattr(self._canny_params, data['param'], data['value'])
        self.update()

    @property
    def otsu_params(self):
        return self._otsu_params

    @otsu_params.setter
    def otsu_params(self, data):
        setattr(self._otsu_params, data['param'], data['value'])
        self.update()

    def update(self):
        if self._original is None:
            return

        self._current = self._original.copy()
        self._current[..., np.invert(self._channels)] = 0

        for section, to_perform in self._analysis_sections.items():
            if to_perform:
                self._analysis_map[section]()

        x=1

    def _perform_canny_analysis(self):
        # sanity checks
        if self._canny_params.blur is None or np.count_nonzero(self._channels) > 1:
            return

        edges = 255 * canny(self._current[..., self._channels][..., 0],
                            self._canny_params.blur,
                            self._canny_params.low,
                            self._canny_params.high).astype(np.uint8)

        if self._overlay:
            self._current = self._original.copy()
            self._current[np.where(edges)] = 255
        else:
            self._current[..., np.nonzero(self._channels)[0][0]] = edges

    def _perform_otsu_analysis(self):
        # sanity checks
        if self._otsu_params.blur is None or np.count_nonzero(self._channels) > 1:
            return

        temp_img = self._current[..., np.nonzero(self._channels)[0][0]]
        temp_img = cv2.blur(temp_img, (self._otsu_params.blur, self._otsu_params.blur))

        otsu_img = temp_img >= threshold_otsu(temp_img)
        otsu_img = 255 * np.asarray(otsu_img, dtype=np.uint8)

        if self._overlay:
            cnts = cv2.findContours(otsu_img, cv2.RETR_LIST, cv2.CHAIN_APPROX_NONE)[0]
            self._current = self._original.copy()
            cv2.drawContours(self._current, cnts, -1, 255, 1)
        else:
            self._current[..., np.nonzero(self._channels)[0][0]] = otsu_img
