import numpy as np
import pandas as pd
from scipy.interpolate import CubicSpline

class Interpolator:
    def __init__(self):
        self.extracted_amplitude_dataframes = []
        self.extracted_num_traces = []
        self.extracted_num_samples = []
        self.extracted_names = []
        self.interpolated_num_traces = None
        self.interpolated_num_samples = None

    def interpolated_amplitudes(self, amplitudes1, amplitudes2, num_samples=1000):
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

            spline = CubicSpline(x1, y1)
            spline2 = CubicSpline(x2, y2)

            y_new1 = spline(x_new)
            y_new2 = spline2(x_new)

            interpolated_amplitudes[:, trace] = (y_new1 + y_new2) / 2

        return pd.DataFrame(interpolated_amplitudes, columns=amplitudes1.columns[:num_traces])

