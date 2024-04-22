import obspy
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.widgets import Button, TextBox, RadioButtons
from scipy import ndimage
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
    def interpolate_datasets(df1, df2, traces_between):
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

    plt.figure(figsize=(8, 6))
    plt.subplots_adjust(left=0.25, right=0.75, bottom=0.25)

    rax = plt.axes([0.35, 0.7, 0.3, 0.15])
    radio = RadioButtons(rax, ['amplitudes_df', 'scaled_amplitudes_df'])

    ax_preprocess = plt.axes([0.35, 0.5, 0.3, 0.075])
    btn_preprocess = Button(ax_preprocess, 'Preprocess Image')

    ax_visualize = plt.axes([0.35, 0.6, 0.3, 0.075])
    btn_visualize = Button(ax_visualize, 'Visualize')

    tbox = plt.axes([0.35, 0.2, 0.3, 0.075])
    text_box = TextBox(tbox, 'Traces:', initial="10")

    ax_interpolate = plt.axes([0.35, 0.1, 0.3, 0.075])
    btn_interpolate = Button(ax_interpolate, 'Interpolate')

    def visualize_data(_):
        df = visualizer.amplitudes_df if radio.value_selected == 'amplitudes_df' else visualizer.scaled_amplitudes_df
        DataVisualizer.visualize(df)

    def preprocess(_):
        visualizer.preprocess_image()

    def interpolate(_):
        traces_between = int(text_box.text)
        df = visualizer.amplitudes_df if radio.value_selected == 'amplitudes_df' else visualizer.scaled_amplitudes_df
        DataInterpolator.visualize_interpolation(
            DataInterpolator.interpolate_datasets(df, df, traces_between),
            df.shape[1], df.shape[1] + traces_between)

    btn_visualize.on_clicked(visualize_data)
    btn_preprocess.on_clicked(preprocess)
    btn_interpolate.on_clicked(interpolate)
    plt.show()


main_interface()
