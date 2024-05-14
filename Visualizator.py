import base64
import datetime
import io

import numpy as np
import tkinter as tk
from PIL import Image, ImageTk
from matplotlib.backends._backend_tk import NavigationToolbar2Tk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
from matplotlib.backends.backend_agg import FigureCanvasAgg

from database.visualization import VisualizationResultsTableCompanion


class Visualizator:
    def __init__(self):
        self.colormap = None
        self.gpr_image_file = None
        self.interpolation_image_file = None
        self.lower_limit = None
        self.upper_limit = None
        self.fig = None
        self.visualization_companion = VisualizationResultsTableCompanion()

    def make_radargramm_image(self, amplitudes, colormap, upper_limit=None, lower_limit=None):
        self.fig = Figure(figsize=(10, 6))
        ax = self.fig.add_subplot(111)

        # Преобразование списка amplitudes в массив NumPy перед транспонированием
        amplitudes_array = np.array(amplitudes)

        if upper_limit is not None and lower_limit is not None:
            amplitudes_array = np.clip(amplitudes_array, lower_limit, upper_limit)

        time_labels = np.linspace(0, len(amplitudes_array[0]), len(amplitudes_array[0]))
        im = ax.imshow(amplitudes_array.T, cmap=colormap, aspect='auto',
                       extent=[0, len(amplitudes_array), time_labels[-1], time_labels[0]])

        self.fig.colorbar(im, ax=ax, label='Амплитуда сигнала')
        ax.set_xlabel('Трассы')
        ax.set_ylabel('Измерения')
        ax.set_title('Радарограмма')

        self.colormap = colormap
        self.upper_limit = upper_limit
        self.lower_limit = lower_limit

    def make_radargramm_images(self, amplitudes1, amplitudes2, colormap='gray', upper_limit=None, lower_limit=None):
        self.fig = Figure(figsize=(16, 8))  # Увеличиваем размер, чтобы поместить два графика
        axes = self.fig.subplots(1, 2)  # Создаем два подграфика

        # Обрабатываем первую радарограмму
        amplitudes_array1 = np.array(amplitudes1)
        if upper_limit is not None and lower_limit is not None:
            amplitudes_array1 = np.clip(amplitudes_array1, lower_limit, upper_limit)
        time_labels1 = np.linspace(0, len(amplitudes_array1[0]), len(amplitudes_array1[0]))
        im1 = axes[0].imshow(amplitudes_array1.T, cmap=colormap, aspect='auto',
                             extent=[0, len(amplitudes_array1), time_labels1[-1], time_labels1[0]])
        axes[0].set_title('Радарограмма 1')
        axes[0].set_xlabel('Трассы')
        axes[0].set_ylabel('Измерения')

        # Обрабатываем вторую радарограмму
        amplitudes_array2 = np.array(amplitudes2)
        if upper_limit is not None and lower_limit is not None:
            amplitudes_array2 = np.clip(amplitudes_array2, lower_limit, upper_limit)
        time_labels2 = np.linspace(0, len(amplitudes_array2[0]), len(amplitudes_array2[0]))
        im2 = axes[1].imshow(amplitudes_array2.T, cmap=colormap, aspect='auto',
                             extent=[0, len(amplitudes_array2), time_labels2[-1], time_labels2[0]])
        axes[1].set_title('Радарограмма 2')
        axes[1].set_xlabel('Трассы')
        axes[1].set_ylabel('Измерения')

        self.fig.colorbar(im1, ax=axes[0], label='Амплитуда сигнала')
        self.fig.colorbar(im2, ax=axes[1], label='Амплитуда сигнала')

    def show_radargramm_image(self, canvas):
        # Удаляем все виджеты из канваса
        for widget in canvas.winfo_children():
            widget.destroy()

        # Получаем размеры канваса
        canvas_width = canvas.winfo_width()
        canvas_height = canvas.winfo_height()

        # Создаем экземпляр FigureCanvasTkAgg с нашим рисунком
        canvas_widget = FigureCanvasTkAgg(self.fig, master=canvas)

        # Получаем tk.Widget для встраивания в окно PySimpleGUI
        canvas_elem = canvas_widget.get_tk_widget()

        # Встраиваем tk.Widget в окно PySimpleGUI
        canvas_elem.pack(side=tk.TOP, fill=tk.BOTH, expand=1)

        # Добавляем панель инструментов
        toolbar = NavigationToolbar2Tk(canvas_widget, canvas)
        toolbar.update()

    def get_bytes_from_image(self):
        img_byte_array = io.BytesIO()
        self.fig.savefig(img_byte_array, format='png')
        img_byte_array.seek(0)
        byte_img = img_byte_array.read()

        return byte_img

    def db_save(self, colormap, img_file, upper_limit, lower_limit, radargramm_id):
        self.visualization_companion.db_save(colormap=colormap, image_file=img_file, upper_limit=upper_limit,
                                             lower_limit=lower_limit, radargramm_id=radargramm_id, date=datetime.date.today())
