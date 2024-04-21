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
        return pd.DataFrame(data).T  # Транспонируем для корректной работы с данными

    def interpolate_datasets(self, df1, df2, traces_between):
        # Проверяем, что количество трасс в обоих датасетах одинаково
        if df1.shape[1] != df2.shape[1]:
            raise ValueError("Datasets must have the same number of traces")

        # Рассчитываем новое количество трасс
        new_trace_count = df1.shape[1] + df2.shape[1] + traces_between

        # Инициализируем массив для интерполированных данных
        interpolated_data = np.zeros((df1.shape[0], new_trace_count))

        # Заполняем первый датасет
        interpolated_data[:, :df1.shape[1]] = df1

        # Начальный индекс для второго датасета
        start_second_dataset = df1.shape[1] + traces_between

        # Заполняем данные второго датасета
        interpolated_data[:, start_second_dataset:start_second_dataset + df2.shape[1]] = df2

        # Интерполируем между последней трассой первого и первой трассой второго датасета
        start_value = df1.iloc[:, -1]
        end_value = df2.iloc[:, 0]
        for i in range(df1.shape[0]):
            interpolated_data[i, df1.shape[1]:start_second_dataset] = np.linspace(start_value[i], end_value[i],
                                                                                  traces_between + 2)[1:-1]

        return pd.DataFrame(interpolated_data)

    def visualize(self, data):
        plt.figure(figsize=(10, 6))
        plt.imshow(data, aspect='auto', interpolation='none', cmap='gray')
        plt.colorbar(label='Amplitude')
        plt.xlabel('Traces')
        plt.ylabel('Samples')
        plt.title('Interpolated Radargram')
        plt.show()


# Example usage
radargramm = Radargramm()
data1 = radargramm.read_from_segy("initial_data/Пресный_водоём.seg")
data2 = radargramm.read_from_segy("initial_data/Пресный_водоём.seg")  # Возможно, у вас другой файл
traces_between = int(input("Enter the number of new traces to interpolate between existing traces: "))
interpolated_data = radargramm.interpolate_datasets(data1, data2, traces_between)
radargramm.visualize(interpolated_data)