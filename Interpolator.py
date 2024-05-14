import numpy as np
from scipy.interpolate import lagrange, CubicSpline


class Interpolator:
    def __init__(self):
        self.extracted_amplitude_dataframes = []
        self.extracted_num_traces = []
        self.extracted_num_samples = []
        self.extracted_names = []
        self.interpolated_num_traces = None
        self.interpolated_num_samples = None

    def interpolated_amplitudes(self, amplitudes1, amplitudes2):
        if isinstance(amplitudes1, list):
            amplitudes1 = np.array(amplitudes1)
        if isinstance(amplitudes2, list):
            amplitudes2 = np.array(amplitudes2)

        min_traces = min(amplitudes1.shape[1], amplitudes2.shape[1])
        num_points = amplitudes1.shape[0] + amplitudes2.shape[0]
        interpolated_amplitudes = np.zeros((num_points, min_traces))

        for trace in range(min_traces):
            # Объединяем данные обоих массивов для каждой трассы
            all_amplitudes = np.concatenate([amplitudes1[:, trace], amplitudes2[:, trace]])
            x = np.linspace(0, 1, len(all_amplitudes))
            x_new = np.linspace(0, 1, num_points)

            spline = CubicSpline(x, all_amplitudes)
            interpolated_amplitudes[:, trace] = spline(x_new)

        return interpolated_amplitudes
