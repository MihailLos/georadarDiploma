from sqlalchemy import Table, Column, Integer, Text, LargeBinary, Float, ForeignKey, Date, select

from database.database_setup import Database


class VisualizationResultsTableCompanion:
    def __init__(self, metadata, engine):
        self.metadata = metadata
        self.engine = engine
        self.visualization_results_table = self.create_visualisation_results_table()

    def create_visualisation_results_table(self):
        return Table(
            'visualization_results', self.metadata,
            Column('ID', Integer, primary_key=True),
            Column('Colormap', Text),
            Column('Image_File', LargeBinary),
            Column('Upper_Limit', Float),
            Column('Lower_Limit', Float),
            Column('Radargramm_ID', Integer, ForeignKey('radargramms.ID')),
            Column('Date', Date)
        )

    def db_save(self, colormap, image_file, upper_limit, lower_limit, radargramm_id, date):
        with self.engine.connect() as conn:
            if lower_limit is not None and upper_limit is not None:
                conn.execute(self.visualization_results_table.insert(), {
                    'Colormap': colormap,
                    'Image_File': image_file,
                    'Upper_Limit': upper_limit,
                    'Lower_Limit': lower_limit,
                    'Radargramm_ID': radargramm_id,
                    'Date': date
                })
            else:
                conn.execute(self.visualization_results_table.insert(), {
                    'Colormap': colormap,
                    'Image_File': image_file,
                    'Radargramm_ID': radargramm_id,
                    'Date': date
                })
            conn.commit()

    def db_read_all_visualizations(self):
        with self.engine.connect() as conn:
            select_query = self.visualization_results_table.select()
            results = conn.execute(select_query).fetchall()
            return results

    def db_read_visualization_by_id(self, id):
        with self.engine.connect() as conn:
            select_query = select(self.visualization_results_table.c).where(
                self.visualization_results_table.c["ID"] == id)
            result = conn.execute(select_query).fetchone()
            return result

    def db_delete_visualization_by_id(self, id):
        with self.engine.connect() as conn:
            conn.execute(
                self.visualization_results_table.delete().where(self.visualization_results_table.c["ID"] == id))
            conn.commit()
