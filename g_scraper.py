import argh
from sqlalchemy import Column, ForeignKey, Integer, String, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker
import sqlite3


def main():
    try:
        conn = sqlite3.connect('QScraper.db')
    except Exception as e:
        print(e)
    else:
        c = conn.cursor()
        c.execute(''' SELECT 'offers' FROM sqlite_master WHERE type='table' ''')
        baza = create_engine('sqlite:///test.db')  # ':memory:'

        BazaModel = declarative_base()
        class Uczen(conn):
            __tablename__ = 'uczen'
            id = Column(Integer, primary_key=True)
            imie = Column(String(100), nullable=False)
            nazwisko = Column(String(100), nullable=False)
            klasa_id = Column(Integer, ForeignKey('klasa.id'))


if __name__ == '__main__':
    argh.dispatch_command(main)
