import PySimpleGUI as sg

from GUI.load_gui import LoadRadargrammGUI
from GUI.viewdata_gui import ViewDataGUI


class MainGUI:
    def __init__(self):
        self.load_radargramm_gui = LoadRadargrammGUI()
        self.view_data_gui = ViewDataGUI()

        self.layout = [
            [sg.TabGroup(
                [[
                    sg.Tab("Загрузка данных", self.load_radargramm_gui.make_layout()),
                    sg.Tab("Просмотр данных", self.view_data_gui.make_layout())
                ]],
                key="-TABGROUP-",
                enable_events=True,
                tab_location="topleft"
            )]
        ]

        self.window = sg.Window('Главное окно', self.layout, resizable=True, finalize=True)

    def run(self):
        while True:
            event, values = self.window.read()
            if event == sg.WINDOW_CLOSED:
                break
            elif event == "Удалить радарограмму":
                selected_rows = values['-TABLE-']
                if selected_rows:
                    selected_radargramm_id = self.view_data_gui.get_radargramm_data()[selected_rows[0]][0]
                    confirm = sg.popup_ok_cancel("Вы уверены, что хотите удалить выбранную радарограмму?")
                    if confirm == "OK":
                        self.view_data_gui.radargramm_companion.db_delete_radargramm_by_id(id=selected_radargramm_id)
                        sg.popup("Радарограмма успешно удалена.")
                        self.window['-TABLE-'].update(values=self.view_data_gui.get_radargramm_data())
            elif event == "Загрузить данные":
                file_path = values['-FILE-']
                radargramm_name = values['-NAME-']

                if not file_path.endswith(".seg"):
                    sg.popup_error('Выбранный файл не является файлом радарограммы (.seg)')
                    continue
                if not radargramm_name:
                    sg.popup_error('Введите название радарограммы!')
                    continue
                self.load_radargramm_gui.radargramm.load_data(file=file_path, name=radargramm_name)
                self.window['-TABLE-'].update(values=self.view_data_gui.get_radargramm_data())
                self.window['-PROGRESS-'].update(visible=True)
                for i in range(1000):
                    sg.one_line_progress_meter('Загрузка', i + 1, 1000, '-PROGRESS-')
                sg.popup('Данные успешно загружены')
                self.window['-FILE-'].update('')
                self.window['-NAME-'].update('')
                self.window['-PROGRESS-'].update(visible=False)
        self.window.close()
