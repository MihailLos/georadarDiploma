from sqlalchemy import MetaData, create_engine, Table, Column, Integer, Text, LargeBinary, Float, ForeignKey, Date, \
    select

from database.DB_connect import DBConnector


class VisualizationResultsTableCompanion:
    metadata = MetaData()
    engine = create_engine(DBConnector.db_uri)

    visualization_results_table = Table('visualization_results', metadata,
                                        Column('ID', Integer, primary_key=True),
                                        Column('Colormap', Text),
                                        Column('Image_File', LargeBinary),
                                        Column('Upper_Limit', Float),
                                        Column('Lower_Limit', Float),
                                        Column('Radargramm_ID', Integer, ForeignKey('radargramms.ID')),
                                        Column('Date', Date))

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

                conn.commit()
                self.engine.connect().connection.close()
            else:
                conn.execute(self.visualization_results_table.insert(), {
                    'Colormap': colormap,
                    'Image_File': image_file,
                    'Radargramm_ID': radargramm_id,
                    'Date': date
                })

                conn.commit()
                self.engine.connect().connection.close()

    def db_read_all_visualizations(self):
        select_query = self.visualization_results_table.select()
        result = self.engine.connect().execute(select_query)
        return result.fetchall()

    def db_read_visualization_by_id(self, id):
        select_query = self.visualization_results_table.select().where(self.visualization_results_table.c["ID"] == id)
        result = self.engine.connect().execute(select_query)
        return result.fetchone()

    def db_delete_visualization_by_id(self, id):
        with self.engine.connect() as conn:
            conn.execute(self.visualization_results_table.delete().where(self.visualization_results_table.c["ID"] == id))
            conn.commit()
            self.engine.connect().connection.close()