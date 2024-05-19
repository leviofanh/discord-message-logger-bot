from sqlalchemy import create_engine, Column, Integer, String, DateTime, MetaData, Table
from sqlalchemy.orm import sessionmaker, declarative_base
from datetime import datetime

Base = declarative_base()


def connect_to_database(database_url):
    engine = create_engine(database_url)
    Session = sessionmaker(bind=engine)
    session = Session()
    return session


def create_channel_table(session, channel_id):
    table_name = str(channel_id)

    if table_name in Base.metadata.tables:
        for cls in Base.registry._class_registry.values():
            if hasattr(cls, '__tablename__') and cls.__tablename__ == table_name:
                return cls

    Message = type(
        f'Message_{channel_id}',
        (Base,),
        {
            '__tablename__': table_name,
            '__table_args__': {'extend_existing': True},
            'message_id': Column(Integer, primary_key=True),
            'username': Column(String),
            'message': Column(String),
            'published': Column(DateTime),
            'updated': Column(DateTime),
            'path': Column(String),
        }
    )

    Base.metadata.create_all(session.bind)
    return Message


class AllowedChannels(Base):
    __tablename__ = 'allowed_channels'
    channel_id = Column(Integer, primary_key=True)
