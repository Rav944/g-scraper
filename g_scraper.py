from collections import defaultdict

import argh
import requests
from bs4 import BeautifulSoup
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from settings import URL_ADDRESS, DOMAIN_URL, HEADERS
from tabels import Base, Department, Technologies, Offer


def main():
    try:
        engine = create_engine('sqlite:///QScraper.db', echo=True)
    except Exception as e:
        print(e)
    else:
        contain_tables = [engine.has_table('offer'), engine.has_table('department'), engine.has_table('technologies')]
        if not all(contain_tables):
            Base.metadata.create_all(bind=engine)
    page = requests.get(URL_ADDRESS)
    soup = BeautifulSoup(page.content, 'html.parser')
    for dep in soup.find_all(class_='department-job-offers'):
        department_name_raw = dep.find(class_='department-description-title').text
        data = defaultdict(str)
        data['department_name'] = department_name_raw[2:department_name_raw.find('(')].lstrip()
        for offer in dep.find_all('a', href=True):
            offer_address = DOMAIN_URL + offer['href']
            offer_page = requests.get(offer_address, headers=HEADERS)
            offer_soup = BeautifulSoup(offer_page.content, 'html.parser')
            data['name'] = offer_soup.find('h1', class_='job-offer-title').text
            data['technologies'] = [t.text for t in offer_soup.find_all('a', class_='offer-tag')]
            data['description'] = offer_soup.find(class_='job-offer-description').text
            for section in offer_soup.find_all(class_='section-bullets'):
                if section.previous_element[2:-2].strip() == 'Obowiązki':
                    data['responsibilities'] = section.text
                elif section.previous_element[2:-2].strip() == 'Wymagania stanowiska':
                    data['requirements'] = section.text
                elif section.previous_element[2:-2].strip() == 'Zalety':
                    data['pluses'] = section.text
                else:
                    data['benefits'] = section.text
            Session = sessionmaker(bind=engine)
            s = Session()
            if not s.query(Department).filter_by(name=data['department_name']).first():
                department = Department(name=data['department_name'])
                s.add(department)
            for tech in data['technologies']:
                if not s.query(Technologies).filter_by(name=tech).all():
                    technologies = Technologies(name=tech)
                    s.add(technologies)
            if s.new:
                s.commit()
            department = s.query(Department).filter_by(name=data['department_name']).all()
            technologies = s.query(Technologies).filter(Technologies.name.in_(data['technologies'])).all()
            if not s.query(Offer).join(Offer.department).filter(Offer.name == data['name'], department == department).first():
                offer = Offer(
                    name=data['name'],
                    description=data['description'],
                    department=department,
                    technologies=technologies,
                    responsibilities=data['responsibilities'],
                    requirements=data['requirements'],
                    pluses=data['pluses'],
                    benefits=data['benefits']
                )
                s.add(offer)
            s.commit()


if __name__ == '__main__':
    argh.dispatch_command(main)
