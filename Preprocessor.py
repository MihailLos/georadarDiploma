import numpy as np
import pandas as pd
from scipy import ndimage
from sklearn.preprocessing import MinMaxScaler

from database.radargramm import RadargrammTableCompanion


class Preprocessor:
    def __init__(self):
        self.quantile_filtered_amplitudes = None
        self.corrode_filtered_amplitudes = None
        self.expand_filtered_amplitudes = None
        self.filtered_amplitudes = None
        self.scaled_amplitudes = None
        self.quantile_amplitudes = None
        self.radargramm_entity = RadargrammTableCompanion()

    def scale_data(self, amplitudes):
        scaler = MinMaxScaler()
        amplitudes_df = pd.DataFrame(amplitudes)
        self.scaled_amplitudes = pd.DataFrame(scaler.fit_transform(amplitudes_df))

    def quantile_analyze(self):
        threshold = np.percentile(self.scaled_amplitudes.values.flatten(), 10)
        filtered_amplitudes_df = (self.scaled_amplitudes > threshold).astype(int)
        self.quantile_filtered_amplitudes = filtered_amplitudes_df
        self.filtered_amplitudes = self.quantile_filtered_amplitudes

    def corrode_image(self):
        self.corrode_filtered_amplitudes = pd.DataFrame(ndimage.binary_erosion(self.quantile_filtered_amplitudes.values,
                                                                               structure=np.ones((3, 3))).astype(int))
        self.filtered_amplitudes = self.corrode_filtered_amplitudes

    def expand_image(self):
        self.expand_filtered_amplitudes = pd.DataFrame(ndimage.binary_dilation(self.corrode_filtered_amplitudes.values,
                                                                               structure=np.ones((3, 3))).astype(int))
        self.filtered_amplitudes = self.expand_filtered_amplitudes

    def interprete_results(self, radargramm_id):
        real_data = pd.DataFrame(self.radargramm_entity.db_read_radaragramm_by_id(radargramm_id))
        positions = np.where(self.filtered_amplitudes == 1)

        real_values_list = [real_data.iloc[pos] for pos in zip(*positions)]

        return real_values_list
