import PySimpleGUI as sg

from Preprocessor import Preprocessor
from Visualizator import Visualizator


class PreprocessorGUI:
    def __init__(self, preprocessor_companion, radargramm_companion, visualizator_companion):
        self.visualizator = Visualizator(visualization_companion=visualizator_companion)
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
        self.selected_colormap = None
        self.colormap_names = list(self.colormaps_list.keys())
        self.radargramm_list = []
        self.chosen_radargramm_amplitudes = None
        self.selected_radargramm_id = None
        self.radargramm_companion = radargramm_companion
        self.preprocessor_companion = preprocessor_companion
        self.canvas_elem = None

    def make_layout(self):
        layout = [
            [sg.Text("Выберите набор данных для предобработки:")],
            [sg.DropDown(self.radargramm_list, key='-RADARGRAMM_LIST2-', enable_events=True, readonly=True)],
            [sg.Button("Привести данные к единому масштабу", key='-SCALE_DATA-')],
            [sg.Canvas(size=(400, 400), key="-CANVAS2-")],
            [sg.Text("Выберите цветовую схему (по умолчанию выставлена черно-белая):", visible=False,
                     key='-CHOOSE_COLORSCHEME_TEXT2-')],
            [sg.DropDown(self.colormap_names, key="-COLORMAP_LIST2-", enable_events=True, readonly=True,
                         default_value='Черно-белый спектр', visible=False)],
            [sg.Text("Выберите способ обнаружения аномалий:", key='-CHOOSE_PREPROCESS_TEXT-', visible=False)],
            [sg.Button("Квантильный анализ", key='-QUANTILE_ANALYZE-', visible=False),
             sg.Button("Операция 'травления'", key='-CORRODE_ANALYZE-', visible=False),
             sg.Button("Операция 'расширения'", key='-EXPAND_ANALYZE-', visible=False)],
            [sg.Button("Сохранить результаты обработки в базу данных", button_color='orange', visible=False,
                       key="-SAVE_PREPROCESS_TO_DB-")]
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
