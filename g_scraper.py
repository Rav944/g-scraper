
import argh
from sqlalchemy import create_engine

from tabels import Base


def main():
    try:
        engine = create_engine('sqlite:///QScraper.db', echo=True)
    except Exception as e:
        print(e)
    else:
        contain_tables = [engine.has_table('offer'), engine.has_table('department'), engine.has_table('technologies')]
        if not all(contain_tables):
            Base.metadata.create_all(bind=engine)


if __name__ == '__main__':
    argh.dispatch_command(main)
