import obspy
import pandas as pd


class Radargramm:
    def __init__(self, radargramm_db_companion):
        self.amplitudes_data = pd.DataFrame()
        self.name = str
        self.num_traces = int
        self.num_samples = int
        self.file_content = None
        self.radargramm_db_companion = radargramm_db_companion

    def load_data(self, file, name):
        amplitudes = []
        stream = obspy.read(file)
        for trace in stream:
            amplitudes.append(trace.data)

        # Преобразуем массивы в DataFrame
        self.amplitudes_data = pd.DataFrame(amplitudes)
        self.num_traces = len(amplitudes)
        self.num_samples = len(amplitudes[0])
        self.name = name

        # Прочитаем содержимое файла в переменную file_content
        with open(file, 'rb') as f:
            self.file_content = f.read()

        self.radargramm_db_companion.db_save(
            radargramm_name=self.name,
            file_content=self.file_content,
            num_traces=self.num_traces,
            num_samples=self.num_samples,
            amplitudes_data=self.amplitudes_data
        )
