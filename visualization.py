import obspy
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.widgets import Slider
from scipy import ndimage
from sklearn.preprocessing import MinMaxScaler


class Radargramm:
    scaled_amplitudes_df = pd.DataFrame()
    amplitudes_df = pd.DataFrame()
    def __init__(self):
        self.amplitudes_df = pd.DataFrame()

    def read_from_segy_interpolation(self, filepath):
        stream = obspy.read(filepath)
        data = np.array([trace.data for trace in stream])
        return pd.DataFrame(data).T

    def interpolate_datasets(self, df1, df2, traces_between):
        if df1.shape[1] != df2.shape[1]:
            raise ValueError("Datasets must have the same number of traces")

        total_traces = df1.shape[1] + df2.shape[1] + traces_between
        interpolated_data = np.zeros((df1.shape[0], total_traces))
        interpolated_data[:, :df1.shape[1]] = df1.values
        start_second_dataset = df1.shape[1] + traces_between

        interpolated_data[:, start_second_dataset:start_second_dataset + df2.shape[1]] = df2.values

        start_value = df1.iloc[:, -1]
        end_value = df2.iloc[:, 0]
        for i in range(df1.shape[0]):
            interpolated_data[i, df1.shape[1]:start_second_dataset] = np.linspace(start_value[i], end_value[i],
                                                                                  traces_between + 2)[1:-1]

        return pd.DataFrame(interpolated_data)

    def visualize_interpolation(self, data, start_interp=None, end_interp=None, colormap='gray'):
        plt.figure(figsize=(10, 6))
        im = plt.imshow(data, aspect='auto', interpolation='none', cmap=colormap)
        plt.colorbar(im, label='Amplitude')
        plt.xlabel('Traces')
        plt.ylabel('Samples')
        plt.title('Interpolated Radargram')

        if start_interp is not None and end_interp is not None:
            plt.axvline(x=start_interp, color='red', linestyle='--', linewidth=2)
            plt.axvline(x=end_interp, color='red', linestyle='--', linewidth=2)

        plt.show()

    def interpolate_and_visualize(self, file1, file2, traces_between):
        df1 = self.read_from_segy_interpolation(file1)
        df2 = self.read_from_segy_interpolation(file2)
        interpolated_data = self.interpolate_datasets(df1, df2, traces_between)
        start_interp = df1.shape[1]
        end_interp = start_interp + traces_between
        self.visualize_interpolation(interpolated_data, start_interp=start_interp, end_interp=end_interp)

    def read_from_segy(self, filepath):
        amplitudes = []
        stream = obspy.read(filepath)
        for trace in stream:
            amplitudes.append(trace.data)

        # Преобразуем массивы в DataFrame
        self.amplitudes_df = pd.DataFrame(amplitudes)

    def visualize(self, amplitudes_df, colormap='gray'):
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

# Example usage

# radargramm.read_from_segy("initial_data/Пресный_водоём.seg")
# radargramm.scale_data()
# print(radargramm.scaled_amplitudes_df)
# radargramm.visualize(amplitudes_df=radargramm.amplitudes_df)

# Interpolation

traces_between = int(input("Enter the number of new traces to interpolate between existing traces: "))
radargramm.interpolate_and_visualize("initial_data/Пресный_водоём.seg",
                                     "initial_data/Пресный_водоём.seg",
                                     traces_between)
