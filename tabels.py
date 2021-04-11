from sqlalchemy import Column, Integer, String, Table, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()

department_association = Table(
    'department_association', Base.metadata,
    Column('offer_id', Integer, ForeignKey('offer.id')),
    Column('department_id', Integer, ForeignKey('department.id'))
    )

technologies_association = Table(
    'technologies_association', Base.metadata,
    Column('offer_id', Integer, ForeignKey('offer.id')),
    Column('technologies_id', Integer, ForeignKey('technologies.id'))
    )


class Offer(Base):
    __tablename__ = 'offer'
    id = Column('id', Integer, primary_key=True, nullable=False)
    name = Column('name', String)
    description = Column('description', String)
    department = relationship('Department', secondary=department_association, backref='offer')
    technologies = relationship('Technologies', secondary=technologies_association, backref='offer')
    responsibilities = Column('responsibilities', String)
    requirements = Column('requirements', String)
    pluses = Column('pluses', String)
    benefits = Column('benefits', String)


class Department(Base):
    __tablename__ = 'department'
    id = Column('id', Integer, primary_key=True, nullable=False)
    name = Column('name', String)


class Technologies(Base):
    __tablename__ = 'technologies'
    id = Column('id', Integer, primary_key=True, nullable=False)
    name = Column('name', String)
