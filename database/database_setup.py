from sqlalchemy import MetaData, create_engine


class Database:

    @staticmethod
    def setup():
        metadata = MetaData()
        engine = create_engine('sqlite:///georadar_db.sqlite', future=True, connect_args={'check_same_thread': False})
        return metadata, engine
