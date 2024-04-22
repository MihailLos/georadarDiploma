import obspy
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.widgets import Button, TextBox, RadioButtons
from scipy import ndimage, interpolate
from sklearn.preprocessing import MinMaxScaler


class DataVisualizer:
    def __init__(self):
        self.amplitudes_df = pd.DataFrame()
        self.scaled_amplitudes_df = pd.DataFrame()

    def read_from_segy(self, filepath):
        stream = obspy.read(filepath)
        data = [trace.data for trace in stream]
        self.amplitudes_df = pd.DataFrame(data).T

    def scale_data(self):
        scaler = MinMaxScaler()
        self.scaled_amplitudes_df = pd.DataFrame(scaler.fit_transform(self.amplitudes_df),
                                                 index=self.amplitudes_df.index, columns=self.amplitudes_df.columns)

    @staticmethod
    def visualize(amplitudes_df, colormap='gray'):
        plt.figure(figsize=(10, 6))
        im = plt.imshow(amplitudes_df.values, aspect='auto', cmap=colormap)
        plt.colorbar(im, label='Amplitude')
        plt.xlabel('Traces')
        plt.ylabel('Samples')
        plt.title('Radargram')
        plt.show()

    def preprocess_image(self):
        threshold = np.percentile(self.scaled_amplitudes_df.values.flatten(), 5)
        binary_image_quantile = (self.scaled_amplitudes_df.values > threshold).astype(int)
        corroded_image = ndimage.binary_erosion(binary_image_quantile, structure=np.ones((3, 3))).astype(int)
        fig, axes = plt.subplots(1, 2, figsize=(12, 6))
        ax = axes[0]
        ax.imshow(binary_image_quantile, cmap='gray', aspect='auto')
        ax.set_title('Квантильный анализ')
        ax.set_xlabel('Трассы')
        ax.set_ylabel('Измерения')

        ax = axes[1]
        ax.imshow(corroded_image, cmap='gray', aspect='auto')
        ax.set_title('Травление')
        ax.set_xlabel('Трассы')
        ax.set_ylabel('Измерения')

        plt.show()


class DataInterpolator:
    def __init__(self, visualizer):
        self.visualizer = visualizer

    @staticmethod
    def interpolate_datasets(df1, df2, traces_between, kind='linear'):
        # Создание массивов координат x для известных точек df1 и df2
        x_left = np.arange(df1.shape[1])  # Координаты x для df1
        x_right = np.arange(df1.shape[1] + traces_between,
                            df1.shape[1] + traces_between + df2.shape[1])  # Координаты x для df2
        x_full = np.hstack([x_left, x_right])  # Объединение координат x для обоих df

        # Создание пустого массива для хранения интерполированных данных
        interpolated_data = np.zeros((df1.shape[0], df1.shape[1] + traces_between + df2.shape[1]))

        # Процесс интерполяции для каждой трассы
        for i in range(df1.shape[0]):
            # Получаем данные для текущей трассы из df1 и df2
            y_left = df1.iloc[i, :]
            y_right = df2.iloc[i, :]
            y_full = np.hstack([y_left, y_right])  # Объединение данных для обоих df

            # Создание функции интерполяции
            interp_function = interpolate.interp1d(x_full, y_full, kind=kind, fill_value="extrapolate")

            # Создание массива координат x для интерполяции
            x_interpolated = np.linspace(0, x_full[-1], num=df1.shape[1] + traces_between + df2.shape[1])

            # Выполнение интерполяции и заполнение данных
            interpolated_data[i, :] = interp_function(x_interpolated)

        # Возвращение DataFrame с интерполированными данными
        return pd.DataFrame(interpolated_data, index=df1.index)

    @staticmethod
    def visualize_interpolation(data, start_interp, end_interp, colormap='gray'):
        plt.figure(figsize=(10, 6))
        im = plt.imshow(data, aspect='auto', interpolation='none', cmap=colormap)
        plt.colorbar(im, label='Amplitude')
        plt.xlabel('Traces')
        plt.ylabel('Samples')
        plt.title('Interpolated Radargram')
        plt.axvline(x=start_interp, color='red', linestyle='-', linewidth=1)
        plt.axvline(x=end_interp, color='red', linestyle='-', linewidth=1)
        plt.show()


def main_interface():
    visualizer = DataVisualizer()
    interpolator = DataInterpolator(visualizer)
    visualizer.read_from_segy("initial_data/Пресный_водоём.seg")
    visualizer.scale_data()

    plt.figure(figsize=(10, 8))
    plt.subplots_adjust(left=0.25, right=0.75, bottom=0.05, top=0.95)

    rax = plt.axes([0.3, 0.85, 0.4, 0.05])
    radio = RadioButtons(rax, ['amplitudes_df', 'scaled_amplitudes_df'])

    ax_visualize = plt.axes([0.3, 0.75, 0.4, 0.05])
    btn_visualize = Button(ax_visualize, 'Visualize')

    ax_preprocess = plt.axes([0.3, 0.65, 0.4, 0.05])
    btn_preprocess = Button(ax_preprocess, 'Preprocess Image')

    rax_interpolation = plt.axes([0.3, 0.45, 0.4, 0.15])
    radio_interpolation = RadioButtons(rax_interpolation, ['linear', 'cubic', 'quadratic', 'nearest'])

    tbox = plt.axes([0.3, 0.35, 0.4, 0.05])
    text_box = TextBox(tbox, 'Traces:', initial="10")

    ax_interpolate = plt.axes([0.3, 0.25, 0.4, 0.05])
    btn_interpolate = Button(ax_interpolate, 'Interpolate')

    def visualize_data(_):
        df = visualizer.amplitudes_df if radio.value_selected == 'amplitudes_df' else visualizer.scaled_amplitudes_df
        visualizer.visualize(amplitudes_df=df)

    def preprocess(_):
        visualizer.preprocess_image()

    def interpolation_process(_):
        traces_between = int(text_box.text)
        interpolation_method = radio_interpolation.value_selected
        df = visualizer.amplitudes_df if radio.value_selected == 'amplitudes_df' else visualizer.scaled_amplitudes_df
        interpolator.visualize_interpolation(
            interpolator.interpolate_datasets(df, df, traces_between, interpolation_method),
            df.shape[1], df.shape[1] + traces_between)

    btn_visualize.on_clicked(visualize_data)
    btn_preprocess.on_clicked(preprocess)
    btn_interpolate.on_clicked(interpolation_process)

    plt.show()


main_interface()
