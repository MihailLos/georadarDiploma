import obspy
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.widgets import Slider, RadioButtons, Button, TextBox
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

    def visualize(self, amplitudes_df, colormap='gray'):
        fig, ax = plt.subplots(figsize=(10, 6))
        # Изменения в этом блоке
        amplitudes = amplitudes_df.values  # Удаляем транспонирование
        amplitude_min, amplitude_max = np.min(amplitudes), np.max(amplitudes)

        im = ax.imshow(amplitudes, cmap=colormap, aspect='auto')  # Удаляем транспонирование
        plt.colorbar(im, label='Signal Amplitude')
        plt.xlabel('Traces')
        plt.ylabel('Measurements')
        plt.title('Radargram')

        ax_min = plt.axes([0.2, 0.02, 0.65, 0.03])
        ax_max = plt.axes([0.2, 0.06, 0.65, 0.03])
        s_min = Slider(ax_min, 'Min Amplitude', amplitude_min, amplitude_max, valinit=amplitude_min)
        s_max = Slider(ax_max, 'Max Amplitude', amplitude_min, amplitude_max, valinit=amplitude_max)

        def update(val):
            im.set_clim([s_min.val, s_max.val])
            fig.canvas.draw_idle()

        s_min.on_changed(update)
        s_max.on_changed(update)
        plt.show()


class DataInterpolator:
    def __init__(self, visualizer):
        self.visualizer = visualizer

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

    def visualize_interpolation(self, data, start_interp, end_interp, colormap='gray'):
        plt.figure(figsize=(10, 6))
        im = plt.imshow(data, aspect='auto', interpolation='none', cmap=colormap)
        plt.colorbar(im, label='Amplitude')
        plt.xlabel('Traces')
        plt.ylabel('Samples')
        plt.title('Interpolated Radargram')

        plt.axvline(x=start_interp, color='red', linestyle='--', linewidth=2)
        plt.axvline(x=end_interp, color='red', linestyle='--', linewidth=2)

        plt.show()


# GUI and control setup
visualizer = DataVisualizer()
interpolator = DataInterpolator(visualizer)


def main_interface():
    visualizer.read_from_segy("initial_data/Пресный_водоём.seg")
    visualizer.scale_data()

    fig, ax = plt.subplots()
    plt.subplots_adjust(left=0.3, bottom=0.3)
    rax = plt.axes([0.05, 0.5, 0.15, 0.15], facecolor='lightgoldenrodyellow')
    radio = RadioButtons(rax, ('amplitudes_df', 'scaled_amplitudes_df'))

    tbox = plt.axes([0.05, 0.3, 0.1, 0.075])
    text_box = TextBox(tbox, 'Traces:', initial="10")

    ax_interpolate = plt.axes([0.05, 0.2, 0.1, 0.075])
    btn_interpolate = Button(ax_interpolate, 'Interpolate')

    def visualize_data(label):
        df = visualizer.amplitudes_df if label == 'amplitudes_df' else visualizer.scaled_amplitudes_df
        visualizer.visualize(df)

    radio.on_clicked(visualize_data)

    def interpolate(event):
        traces_between = int(text_box.text)
        df_type = radio.value_selected
        df = visualizer.amplitudes_df if df_type == 'amplitudes_df' else visualizer.scaled_amplitudes_df
        interpolator.visualize_interpolation(
            interpolator.interpolate_datasets(df, df, traces_between),
            df.shape[1], df.shape[1] + traces_between)

    btn_interpolate.on_clicked(interpolate)
    plt.show()


main_interface()