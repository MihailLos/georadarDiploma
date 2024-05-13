import pandas as pd
import obspy


class Interpolator:
    def __init__(self):
        self.interpolated_amplitudes = None
        self.extracted_amplitude_dataframes = []
        self.extracted_num_traces = []
        self.extracted_num_samples = []
        self.extracted_names = []
        self.interpolated_num_traces = None
        self.interpolated_num_samples = None

    def interpolate(self):
        self.interpolated_amplitudes = pd.concat(self.extracted_amplitude_dataframes)

    def load_radargramms(self, files, names):
        for name in names:
            self.extracted_names.append(name)

        for file in files:
            stream = obspy.read(file)
            for trace in stream:
                extracted_amplitude = [trace.data]
                self.extracted_amplitude_dataframes.append(pd.DataFrame(extracted_amplitude))
                self.extracted_num_traces = len(extracted_amplitude)
                self.extracted_num_samples = len(extracted_amplitude[0])