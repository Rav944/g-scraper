import argh

from scraper import Scrapper


def main():
    s = Scrapper()
    s.report()


if __name__ == '__main__':
    argh.dispatch_command(main)
