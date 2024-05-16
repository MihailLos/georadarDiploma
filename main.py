from GUI.main_gui import MainGUI
from database.database_setup import Database
from database.preprocessing import PreprocessingTableCompanion
from database.radargramm import RadargrammTableCompanion
from database.visualization import VisualizationResultsTableCompanion

if __name__ == '__main__':
    metadata, engine = Database.setup()

    # Инициализация классов таблиц
    preprocessing_companion = PreprocessingTableCompanion(metadata=metadata, engine=engine)
    radargramm_companion = RadargrammTableCompanion(metadata=metadata, engine=engine)
    visualization_companion = VisualizationResultsTableCompanion(metadata=metadata, engine=engine)

    # Создание всех таблиц
    metadata.create_all(engine)

    ui = MainGUI(preprocessing_companion, radargramm_companion, visualization_companion)
    ui.run()