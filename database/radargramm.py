import datetime

from sqlalchemy import Table, MetaData, Integer, Column, Text, Date, LargeBinary, create_engine, Float, ForeignKey, \
    ARRAY, select

from database.DB_connect import DBConnector


class RadargrammTableCompanion:
    metadata = MetaData()
    engine = create_engine(DBConnector.db_uri, future=True)
    radargramm_table = Table('radargramms', metadata,
                             Column('ID', Integer, primary_key=True),
                             Column('Load_Date', Date),
                             Column('Name', Text),
                             Column('File_Contents', LargeBinary),
                             Column('Num_Traces', Integer),
                             Column('Num_Samples', Integer))

    signals_table = Table('signals', metadata,
                          Column('ID', Integer, primary_key=True),
                          Column('Amplitudes', ARRAY(Float)),
                          Column('Radargramm_ID', Integer, ForeignKey('radargramms.ID')))

    def db_save(self, radargramm_name, file_content, num_traces, num_samples, amplitudes_data, load_date=datetime.date.today()):
        with self.engine.connect() as conn:
            radargramm_id = conn.execute(self.radargramm_table.insert(), [{
                'Load_Date': load_date,
                'Name': radargramm_name,
                'File_Contents': file_content,
                'Num_Traces': num_traces,
                'Num_Samples': num_samples
            }]).inserted_primary_key[0]

            amplitudes_array = []
            for trace_data in amplitudes_data.values:
                amplitudes_array.append(trace_data.tolist())

            conn.execute(self.signals_table.insert(), {
                'Amplitudes': amplitudes_array,
                'Radargramm_ID': radargramm_id
            })

            conn.commit()
            self.engine.connect().connection.close()

            return [True, 'Радарограмма загружена успешно!']

    def db_read_radargramms(self):
        select_query = self.radargramm_table.select()
        result = self.engine.connect().execute(select_query)
        return result.fetchall()

    def db_read_radaragramm_by_id(self, id):
        select_query = select(self.signals_table.c["Amplitudes"]).where(self.signals_table.c.Radargramm_ID == id)
        result = self.engine.connect().execute(select_query)
        fetch = result.fetchall()
        first_elem = fetch[0]
        nested_list = first_elem[0]
        return nested_list

    def db_delete_radargramm_by_id(self, id):
        with self.engine.connect() as conn:
            conn.execute(self.signals_table.delete().where(self.signals_table.c.Radargramm_ID == id))
            conn.execute(self.radargramm_table.delete().where(self.radargramm_table.c.ID == id))

            conn.commit()
            self.engine.connect().connection.close()

            return [True, 'Радарограмма удалена успешно!']

    def db_get_binary_by_id(self, id):
        select_query = select(self.signals_table.c["File_Contents"]).where(self.signals_table.c.Radargramm_ID == id)
        result = self.engine.connect().execute(select_query)
        fetch = result.fetchone()

        return fetch

