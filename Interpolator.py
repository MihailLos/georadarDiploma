import numpy as np
import pandas as pd
from sklearn.metrics import mean_squared_error, r2_score, mean_absolute_error


class Interpolator:
    def __init__(self):
        self.extracted_amplitude_dataframes = []
        self.extracted_num_traces = []
        self.extracted_num_samples = []
        self.extracted_names = []
        self.interpolated_num_traces = None
        self.interpolated_num_samples = None

    @staticmethod
    def calculate_metrics(amplitudes1, amplitudes2, interpolated_amplitudes):
        if isinstance(amplitudes1, pd.DataFrame):
            amplitudes1 = amplitudes1.values.flatten()
        if isinstance(amplitudes2, pd.DataFrame):
            amplitudes2 = amplitudes2.values.flatten()
        if isinstance(interpolated_amplitudes, pd.DataFrame):
            interpolated_amplitudes = interpolated_amplitudes.values.flatten()

        combined_amplitudes = np.concatenate((amplitudes1, amplitudes2))
        true_values = np.tile(combined_amplitudes, 2)[:len(interpolated_amplitudes)]

        rmse = np.sqrt(mean_squared_error(true_values, interpolated_amplitudes))
        mae = mean_absolute_error(true_values, interpolated_amplitudes)
        r2 = r2_score(true_values, interpolated_amplitudes)

        max_val = np.max(combined_amplitudes)
        min_val = np.min(combined_amplitudes)
        range_val = max_val - min_val

        rmse_percentage = (rmse / range_val) * 100
        mae_percentage = (mae / range_val) * 100

        return rmse, rmse_percentage, mae, mae_percentage, r2

    @staticmethod
    def interpolated_amplitudes(amplitudes1, amplitudes2, num_samples=300, degree=16):
        if isinstance(amplitudes1, list):
            amplitudes1 = pd.DataFrame(amplitudes1)
        if isinstance(amplitudes2, list):
            amplitudes2 = pd.DataFrame(amplitudes2)

        if amplitudes1.shape[1] != amplitudes2.shape[1]:
            return None

        interpolated_amplitudes_list = []

        for col in amplitudes1.columns:
            x1 = np.linspace(0, 1, len(amplitudes1))
            y1 = amplitudes1[col].values
            x2 = np.linspace(0, 1, len(amplitudes2))
            y2 = amplitudes2[col].values

            x_new = np.linspace(0, 1, num_samples)

            coefficients = np.polyfit(np.concatenate((x1, x2)), np.concatenate((y1, y2)), deg=degree)
            poly_func = np.poly1d(coefficients)

            interpolated_values = poly_func(x_new)

            interpolated_amplitudes_list.append(pd.DataFrame(interpolated_values, columns=[col]))

        interpolated_amplitudes = pd.concat(interpolated_amplitudes_list, axis=1)

        rmse, rmse_percentage, mae, mae_percentage, r2 = Interpolator.calculate_metrics(
            amplitudes1,
            amplitudes2,
            interpolated_amplitudes,
        )

        print("\nСравнение вырезанной и интерполированной части данных:")
        print(f"Среднеквадратичная ошибка (RMSE): {rmse:.2f}")
        print(f"Среднеквадратичная ошибка (RMSE) в процентах: {rmse_percentage:.2f}%")
        print(f"Средняя абсолютная ошибка (MAE): {mae:.2f}")
        print(f"Средняя абсолютная ошибка (MAE) в процентах: {mae_percentage:.2f}%")
        print(f"Коэффициент детерминации (R²): {r2:.2f}")

        return interpolated_amplitudes
