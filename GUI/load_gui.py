import PySimpleGUI as sg
from Radargramm import Radargramm
class LoadRadargrammGUI:
    def __init__(self):
        self.radargramm = Radargramm()

    def make_layout(self):
        layout = [
            [sg.Text("Выберите файл радарограммы:")],
            [sg.InputText(key='-FILE-'), sg.FilesBrowse()],
            [sg.Text("Введите название радарограммы:")],
            [sg.InputText(key='-NAME-')],
            [sg.Button("Загрузить данные")],
            [sg.ProgressBar(1000, orientation='h', size=(20, 20), key='-PROGRESS-')]
        ]
        return layout
