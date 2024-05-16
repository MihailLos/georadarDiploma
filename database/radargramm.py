import datetime
import json
from sqlalchemy import Table, Integer, Column, Text, Date, LargeBinary, ForeignKey, select

from database.database_setup import Database


class RadargrammTableCompanion:
    def __init__(self, metadata, engine):
        self.metadata = metadata
        self.engine = engine
        self.radargramm_table = self.create_radargramm_table()
        self.signals_table = self.create_signals_table()

    def create_radargramm_table(self):
        return Table(
            'radargramms', self.metadata,
            Column('ID', Integer, primary_key=True),
            Column('Load_Date', Date),
            Column('Name', Text),
            Column('File_Contents', LargeBinary),
            Column('Num_Traces', Integer),
            Column('Num_Samples', Integer)
        )

    def create_signals_table(self):
        return Table(
            'signals', self.metadata,
            Column('ID', Integer, primary_key=True),
            Column('Amplitudes', Text),
            Column('Radargramm_ID', Integer, ForeignKey('radargramms.ID'))
        )

    def db_save(self, radargramm_name, file_content, num_traces, num_samples, amplitudes_data,
                load_date=datetime.date.today()):
        with self.engine.connect() as conn:
            radargramm_id = conn.execute(self.radargramm_table.insert(), {
                'Load_Date': load_date,
                'Name': radargramm_name,
                'File_Contents': file_content,
                'Num_Traces': num_traces,
                'Num_Samples': num_samples
            }).inserted_primary_key[0]

            amplitudes_json = json.dumps(amplitudes_data.values.tolist())
            conn.execute(self.signals_table.insert(), {
                'Amplitudes': amplitudes_json,
                'Radargramm_ID': radargramm_id
            })

            conn.commit()

    def db_read_radargramms(self):
        with self.engine.connect() as conn:
            select_query = self.radargramm_table.select()
            results = conn.execute(select_query).fetchall()
            return results

    def db_read_radaragramm_by_id(self, id):
        with self.engine.connect() as conn:
            select_query = select(self.signals_table.c["Amplitudes"]).where(self.signals_table.c.Radargramm_ID == id)
            result = conn.execute(select_query).fetchone()
            if result:
                return json.loads(result['Amplitudes'])
            else:
                return None

    def db_delete_radargramm_by_id(self, id):
        with self.engine.connect() as conn:
            conn.execute(self.signals_table.delete().where(self.signals_table.c.Radargramm_ID == id))
            conn.execute(self.radargramm_table.delete().where(self.radargramm_table.c.ID == id))
            conn.commit()

    def db_get_binary_by_id(self, id):
        with self.engine.connect() as conn:
            select_query = select(self.radargramm_table.c["File_Contents"]).where(self.radargramm_table.c.ID == id)
            result = conn.execute(select_query).fetchone()
            if result:
                return result['File_Contents']
            else:
                return None
