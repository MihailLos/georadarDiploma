from database.radargramm import RadargrammTableCompanion
import PySimpleGUI as sg


class ViewDataGUI:
    def __init__(self, radargramm_companion):
        self.radargramm_companion = radargramm_companion

    def make_layout(self):
        layout = [
            [sg.Text("Загруженные данные из БД:")],
            [sg.Table(values=self.get_radargramm_data(), headings=['ID', 'Название', 'Дата загрузки',
                                                                   'Количество трасс', 'Количество измерений'],
                      display_row_numbers=False, auto_size_columns=True,
                      num_rows=min(20, len(self.get_radargramm_data())),
                      key="-TABLE-", enable_events=True,)],
            [sg.Button("Удалить радарограмму", key='-DELETE_DATA-')]
        ]
        scrollable_layout = [
            [sg.Column(layout, scrollable=True, vertical_scroll_only=True, size=(1920, 1080))]
        ]
        return scrollable_layout

    def get_radargramm_data(self):
        radargramms = self.radargramm_companion.db_read_radargramms()
        data = []
        for radargramm in radargramms:
            data.append([radargramm.ID, radargramm.Name, radargramm.Load_Date, radargramm.Num_Traces,
                         radargramm.Num_Samples])
        return data