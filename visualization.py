import obspy
import matplotlib.pyplot as plt
from matplotlib.widgets import Slider
import numpy as np
from scipy import ndimage
from sklearn.cluster import DBSCAN, KMeans
from sklearn.neighbors import KNeighborsClassifier
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

    def visualize(self, amplitudes_df, colormap='rainbow', amplitude_range=None):
        fig, ax = plt.subplots(figsize=(10, 6))

        amplitudes = amplitudes_df.values  # Преобразуем DataFrame обратно в массив numpy

        if amplitude_range is not None:
            min_amplitude, max_amplitude = amplitude_range
            amplitudes = np.clip(amplitudes, min_amplitude, max_amplitude)

        time_labels = np.linspace(0, len(amplitudes[0]), len(amplitudes[0]))
        im = ax.imshow(amplitudes.T, cmap=colormap, aspect='auto',
                       extent=[0, len(amplitudes), time_labels[-1], time_labels[0]])
        plt.colorbar(im, label='Амплитуда сигнала')
        plt.xlabel('Трассы')
        plt.ylabel('Измерения')
        plt.title('Радарограмма')
        plt.show()

    def scale_data(self):
        scaler = MinMaxScaler()
        self.scaled_amplitudes_df = pd.DataFrame(scaler.fit_transform(self.amplitudes_df))

    def preprocess_image(self, method=1):
        if method == 1:
            binary_image_quantile = self.quantile_analysis()
            self.visualize_preprocessing_results(binary_image_quantile, title='Квантильный анализ')
        elif method == 2:
            corroded_image = self.corrode_image()
            self.visualize_preprocessing_results(corroded_image, title='Травление')
        elif method == 3:
            expanded_image = self.expand_image()
            self.visualize_preprocessing_results(expanded_image, title='Расширение сигналов')

    def quantile_analysis(self):
        threshold = np.percentile(self.scaled_amplitudes_df.values.flatten(), 10)
        return (self.scaled_amplitudes_df > threshold).astype(int)

    def corrode_image(self):
        binary_image_quantile = self.quantile_analysis()
        return ndimage.binary_erosion(binary_image_quantile.values, structure=np.ones((3, 3))).astype(int)

    def expand_image(self):
        corroded_image = self.corrode_image()
        return ndimage.binary_dilation(corroded_image, structure=np.ones((3, 3))).astype(int)

    def visualize_preprocessing_results(self, image, title):
        fig, ax = plt.subplots(figsize=(10, 6))
        ax.imshow(image.T, cmap='gray', aspect='auto')
        ax.set_title(title)
        ax.set_xlabel('Трассы')
        ax.set_ylabel('Измерения')
        plt.show()

def interpolate_dataframes(amplitudes_df_first, amplitudes_df_second, degree=3):
    interpolated_dfs = []
    # Проверяем, что оба датафрейма имеют одинаковое количество столбцов
    if amplitudes_df_first.shape[1] != amplitudes_df_second.shape[1]:
        raise ValueError("Both dataframes must have the same number of columns.")

        # Интерполируем значения для каждой пары столбцов
    for col1, col2 in zip(amplitudes_df_first.columns, amplitudes_df_second.columns):
        x1 = amplitudes_df_first[col1].values
        y1 = amplitudes_df_first[col2].values
        x2 = amplitudes_df_second[col1].values

        # Выполняем полиномиальную интерполяцию
        coeffs = np.polyfit(x1, y1, deg=degree)
        poly_func = np.poly1d(coeffs)

        # Оцениваем значения полинома для точек между данными
        interpolated_values = poly_func(x2)

        # Создаем новый датафрейм с интерполированными значениями
        interpolated_df = pd.DataFrame({col1: x2, col2: interpolated_values})
        interpolated_dfs.append(interpolated_df)

    return pd.concat(interpolated_dfs, axis=1)


def lagrange_polynomial(x, y, xi):
    n = len(x)
    result = 0.0
    for i in range(n):
        term = y[i]
        for j in range(n):
            if i != j:
                term *= (xi - x[j]) / (x[i] - x[j])
        result += term
    return result


def dataframe_polynomial_interpolation(df1, df2, num_points):
    num_cols_df1 = df1.shape[1]
    num_cols_df2 = df2.shape[1]

    min_num_cols = min(num_cols_df1, num_cols_df2)
    num_points = min(num_points, min_num_cols)  # Проверяем, не превышает ли num_points минимальное количество столбцов

    if num_cols_df1 < min_num_cols:
        df1_selected = df1.iloc[:, -min_num_cols:]
    else:
        df1_selected = df1.iloc[:, -num_points:]

    if num_cols_df2 < min_num_cols:
        df2_selected = df2.iloc[:, :min_num_cols]
    else:
        df2_selected = df2.iloc[:, :num_points]

    interpolated_df = pd.DataFrame(columns=df2.columns)

    for column in df2.columns:  # Интерполируем каждый столбец DataFrame
        x = np.linspace(0, 1, num_points)
        y1 = df1_selected[column].values[-num_points:]  # Берем последние num_points значений из столбца df1
        y2 = df2_selected[column].values[:num_points]  # Берем первые num_points значений из столбца df2

        min_num_points = min(len(y1), len(y2))

        interpolated_values = np.array(
            [lagrange_polynomial([0, 1], [y1[j], y2[j]], t) for j, t in enumerate(x[:min_num_points])])

        interpolated_df[column] = interpolated_values

    return interpolated_df


radargramm = Radargramm()
radargramm2 = Radargramm()

radargramm.read_from_segy("initial_data/Пресный_водоём.seg")
radargramm2.read_from_segy("initial_data/Арматура.seg")
radargramm.scale_data()
radargramm2.scale_data()

f = dataframe_polynomial_interpolation(radargramm.scaled_amplitudes_df, radargramm.scaled_amplitudes_df, 2000)
print(radargramm.amplitudes_df)
print(f)

radargramm.visualize(f, colormap='gray')
radargramm.visualize(radargramm.scaled_amplitudes_df, colormap='gray')