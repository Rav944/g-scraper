from sqlite3 import Date

import argh
from sqlalchemy import Column, ForeignKey, Integer, String, create_engine, MetaData, Table, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker
import sqlite3


def main():
    try:
        engine = create_engine('sqlite:///QScraper.db')
    except Exception as e:
        print(e)
    else
        if not engine.has_table('Offer'):
            metadata = MetaData(engine)
            Table('Offer', metadata,
                  Column('Id', Integer, primary_key=True, nullable=False),
                  Column('Date', Date), Column('Country', String),
                  Column('Brand', String), Column('Price', Float),
                  )
            metadata.create_all()

if __name__ == '__main__':
    argh.dispatch_command(main)
