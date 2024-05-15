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

        min_num_samples = min(amplitudes1.shape[0], amplitudes2.shape[0], num_samples)
        num_traces = min(amplitudes1.shape[1], amplitudes2.shape[1])
        interpolated_amplitudes = np.zeros((min_num_samples, num_traces))

        for trace in range(num_traces):
            y1 = amplitudes1.iloc[:, trace].values[:min_num_samples]
            y2 = amplitudes2.iloc[:, trace].values[:min_num_samples]

            x1 = np.linspace(0, 1, min_num_samples)
            x2 = np.linspace(0, 1, min_num_samples)
            x_new = np.linspace(0, 1, min_num_samples)

            interpolated_values = np.array([
                Interpolator.lagrange_polynomial(x1, y1, x) for x in x_new
            ])

            interpolated_amplitudes[:, trace] = interpolated_values

        return pd.DataFrame(interpolated_amplitudes, columns=amplitudes1.columns[:num_traces])

