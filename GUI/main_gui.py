import random

import PySimpleGUI as sg

from GUI.interpolation_gui import InterpolationGUI
from GUI.load_gui import LoadRadargrammGUI
from GUI.preprocessor_gui import PreprocessorGUI
from GUI.viewdata_gui import ViewDataGUI
from GUI.visualization_gui import VisualizationGUI


class MainGUI:
    def __init__(self, preprocessing_db_companion, radargramm_db_companion, visualisation_db_companion):
        self.load_radargramm_gui = LoadRadargrammGUI(radargramm_companion=radargramm_db_companion)
        self.view_data_gui = ViewDataGUI(radargramm_companion=radargramm_db_companion)
        self.visualization_gui = VisualizationGUI(
            radargramm_companion=radargramm_db_companion,
            visualizator_companion=visualisation_db_companion
        )
        self.preprocessor_gui = PreprocessorGUI(
            preprocessor_companion=preprocessing_db_companion,
            radargramm_companion=radargramm_db_companion,
            visualizator_companion=visualisation_db_companion
        )
        self.interpolation_gui = InterpolationGUI(
            radargramm_companion=radargramm_db_companion,
            visualization_companion=visualisation_db_companion
        )

        self.layout = [
            [sg.TabGroup(
                [[
                    sg.Tab("Загрузка данных", self.load_radargramm_gui.make_layout(), key='-LOAD_DATA_TAB-'),
                    sg.Tab("Просмотр данных", self.view_data_gui.make_layout(), key='-VIEW_DATA_TAB-'),
                    sg.Tab("Визуализация данных (ручная)", self.visualization_gui.make_layout(),
                           key='-HANDLE_VISUALIZE_TAB-'),
                    sg.Tab("Автоматическое обнаружение аномалий", self.preprocessor_gui.make_layout(),
                           key='-AUTO_ANOMALIES_RECOGNIZE-'),
                    sg.Tab("Интерполяция", self.interpolation_gui.make_layout(), key="-INTERPOLATION-")
                ]],
                key='-TAB_GROUP-',
                enable_events=True,
                tab_location="topleft",
            )]
        ]

        self.window = sg.Window('Главное окно', self.layout, resizable=True, finalize=True)

    def run(self):
        self.visualization_gui.get_radargramm_data()
        self.preprocessor_gui.get_radargramm_data()
        self.interpolation_gui.get_radargramm_data()
        self.window['-RADARGRAMM_LIST-'].update(values=self.visualization_gui.radargramm_list)
        self.window['-RADARGRAMM_LIST2-'].update(values=self.preprocessor_gui.radargramm_list)
        self.window['-RADARGRAMM_LIST3-'].update(values=self.interpolation_gui.radargramm_list)
        self.window['-RADARGRAMM_LIST4-'].update(values=self.interpolation_gui.radargramm_list)
        while True:
            event, values = self.window.read()
            if event == sg.WINDOW_CLOSED:
                break
            # Экран просмотра и удаления радарограмм
            elif event == '-DELETE_DATA-':
                selected_rows = values['-TABLE-']
                if selected_rows:
                    selected_radargramm_id = self.view_data_gui.get_radargramm_data()[selected_rows[0]][0]
                    confirm = sg.popup_ok_cancel("Вы уверены, что хотите удалить выбранную радарограмму?")
                    if confirm == "OK":
                        self.view_data_gui.radargramm_companion.db_delete_radargramm_by_id(id=selected_radargramm_id)
                        sg.popup("Радарограмма успешно удалена.")
                        self.window['-TABLE-'].update(values=self.view_data_gui.get_radargramm_data())
                        self.visualization_gui.get_radargramm_data()
                        self.window['-RADARGRAMM_LIST-'].update(values=self.visualization_gui.radargramm_list)
                        self.window['-RADARGRAMM_LIST2-'].update(values=self.visualization_gui.radargramm_list)
                        self.window['-RADARGRAMM_LIST3-'].update(values=self.visualization_gui.radargramm_list)
                        self.window['-RADARGRAMM_LIST4-'].update(values=self.visualization_gui.radargramm_list)
            # Экран загрузки радарограмм
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
                self.visualization_gui.get_radargramm_data()
                self.window['-RADARGRAMM_LIST-'].update(values=self.visualization_gui.radargramm_list)
                self.window['-RADARGRAMM_LIST2-'].update(values=self.visualization_gui.radargramm_list)
                self.window['-RADARGRAMM_LIST3-'].update(values=self.visualization_gui.radargramm_list)
                self.window['-RADARGRAMM_LIST4-'].update(values=self.visualization_gui.radargramm_list)
                self.window['-PROGRESS-'].update(visible=True)
                for i in range(1000):
                    sg.one_line_progress_meter('Загрузка', i + 1, 1000, '-PROGRESS-')
                sg.popup('Данные успешно загружены')
                self.window['-FILE-'].update('')
                self.window['-NAME-'].update('')
                self.window['-PROGRESS-'].update(visible=False)
            # Экран предобработки данных
            elif event == '-RADARGRAMM_LIST-':
                selected_radargramm = values["-RADARGRAMM_LIST-"]
                if selected_radargramm:
                    selected_id = selected_radargramm[0]
                    self.visualization_gui.get_amplitudes_by_id(selected_id)
            elif event == '-VISUALIZE_DATA-':
                if self.visualization_gui.chosen_radargramm_amplitudes is None:
                    sg.popup_error("Выберите радарограмму для визуализации!")
                else:
                    self.visualization_gui.update_sliders()
                    self.window['-MIN_AMPL_SLIDER-'].update(
                        range=(self.visualization_gui.lower_diap, self.visualization_gui.avg_diap))
                    self.window['-MAX_AMPL_SLIDER-'].update(
                        range=(self.visualization_gui.avg_diap, self.visualization_gui.upper_diap))
                    self.visualization_gui.selected_colormap = self.visualization_gui.colormaps_list.get(
                        values['-COLORMAP_LIST-'])
                    self.visualization_gui.visualizator.make_radargramm_image(
                        self.visualization_gui.chosen_radargramm_amplitudes,
                        colormap=self.visualization_gui.selected_colormap)
                    self.visualization_gui.canvas_elem = self.window['-CANVAS-'].TKCanvas
                    self.visualization_gui.visualizator.show_radargramm_image(self.visualization_gui.canvas_elem)
                    self.window['-CHOOSE_COLORSCHEME_TEXT-'].update(visible=True)
                    self.window['-COLORMAP_LIST-'].update(visible=True)
                    self.window['-DB_SAVE_VISUALIZATION-'].update(visible=True)
                    self.window['-CHANGE_AMPL_DIAP_TEXT-'].update(visible=True)
                    self.window['-MIN_AMPL_SLIDER_LABEL-'].update(visible=True)
                    self.window['-MIN_AMPL_SLIDER-'].update(visible=True)
                    self.window['-MAX_AMPL_SLIDER_LABEL-'].update(visible=True)
                    self.window['-MAX_AMPL_SLIDER-'].update(visible=True)
            elif event == '-COLORMAP_LIST-':
                selected_colorscheme = values['-COLORMAP_LIST-']
                self.visualization_gui.selected_colormap = self.visualization_gui.colormaps_list.get(
                    selected_colorscheme)
                if self.visualization_gui.selected_colormap is not None:
                    self.visualization_gui.visualizator.make_radargramm_image(
                        self.visualization_gui.chosen_radargramm_amplitudes,
                        colormap=self.visualization_gui.selected_colormap)
                    canvas_elem = self.window['-CANVAS-'].TKCanvas
                    self.visualization_gui.visualizator.show_radargramm_image(canvas_elem)
            elif event == '-MIN_AMPL_SLIDER-' or event == '-MAX_AMPL_SLIDER-':
                self.visualization_gui.lower_diap = values['-MIN_AMPL_SLIDER-']
                self.visualization_gui.upper_diap = values['-MAX_AMPL_SLIDER-']
                self.visualization_gui.visualizator.make_radargramm_image(
                    self.visualization_gui.chosen_radargramm_amplitudes,
                    colormap=self.visualization_gui.selected_colormap,
                    lower_limit=self.visualization_gui.lower_diap,
                    upper_limit=self.visualization_gui.upper_diap)
                canvas_elem = self.window['-CANVAS-'].TKCanvas
                self.visualization_gui.visualizator.show_radargramm_image(canvas_elem)
            elif event == '-DB_SAVE_VISUALIZATION-':
                self.visualization_gui.visualizator.db_save(colormap=self.visualization_gui.selected_colormap,
                                                            img_file=self.visualization_gui.visualizator.get_bytes_from_image(),
                                                            upper_limit=self.visualization_gui.upper_diap,
                                                            lower_limit=self.visualization_gui.lower_diap,
                                                            radargramm_id=values['-RADARGRAMM_LIST-'][0])
                sg.popup('Данные успешно загружены.')
            elif event == '-RADARGRAMM_LIST2-':
                selected_radargramm = values["-RADARGRAMM_LIST2-"]
                if selected_radargramm:
                    self.selected_radargramm_id = selected_radargramm[0]
                    self.preprocessor_gui.get_amplitudes_by_id(self.selected_radargramm_id)
            elif event == '-SCALE_DATA-':
                if self.preprocessor_gui.chosen_radargramm_amplitudes is None:
                    sg.popup_error("Выберите набор данных для предобработки!")
                else:
                    self.preprocessor_gui.preprocessor.scale_data(self.preprocessor_gui.chosen_radargramm_amplitudes)
                    self.selected_colormap = self.preprocessor_gui.colormaps_list.get(
                        values['-COLORMAP_LIST2-'])
                    self.preprocessor_gui.visualizator.make_radargramm_image(
                        self.preprocessor_gui.preprocessor.scaled_amplitudes,
                        colormap=self.selected_colormap)
                    self.canvas_elem = self.window['-CANVAS2-'].TKCanvas
                    self.preprocessor_gui.visualizator.show_radargramm_image(self.canvas_elem)
                    self.window['-CHOOSE_COLORSCHEME_TEXT2-'].update(visible=True)
                    self.window['-CHOOSE_PREPROCESS_TEXT-'].update(visible=True)
                    self.window['-COLORMAP_LIST2-'].update(visible=True)
                    self.window['-QUANTILE_ANALYZE-'].update(visible=True)
                    self.window['-CORRODE_ANALYZE-'].update(visible=True)
                    self.window['-EXPAND_ANALYZE-'].update(visible=True)
            # Экран интерполяции
            elif event == '-RADARGRAMM_LIST3-':
                selected_radargramm = values["-RADARGRAMM_LIST3-"]
                if selected_radargramm:
                    selected_id = selected_radargramm[0]
                    self.interpolation_gui.get_amplitudes_by_id(selected_id)
            elif event == '-RADARGRAMM_LIST4-':
                selected_radargramm = values["-RADARGRAMM_LIST4-"]
                if selected_radargramm:
                    selected_id = selected_radargramm[0]
                    self.interpolation_gui.get_amplitudes_second_by_id(selected_id)
            elif event == '-DATA_INTERPOLATION-':
                if self.interpolation_gui.chosen_radargramm_amplitudes is None or self.interpolation_gui.chosen_second_radargramm_amplitudes is None:
                    sg.popup_error("Выберите радарограмму для визуализации!")
                else:
                    selected_colorscheme = values['-COLORMAP_LIST3-']
                    self.selected_colormap = self.preprocessor_gui.colormaps_list.get(selected_colorscheme)
                    interpolated_amplitudes = self.interpolation_gui.interpolation.interpolated_amplitudes(
                        amplitudes1=self.interpolation_gui.chosen_radargramm_amplitudes,
                        amplitudes2=self.interpolation_gui.chosen_second_radargramm_amplitudes,
                    )
                    if interpolated_amplitudes is None:
                        sg.popup_error('Радарограммы имеют слишком разные значения')
                    else:
                        (
                            self.interpolation_gui.combined,
                            self.interpolation_gui.num_traces,
                            self.interpolation_gui.num_samples
                        ) = self.interpolation_gui.visualizator.make_radargramm_images(
                            amplitudes1=self.interpolation_gui.chosen_radargramm_amplitudes,
                            interpolated_amplitudes=interpolated_amplitudes,
                            amplitudes2=self.interpolation_gui.chosen_second_radargramm_amplitudes,
                            colormap=self.selected_colormap)
                        self.interpolation_gui.canvas_elem = self.window['-CANVAS3-'].TKCanvas
                        self.interpolation_gui.visualizator.show_radargramm_image(self.interpolation_gui.canvas_elem)
                        self.window['-CHOOSE_COLORSCHEME_TEXT3-'].update(visible=True)
                        self.window['-COLORMAP_LIST3-'].update(visible=True)
                        self.window['-SAVE_PREPROCESS_TO_DB2-'].update(visible=True)
            elif event == '-COLORMAP_LIST3-':
                selected_colorscheme = values['-COLORMAP_LIST3-']
                self.selected_colormap = self.interpolation_gui.colormaps_list.get(selected_colorscheme)
                if self.selected_colormap is not None and self.interpolation_gui.chosen_radargramm_amplitudes is not None and self.interpolation_gui.chosen_second_radargramm_amplitudes is not None:
                    interpolated_amplitudes = self.interpolation_gui.interpolation.interpolated_amplitudes(
                        amplitudes1=self.interpolation_gui.chosen_radargramm_amplitudes,
                        amplitudes2=self.interpolation_gui.chosen_second_radargramm_amplitudes,
                    )
                    self.interpolation_gui.visualizator.make_radargramm_images(
                        amplitudes1=self.interpolation_gui.chosen_radargramm_amplitudes,
                        interpolated_amplitudes=interpolated_amplitudes,
                        amplitudes2=self.interpolation_gui.chosen_second_radargramm_amplitudes,
                        colormap=self.selected_colormap)
                    canvas_elem = self.window['-CANVAS3-'].TKCanvas
                    self.interpolation_gui.visualizator.show_radargramm_image(canvas_elem)
            elif event == '-COLORMAP_LIST2-':
                selected_colorscheme = values['-COLORMAP_LIST2-']
                self.selected_colormap = self.preprocessor_gui.colormaps_list.get(selected_colorscheme)
                if self.selected_colormap is not None:
                    self.preprocessor_gui.visualizator.make_radargramm_image(
                        self.preprocessor_gui.preprocessor.scaled_amplitudes,
                        colormap=self.selected_colormap
                    )
                    canvas_elem = self.window['-CANVAS2-'].TKCanvas
                    self.preprocessor_gui.visualizator.show_radargramm_image(canvas_elem)
            elif event == '-SAVE_PREPROCESS_TO_DB2-':
                decision = sg.popup_ok_cancel(
                    'Загружаемые данные будут задействованы при создании модели обнаружения аномалий '
                    'на радарограмме! В дальнейшем вы можете удалить неактуальные данные.',
                    title='Предупреждение')
                if decision == 'OK':
                    text = sg.popup_get_text(
                        'Введите название сохраняемых данных для удобства поиска:',
                        title='Ввод названия'
                    )
                    self.interpolation_gui.radargramm_companion.db_save(
                        radargramm_name=text,
                        file_content=None,
                        num_traces=self.interpolation_gui.num_traces,
                        num_samples=self.interpolation_gui.num_samples,
                        amplitudes_data=self.interpolation_gui.combined,
                    )
                    self.visualization_gui.get_radargramm_data()
                    self.window['-RADARGRAMM_LIST-'].update(values=self.visualization_gui.radargramm_list)
                    self.window['-RADARGRAMM_LIST2-'].update(values=self.visualization_gui.radargramm_list)
                    self.window['-RADARGRAMM_LIST3-'].update(values=self.visualization_gui.radargramm_list)
                    self.window['-RADARGRAMM_LIST4-'].update(values=self.visualization_gui.radargramm_list)
                    self.window['-TABLE-'].update(values=self.view_data_gui.get_radargramm_data())
                    sg.popup('Данные успешно загружены!')
            elif event == '-QUANTILE_ANALYZE-':
                self.preprocessor_gui.preprocessor.quantile_analyze()
                selected_colorscheme = values['-COLORMAP_LIST2-']
                self.selected_colormap = self.preprocessor_gui.colormaps_list.get(selected_colorscheme)
                if self.selected_colormap is not None:
                    self.preprocessor_gui.visualizator.make_radargramm_image(
                        self.preprocessor_gui.preprocessor.quantile_filtered_amplitudes,
                        colormap=self.selected_colormap
                    )
                    canvas_elem = self.window['-CANVAS2-'].TKCanvas
                    self.preprocessor_gui.visualizator.show_radargramm_image(canvas_elem)
                self.window['-SAVE_PREPROCESS_TO_DB-'].update(visible=True)
            elif event == '-CORRODE_ANALYZE-':
                self.preprocessor_gui.preprocessor.corrode_image()
                selected_colorscheme = values['-COLORMAP_LIST2-']
                self.selected_colormap = self.preprocessor_gui.colormaps_list.get(selected_colorscheme)
                if self.selected_colormap is not None:
                    self.preprocessor_gui.visualizator.make_radargramm_image(
                        self.preprocessor_gui.preprocessor.corrode_filtered_amplitudes,
                        colormap=self.selected_colormap
                    )
                    canvas_elem = self.window['-CANVAS2-'].TKCanvas
                    self.preprocessor_gui.visualizator.show_radargramm_image(canvas_elem)
                self.window['-SAVE_PREPROCESS_TO_DB-'].update(visible=True)
            elif event == '-EXPAND_ANALYZE-':
                self.preprocessor_gui.preprocessor.expand_image()
                selected_colorscheme = values['-COLORMAP_LIST2-']
                self.selected_colormap = self.preprocessor_gui.colormaps_list.get(selected_colorscheme)
                if self.selected_colormap is not None:
                    self.preprocessor_gui.visualizator.make_radargramm_image(
                        self.preprocessor_gui.preprocessor.expand_filtered_amplitudes,
                        colormap=self.selected_colormap
                    )
                    canvas_elem = self.window['-CANVAS2-'].TKCanvas
                    self.preprocessor_gui.visualizator.show_radargramm_image(canvas_elem)
                self.window['-SAVE_PREPROCESS_TO_DB-'].update(visible=True)
            elif event == '-SAVE_PREPROCESS_TO_DB-':
                decision = sg.popup_ok_cancel(
                    'Загружаемые данные будут задействованы при создании модели обнаружения аномалий на радарограмме! '
                    'В дальнейшем вы можете удалить неактуальные данные.',
                    title='Предупреждение'
                )
                if decision == 'OK':
                    text = sg.popup_get_text(
                        'Введите название сохраняемых данных для удобства поиска:',
                        title='Ввод названия'
                    )
                    self.preprocessor_gui.preprocessor_companion.db_save(
                        text,
                        self.preprocessor_gui.preprocessor.interprete_results(self.selected_radargramm_id),
                        self.preprocessor_gui.visualizator.get_bytes_from_image(),
                        self.selected_radargramm_id
                    )
                    sg.popup('Данные успешно загружены!')
        self.window.close()
