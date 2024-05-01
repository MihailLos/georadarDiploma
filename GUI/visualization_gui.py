import PySimpleGUI as sg
from Visualizator import Visualizator
from database.radargramm import RadargrammTableCompanion


class VisualizationGUI:
    def __init__(self):
        self.visualizator = Visualizator()
        self.colormaps_dict = {
            0: ['gray', 'черно-белая'],
            1: ['rainbow', 'цветовой спектр'],
            2: ['seismic', 'сейсмический спектр']
        }
        self.radargramm_list = []
        self.chosen_radargramm_amplitudes = None
        self.radargramm_companion = RadargrammTableCompanion()
        self.layout = [
            [sg.Text("Выберите набор данных, который нужно визуализировать:")],
            [sg.DropDown(self.radargramm_list, key="-RADARGRAMM_LIST-", enable_events=True, readonly=True)],
            [sg.Button("Визуализировать данные", key='-VISUALIZE_DATA-')],
            [sg.Canvas(size=(400, 400), key="-CANVAS-"), sg.Text("Выберите цветовую схему:")],
            [sg.Button("Сохранить файл визуализации в базу данных", key='-DB_SAVE_VISUALIZATION-', visible=False)]
        ]
        self.window = sg.Window("Visualization", self.layout)

    def get_radargramm_data(self):
        radargramms = self.radargramm_companion.db_read_radargramms()
        for radargramm in radargramms:
            self.radargramm_list.append([radargramm.ID, radargramm.Name, radargramm.Load_Date, radargramm.Num_Traces,
                         radargramm.Num_Samples])

    def get_amplitudes_by_id(self, id):
        self.chosen_radargramm_amplitudes = self.radargramm_companion.db_read_radaragramm_by_id(id)

    def run(self):
        self.get_radargramm_data()
        while True:
            event, values = self.window.read()
            if event == sg.WINDOW_CLOSED:
                break
            elif event == '-RADARGRAMM_LIST-':
                selected_radargramm = values["-RADARGRAMM_LIST-"]
                if selected_radargramm:
                    selected_id = selected_radargramm[0]
                    self.get_amplitudes_by_id(selected_id)
            elif event == '-VISUALIZE_DATA-':
                if self.chosen_radargramm_amplitudes is None:
                    sg.popup_error("Выберите радарограмму для визуализации!")
                else:
                    self.visualizator.make_radargramm_image(self.chosen_radargramm_amplitudes, colormap='gray')
                    canvas_elem = self.window['-CANVAS-'].TKCanvas
                    self.visualizator.show_radargramm_image(canvas_elem)
                    self.window['-DB_SAVE_VISUALIZATION-'].update(visible=True)

        self.window.close()


ui = VisualizationGUI()
ui.run()
