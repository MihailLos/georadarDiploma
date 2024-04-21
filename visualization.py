import obspy
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


class Radargramm:
    def __init__(self):
        self.amplitudes_df = pd.DataFrame()

    def read_from_segy(self, filepath):
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

    def visualize(self, data, start_interp=None, end_interp=None, colormap='gray'):
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
        df1 = self.read_from_segy(file1)
        df2 = self.read_from_segy(file2)
        interpolated_data = self.interpolate_datasets(df1, df2, traces_between)
        start_interp = df1.shape[1]
        end_interp = start_interp + traces_between
        self.visualize(interpolated_data, start_interp=start_interp, end_interp=end_interp)


# Example usage
radargramm = Radargramm()
traces_between = int(input("Enter the number of new traces to interpolate between existing traces: "))
radargramm.interpolate_and_visualize("initial_data/Пресный_водоём.seg",
                                     "initial_data/Пресный_водоём.seg",
                                     traces_between)
