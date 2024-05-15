import datetime

from sqlalchemy import MetaData, create_engine, Table, Column, Integer, Text, ARRAY, Float, LargeBinary, ForeignKey, \
    Date

from database.DB_connect import DBConnector


class PreprocessingTableCompanion:
    metadata = MetaData()
    engine = create_engine(DBConnector.db_uri, future=True)

    preprocessing_results_table = Table('preprocessing_results', metadata,
                                        Column('ID', Integer, primary_key=True),
                                        Column('Name', Text),
                                        Column('Preprocessing_Res', ARRAY(Float)),
                                        Column('Preprocessing_Image', LargeBinary),
                                        Column('Radargramm_ID', Integer, ForeignKey('radargramms.ID')),
                                        Column('Date', Date))

    def db_save(self, result_name, preprocessed_data, preprocessed_image, radargramm_id):
        with self.engine.connect() as conn:
            conn.execute(self.preprocessing_results_table.insert(), {
                'Name': result_name,
                'Preprocessing_Res': preprocessed_data,
                'Preprocessing_Image': preprocessed_image,
                'Radargramm_ID': radargramm_id,
                'Date': datetime.date.today()
            })

            conn.commit()
            self.engine.connect().connection.close()

    def db_read_all_preprocess_results(self):
        select_query = self.preprocessing_results_table.select()
        result = self.engine.connect().execute(select_query)
        return result.fetchall()

    def db_delete_preprocess_result_by_id(self, id):
        with self.engine.connect() as conn:
            conn.execute(self.preprocessing_results_table.delete().where(self.preprocessing_results_table.c["ID"] == id))
            conn.commit()
            self.engine.connect().connection.close()