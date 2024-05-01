import numpy as np
import tkinter as tk
from PIL import Image, ImageTk
from matplotlib.backends._backend_tk import NavigationToolbar2Tk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
from matplotlib.backends.backend_agg import FigureCanvasAgg


class Visualizator:
    def __init__(self):
        self.colormap = None
        self.gpr_image_file = None
        self.interpolation_image_file = None
        self.lower_limit = None
        self.upper_limit = None
        self.fig = None

    def make_radargramm_image(self, amplitudes, colormap, upper_limit=None, lower_limit=None):
        self.fig = Figure(figsize=(10, 6))
        ax = self.fig.add_subplot(111)

        # Преобразование списка amplitudes в массив NumPy перед транспонированием
        amplitudes_array = np.array(amplitudes)

        if upper_limit is not None and lower_limit is not None:
            amplitudes = np.clip(amplitudes_array, upper_limit, lower_limit)

        time_labels = np.linspace(0, len(amplitudes[0]), len(amplitudes[0]))
        im = ax.imshow(amplitudes_array.T, cmap=colormap, aspect='auto',
                       extent=[0, len(amplitudes), time_labels[-1], time_labels[0]])

        self.fig.colorbar(im, ax=ax, label='Амплитуда сигнала')
        ax.set_xlabel('Трассы')
        ax.set_ylabel('Измерения')
        ax.set_title('Радарограмма')

        self.colormap = colormap
        self.upper_limit = upper_limit
        self.lower_limit = lower_limit

    def show_radargramm_image(self, canvas):
        # Удаляем все виджеты из канваса
        for widget in canvas.winfo_children():
            widget.destroy()

        # Создаем экземпляр FigureCanvasTkAgg с нашим рисунком
        canvas_widget = FigureCanvasTkAgg(self.fig, master=canvas)

        # Получаем tk.Widget для встраивания в окно PySimpleGUI
        canvas_elem = canvas_widget.get_tk_widget()

        # Встраиваем tk.Widget в окно PySimpleGUI
        canvas_elem.pack(side=tk.TOP, fill=tk.BOTH, expand=1)

        # Добавляем панель инструментов
        toolbar = NavigationToolbar2Tk(canvas_widget, canvas)
        toolbar.update()

