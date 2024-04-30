from database.DB_connect import DBConnector
from database.radargramm import RadargrammTableCompanion
import PySimpleGUI as sg


class ViewDataGUI:
    def __init__(self):
        self.db_connector = DBConnector()
        self.radargramm_companion = RadargrammTableCompanion()

    def make_layout(self):
        layout = [
            [sg.Text("Загруженные данные из БД:")],
            [sg.Table(values=self.get_radargramm_data(), headings=['ID', 'Название', 'Дата загрузки',
                                                                   'Количество трасс', 'Количество измерений'],
                      display_row_numbers=False, auto_size_columns=True,
                      num_rows=min(20, len(self.get_radargramm_data())),
                      key="-TABLE-", enable_events=True)],
            [sg.Button("Удалить радарограмму")]
        ]
        return layout

    def get_radargramm_data(self):
        radargramms = self.radargramm_companion.db_read_radargramms()
        data = []
        for radargramm in radargramms:
            data.append([radargramm.ID, radargramm.Name, radargramm.Load_Date, radargramm.Num_Traces,
                         radargramm.Num_Samples])
        return data