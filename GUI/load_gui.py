import PySimpleGUI as sg
from Radargramm import Radargramm
class LoadRadargrammGUI:
    def __init__(self):
        self.layout = [
            [sg.Text("Выберите файл радарограммы:")],
            [sg.InputText(key='-FILE-'), sg.FilesBrowse()],
            [sg.Text("Введите название радарограммы:")],
            [sg.InputText(key='-NAME-')],
            [sg.Button("Загрузить данные")],
            [sg.ProgressBar(1000, orientation='h', size = (20, 20), key='-PROGRESS-')]
        ]
        self.window = sg.Window("Загрузка радарограммы", self.layout)
        self.radargramm = Radargramm()

    def run(self):
        while True:
            event, values = self.window.read()
            if event == sg.WINDOW_CLOSED:
                break
            elif event == "Загрузить данные":
                file_path = values['-FILE-']
                radargramm_name = values['-NAME-']

                if not file_path.endswith(".seg"):
                    sg.popup_error('Выбранный файл не является файлом радарограммы (.seg)')
                    continue
                if not radargramm_name:
                    sg.popup_error('Введите название радарограммы!')
                    continue
                self.radargramm.load_data(file=file_path, name=radargramm_name)
                self.window['-PROGRESS-'].update(visible=True)
                for i in range(1000):
                    sg.one_line_progress_meter('Загрузка', i + 1, 1000, '-PROGRESS-')
                sg.popup('Данные успешно загружены')
                self.window['-FILE-'].update('')
                self.window['-NAME-'].update('')
                self.window['-PROGRESS-'].update(visible=False)
        self.window.close()