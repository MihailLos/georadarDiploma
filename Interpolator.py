import numpy as np
import pandas as pd


class Interpolator:
    def __init__(self):
        self.extracted_amplitude_dataframes = []
        self.extracted_num_traces = []
        self.extracted_num_samples = []
        self.extracted_names = []
        self.interpolated_num_traces = None
        self.interpolated_num_samples = None

    @staticmethod
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

    def interpolated_amplitudes(self, amplitudes1, amplitudes2, num_samples=300):
        if isinstance(amplitudes1, list):
            amplitudes1 = pd.DataFrame(amplitudes1)
        if isinstance(amplitudes2, list):
            amplitudes2 = pd.DataFrame(amplitudes2)

        if amplitudes1.shape[1] != amplitudes2.shape[1]:
            return None

        interpolated_amplitudes = pd.DataFrame()

        for col in amplitudes1.columns:
            x1 = np.linspace(0, 1, len(amplitudes1))
            y1 = amplitudes1[col].values
            x2 = np.linspace(0, 1, len(amplitudes2))
            y2 = amplitudes2[col].values

            x_new = np.linspace(0, 1, num_samples)

            coeffs = np.polyfit(np.concatenate((x1, x2)), np.concatenate((y1, y2)), deg=24)
            poly_func = np.poly1d(coeffs)

            interpolated_values = poly_func(x_new)

            interpolated_amplitudes[col] = interpolated_values

        return interpolated_amplitudes
