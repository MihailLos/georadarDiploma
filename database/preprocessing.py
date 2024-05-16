# preprocessing.py
import datetime
import json
from sqlalchemy import Table, Column, Integer, Text, LargeBinary, ForeignKey, Date
from database.database_setup import Database


class PreprocessingTableCompanion:
    def __init__(self, metadata, engine):
        self.metadata = metadata
        self.engine = engine
        self.preprocessing_results_table = self.create_preprocessing_results_table()

    def create_preprocessing_results_table(self):
        return Table(
            'preprocessing_results', self.metadata,
            Column('ID', Integer, primary_key=True),
            Column('Name', Text),
            Column('Preprocessing_Res', Text),
            Column('Preprocessing_Image', LargeBinary),
            Column('Radargramm_ID', Integer, ForeignKey('radargramms.ID')),
            Column('Date', Date)
        )

    def db_save(self, result_name, preprocessed_data, preprocessed_image, radargramm_id):
        preprocessed_data_json = json.dumps(preprocessed_data)
        with self.engine.connect() as conn:
            conn.execute(self.preprocessing_results_table.insert(), {
                'Name': result_name,
                'Preprocessing_Res': preprocessed_data_json,
                'Preprocessing_Image': preprocessed_image,
                'Radargramm_ID': radargramm_id,
                'Date': datetime.date.today()
            })
            conn.commit()

    def db_read_all_preprocess_results(self):
        with self.engine.connect() as conn:
            select_query = self.preprocessing_results_table.select()
            results = conn.execute(select_query).fetchall()
            for result in results:
                result['Preprocessing_Res'] = json.loads(result['Preprocessing_Res'])
            return results
