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
        # Проверяем, являются ли амплитуды списками, и конвертируем в массивы NumPy, если нужно
        if isinstance(amplitudes1, list):
            amplitudes1 = np.array(amplitudes1)
        if isinstance(amplitudes2, list):
            amplitudes2 = np.array(amplitudes2)

        num_samples = min(amplitudes1.shape[0], amplitudes2.shape[0])
        min_traces = min(amplitudes1.shape[1], amplitudes2.shape[1])

        interpolated_amplitudes = np.zeros((num_samples, min_traces))

        for trace in range(min_traces):
            y1 = amplitudes1[:, trace]
            y2 = amplitudes2[:, trace]

            x1 = np.linspace(0, 1, len(y1))
            x2 = np.linspace(0, 1, len(y2))
            x_new = np.linspace(0, 1, num_samples)

            spline = CubicSpline(x1, y1)
            spline2 = CubicSpline(x2, y2)

            y_new1 = spline(x_new)
            y_new2 = spline2(x_new)

            interpolated_amplitudes[:, trace] = (y_new1 + y_new2) / 2

        return interpolated_amplitudes
