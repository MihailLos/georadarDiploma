import PySimpleGUI as sg

from Interpolator import Interpolator
from Preprocessor import Preprocessor
from Visualizator import Visualizator


class InterpolationGUI:
    def __init__(self, radargramm_companion, visualization_companion):
        self.interpolation = Interpolator()
        self.visualizator = Visualizator(visualization_companion=visualization_companion)
        self.preprocessor = Preprocessor(radargramm_companion=radargramm_companion)
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
        self.selected_colormap = 'gray'
        self.colormap_names = list(self.colormaps_list.keys())
        self.radargramm_list = []
        self.chosen_radargramm_amplitudes = None
        self.chosen_second_radargramm_amplitudes = None
        self.radargramm_companion = radargramm_companion
        self.lower_diap = 0
        self.upper_diap = 0
        self.combined = None
        self.num_traces = None
        self.num_samples = None

    def make_layout(self):
        layout = [
            [sg.Text("Выберите два набора данных и нажмите кнопку интерполяции для получения финального результата")],
            [sg.Text("Выберите первый набор данных для интерполяции:")],
            [sg.DropDown(self.radargramm_list, key='-RADARGRAMM_LIST3-', enable_events=True, readonly=True)],
            [sg.Text("Выберите второй набор данных для интерполяции:")],
            [sg.DropDown(self.radargramm_list, key='-RADARGRAMM_LIST4-', enable_events=True, readonly=True)],
            [sg.Button("Интерполяция", key='-DATA_INTERPOLATION-')],
            [sg.Canvas(size=(800, 400), key="-CANVAS3-")],
            [sg.Text("Выберите цветовую схему (по умолчанию выставлена черно-белая):", visible=False,
                     key='-CHOOSE_COLORSCHEME_TEXT3-')],
            [sg.DropDown(self.colormap_names, key="-COLORMAP_LIST3-", enable_events=True, readonly=True,
                         default_value='Черно-белый спектр', visible=False)],
            [sg.Button("Сохранить файл визуализации в базу данных", key='-SAVE_PREPROCESS_TO_DB2-', visible=False)]
        ]

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

    def get_amplitudes_second_by_id(self, id):
        self.chosen_second_radargramm_amplitudes = self.radargramm_companion.db_read_radaragramm_by_id(id)
