import PySimpleGUI as sg
from Visualizator import Visualizator
from database.radargramm import RadargrammTableCompanion
from database.visualization import VisualizationResultsTableCompanion


class VisualizationGUI:
    def __init__(self):
        self.visualizator = Visualizator()
        self.colormaps_list = {
            'Черно-белый спектр': 'gray',
            'Цветовой спектр': 'rainbow',
            'Сейсмический спектр': 'seismic',
            'Зеленый спектр': 'viridis',
            'Фиолетово-желтый спектр': 'plasma',
            'Красно-желтый спектр': 'inferno',
            'Сине-красный спектр': 'magma',
            '"Холодный" спектр': 'cool',
            '"Теплый" спектр': 'hot'
        }
        self.selected_colormap = None
        self.radargramm_list = []
        self.chosen_radargramm_amplitudes = None
        self.radargramm_companion = RadargrammTableCompanion()
        self.colormap_names = list(self.colormaps_list.keys())
        self.lower_diap = 0
        self.upper_diap = 0
        self.avg_diap = 0
        self.canvas_elem = None

    def make_layout(self):
        layout = [
            [sg.Text("Выберите набор данных, который нужно визуализировать:")],
            [sg.DropDown(self.radargramm_list, key='-RADARGRAMM_LIST-', enable_events=True, readonly=True)],
            [sg.Button("Визуализировать данные", key='-VISUALIZE_DATA-')],
            [sg.Canvas(size=(400, 400), key="-CANVAS-")],
            [sg.Text("Выберите цветовую схему (по умолчанию выставлена черно-белая):", visible=False,
                     key='-CHOOSE_COLORSCHEME_TEXT-')],
            [sg.DropDown(self.colormap_names, key="-COLORMAP_LIST-", enable_events=True, readonly=True,
                         default_value='Черно-белый спектр', visible=False)],
            [sg.Text("Выберите отображаемый амплитудный диапазон, используя ползунки:", visible=False,
                     key='-CHANGE_AMPL_DIAP_TEXT-')],
            [sg.Text('Минимум:', visible=False, key='-MIN_AMPL_SLIDER_LABEL-'),
             sg.Slider(range=(0, 0), default_value=self.lower_diap, key='-MIN_AMPL_SLIDER-', visible=False,
                       orientation='h', enable_events=True),
             sg.Text('Максимум:', visible=False, key='-MAX_AMPL_SLIDER_LABEL-'),
             sg.Slider(range=(0, 0), default_value=self.lower_diap, key='-MAX_AMPL_SLIDER-', visible=False,
                       orientation='h', enable_events=True)
             ],
            [sg.Button("Сохранить файл визуализации в базу данных", key='-DB_SAVE_VISUALIZATION-', visible=False)]
        ]
        # Создание скроллируемого окна с layout
        scrollable_layout = [
            [sg.Column(layout, scrollable=True, vertical_scroll_only=True, size=(1920, 1080))]
        ]
        return scrollable_layout

    def get_radargramm_data(self):
        radargramms = self.radargramm_companion.db_read_radargramms()
        self.radargramm_list.clear()
        for radargramm in radargramms:
            self.radargramm_list.append([radargramm.ID, radargramm.Name, radargramm.Load_Date, radargramm.Num_Traces,
                         radargramm.Num_Samples])

    def get_amplitudes_by_id(self, id):
        self.chosen_radargramm_amplitudes = self.radargramm_companion.db_read_radaragramm_by_id(id)

    def update_sliders(self):
        array_from_2d = sum(self.chosen_radargramm_amplitudes, [])
        self.avg_diap = int(sum(array_from_2d)/(len(array_from_2d)))
        self.upper_diap = int(max(array_from_2d))
        self.lower_diap = int(min(array_from_2d))
