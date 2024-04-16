import obspy
import matplotlib.pyplot as plt
from matplotlib.widgets import Slider
import numpy as np
from scipy import ndimage
from sklearn.preprocessing import MinMaxScaler
import pandas as pd

class Radargramm:
    scaled_amplitudes_df = pd.DataFrame()
    amplitudes_df = pd.DataFrame()

    def read_from_segy(self, filepath):
        amplitudes = []
        stream = obspy.read(filepath)
        for trace in stream:
            amplitudes.append(trace.data)

        # Преобразуем массивы в DataFrame
        self.amplitudes_df = pd.DataFrame(amplitudes)

    def visualize(self, amplitudes_df, colormap='rainbow'):
        fig, ax = plt.subplots(figsize=(10, 6))

        amplitudes = amplitudes_df.values
        amplitude_min = np.min(amplitudes)
        amplitude_max = np.max(amplitudes)

        im = ax.imshow(amplitudes.T, cmap=colormap, aspect='auto')
        plt.colorbar(im, label='Амплитуда сигнала')
        plt.xlabel('Трассы')
        plt.ylabel('Измерения')
        plt.title('Радарограмма')

        # Создаем слайдеры для изменения диапазона амплитуд
        ax_amplitude_min = plt.axes([0.2, 0.02, 0.65, 0.03])
        ax_amplitude_max = plt.axes([0.2, 0.06, 0.65, 0.03])

        s_amplitude_min = Slider(ax_amplitude_min, 'Min Amplitude', amplitude_min, amplitude_max, valinit=amplitude_min)
        s_amplitude_max = Slider(ax_amplitude_max, 'Max Amplitude', amplitude_min, amplitude_max, valinit=amplitude_max)

        def update(val):
            min_val = s_amplitude_min.val
            max_val = s_amplitude_max.val

            amplitudes_clipped = np.clip(amplitudes_df.values, min_val, max_val)

            im.set_data(amplitudes_clipped.T)
            fig.canvas.draw_idle()

        s_amplitude_min.on_changed(update)
        s_amplitude_max.on_changed(update)

        plt.show()

    def scale_data(self):
        scaler = MinMaxScaler()
        self.scaled_amplitudes_df = pd.DataFrame(scaler.fit_transform(self.amplitudes_df))

    def preprocess_image(self):
        # Находим 5-й процентный квантиль для сигналов радарограммы
        threshold = np.percentile(self.scaled_amplitudes_df.values.flatten(), 5)

        # Бинаризуем изображение: если значение амплитуды больше порога, делаем его 1, иначе 0
        binary_image_quantile = (self.scaled_amplitudes_df > threshold).astype(int)

        # Применяем операцию коррозии для выполнения "травления"
        corroded_image = ndimage.binary_erosion(binary_image_quantile.values, structure=np.ones((3, 3))).astype(int)

        # Визуализируем оба результата предобработки для сравнения
        fig, axes = plt.subplots(1, 2, figsize=(12, 6))

        # Визуализация квантильного анализа
        ax = axes[0]
        ax.imshow(binary_image_quantile.values.T, cmap='gray', aspect='auto')
        ax.set_title('Квантильный анализ')
        ax.set_xlabel('Трассы')
        ax.set_ylabel('Измерения')

        # Визуализация операции коррозии
        ax = axes[1]
        ax.imshow(corroded_image.T, cmap='gray', aspect='auto')
        ax.set_title('Травление')
        ax.set_xlabel('Трассы')
        ax.set_ylabel('Измерения')

        plt.show()

radargramm = Radargramm()
radargramm.read_from_segy("initial_data/Пресный_водоём.seg")
radargramm.scale_data()
print(radargramm.scaled_amplitudes_df)
radargramm.preprocess_image()