import sys
from PyQt6.QtWidgets import QApplication
from src.controllers.ctrl import Controller
from src.model.model import Model
from src.views.main_window import MainView


class ImageInvestigator(QApplication):
    def __init__(self, sys_argv):
        super().__init__(sys_argv)

        self.model = Model()
        self.ctrl = Controller(self.model)
        self.view = MainView(self.model, self.ctrl)

        self.view.show()


if __name__ == "__main__":
    image_investigator = ImageInvestigator(sys.argv)
    sys.exit(image_investigator.exec())
