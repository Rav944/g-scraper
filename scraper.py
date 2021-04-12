from collections import defaultdict

import requests
from bs4 import BeautifulSoup
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from settings import URL_ADDRESS, DOMAIN_URL, DB_PATH
from tabels import Base, Department, Technologies, Offer


class Scrapper:
    def __init__(self):
        self.errors = []
        self.new_items = 0
        self.engine = ''
        self.session = ''
        self.department_name = ''
        self.db_tables = ['offer', 'department', 'technologies']
        self.data = defaultdict(str)
        self.creat_connection()
        if self.engine and self.session:
            self.scrap()

    def creat_connection(self):
        try:
            self.engine = create_engine(f'sqlite:///{DB_PATH}')
        except Exception as e:
            self.errors.append(e)
        else:
            if not all([self.engine.has_table(t) for t in self.db_tables]):
                Base.metadata.create_all(bind=self.engine)
        if self.engine:
            try:
                Session = sessionmaker(bind=self.engine)
            except Exception as e:
                self.errors.append(e)
            else:
                self.session = Session()

    def scrap(self):
        page = requests.get(URL_ADDRESS)
        soup = BeautifulSoup(page.content, 'html.parser')
        for dep in soup.find_all(class_='department-job-offers'):
            department_name_raw = dep.find(class_='department-description-title').text
            self.department_name = department_name_raw[2:department_name_raw.find('(')].lstrip()
            [self.offers_check(o) for o in dep.find_all('a', href=True)]

    def offers_check(self, offer):
        offer_address = DOMAIN_URL + offer['href']
        offer_page = requests.get(offer_address)
        offer_soup = BeautifulSoup(offer_page.content, 'html.parser')
        self.data['name'] = offer_soup.find('h1', class_='job-offer-title').text
        self.data['technologies'] = [t.text for t in offer_soup.find_all('a', class_='offer-tag')]
        self.data['description'] = offer_soup.find(class_='job-offer-description').text
        [self.section_check(s) for s in offer_soup.find_all(class_='section-bullets')]
        self.department_check()
        [self.technologies_check(t) for t in self.data['technologies']]
        self.save()

    def section_check(self, section):
        if section.previous_element[2:-2].strip() == 'Obowiązki':
            self.data['responsibilities'] = section.text
        elif section.previous_element[2:-2].strip() == 'Wymagania stanowiska':
            self.data['requirements'] = section.text
        elif section.previous_element[2:-2].strip() == 'Zalety':
            self.data['pluses'] = section.text
        else:
            self.data['benefits'] = section.text

    def department_check(self):
        if not self.session.query(Department).filter_by(name=self.department_name).all():
            department = Department(name=self.department_name)
            self.session.add(department)

    def technologies_check(self, tech):
        if not self.session.query(Technologies).filter_by(name=tech).all():
            technologies = Technologies(name=tech)
            self.session.add(technologies)

    def save(self):
        department = self.session.query(Department).filter_by(name=self.department_name).all()
        technologies = self.session.query(Technologies).filter(Technologies.name.in_(self.data['technologies'])).all()
        if not self.session.query(Offer).join(Offer.department).filter(Offer.name == self.data['name'],
                                                                       department == department).first():
            offer = Offer(
                name=self.data['name'],
                description=self.data['description'],
                department=department,
                technologies=technologies,
                responsibilities=self.data['responsibilities'],
                requirements=self.data['requirements'],
                pluses=self.data['pluses'],
                benefits=self.data['benefits']
            )
            self.session.add(offer)
        if self.session.new:
            self.session.commit()

    def report(self):
        if self.errors:
            print('Mission aborted, errors encountered:')
            [print(e) for e in self.errors]
        else:
            print(f"No errors detected, Mission accomplished!")
