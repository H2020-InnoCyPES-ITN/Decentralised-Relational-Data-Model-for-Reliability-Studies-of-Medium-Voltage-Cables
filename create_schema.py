#Connect to postgresql database and create a table

from sqlalchemy import create_engine, MetaData
from sqlalchemy.orm import declarative_base
from sqlalchemy import Column, Integer, String, Boolean, Date, ForeignKey, Float
from sqlalchemy.exc import ProgrammingError
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.sql import select, func
from sqlalchemy.orm import sessionmaker, relationship
from geoalchemy2 import Geometry
from sqlalchemy.sql import text

# Replace the following with your own details
db_username = 'postgres'
db_password = 'ESR9'
db_host = 'localhost'  # or the IP address of your database server
db_port = '5432'
db_name = 'MyDB'

# Create the database engine
engine = create_engine(f'postgresql+psycopg2://{db_username}:{db_password}@{db_host}:{db_port}/{db_name}')
# The name of the database you want to drop and create
DATABASE_NAME = "MyDB"
# Connect to the PostgreSQL server
with engine.connect() as conn:
    conn.execution_options(isolation_level="AUTOCOMMIT")

    # Drop the database if it exists
    try:
        conn.execute(text(f"DROP DATABASE IF EXISTS {DATABASE_NAME}"))
        print(f"Database {DATABASE_NAME} dropped.")
    except ProgrammingError as e:
        print(f"Error dropping database {DATABASE_NAME}: {e}")

    # Create the database
    try:
        conn.execute(text(f"CREATE DATABASE {DATABASE_NAME}"))
        print(f"Database {DATABASE_NAME} created.")
    except ProgrammingError as e:
        print(f"Error creating database {DATABASE_NAME}: {e}")

with engine.connect() as conn:
    conn.execution_options(isolation_level="AUTOCOMMIT")
    
    # Enable PostGIS extension
    try:
        conn.execute(text("CREATE EXTENSION IF NOT EXISTS postgis"))
        print(f"PostGIS extension enabled for {DATABASE_NAME}.")
    except ProgrammingError as e:
        print(f"Error enabling PostGIS extension for {DATABASE_NAME}: {e}")
#NOTE: THE CODE deletes all tables from the database except the required tables for PostGIS

# Create a MetaData instance
metadata = MetaData()

# Reflect the current database tables
metadata.reflect(bind=engine)

# List of required table names for PostGIS
required_tables = ['spatial_ref_sys']

# Drop all tables except the required tables
for table in reversed(metadata.sorted_tables):
    if table.name not in required_tables:
        table.drop(bind=engine)

print("Only the required tables for PostGIS are kept.")

# Define your tables using the declarative base
Base = declarative_base()
# Define Database Tables for Component data

class DSOs(Base):
    __tablename__ = 'dso'
    id = Column(Integer, primary_key=True)
    name = Column(String(255), unique=True)
    supply_area = Column(Geometry('MULTIPOLYGON', srid=4326))

class Voltage(Base):
    __tablename__ = 'voltage'
    id = Column(Integer, primary_key=True)
    voltage = Column(Float)

# class AssetCategories(Base):
#     __tablename__ = 'asset_category'
#     id = Column(Integer, primary_key=True)
#     name = Column(String(255))

class Substation(Base):
    __tablename__ = 'substation'
    id = Column(Integer, primary_key=True)
    dso_id = Column(Integer, ForeignKey('dso.id'))
    Voltage_level_high = Column(Integer, ForeignKey('voltage.id'))
    Voltage_level_low = Column(Integer, ForeignKey('voltage.id'))
    #asset_category_id = Column(Integer, ForeignKey('asset_category.id'))
    name = Column(String(255))
    Installation_date = Column(Date)
    Coordinates = Column(Geometry('POINT', srid=4326))
    
    cables_from = relationship("MediumVoltageCableSystem", back_populates="station_from", foreign_keys="[MediumVoltageCableSystems.station_from_id]")
    cables_to = relationship("MediumVoltageCableSystem", back_populates="station_to", foreign_keys="[MediumVoltageCableSystems.station_to_id]")

class MainSubstation(Substation):
    __tablename__ = 'main_substation'
    id = Column(Integer, ForeignKey('substation.id'), primary_key=True)
    children_substations = relationship("SecondarySubstation", back_populates="parent_station")

class SecondarySubstation(Substation):
    __tablename__ = 'secondary_substation'
    id = Column(Integer, ForeignKey('substation.id'), primary_key=True)
    parent_station_id = Column(Integer, ForeignKey('main_substation.id'))
    parent_station = relationship("MainSubstation", back_populates="children_substations")

class MediumVoltageCableSystem(Base):
    __tablename__ = 'medium_voltage_cable_system'
    id = Column(Integer, primary_key=True)
    dso_id = Column(Integer, ForeignKey('dso.id'))
    station_from_id = Column(Integer, ForeignKey('substation.id'))
    station_to_id = Column(Integer, ForeignKey('substation.id'))
    operating_voltage = Column(Integer, ForeignKey('voltage.id'))
    #asset_category_id = Column(Integer, ForeignKey('asset_category.id'))
    name = Column(String(255))
    number_of_subsections = Column(Integer) # can be an calculated parameter
    length_km = Column(Float) # can be an calculated parameter

    station_from = relationship("Substation", back_populates="cables_from", foreign_keys=[station_from_id])
    station_to = relationship("Substation", back_populates="cables_to", foreign_keys=[station_to_id])

    # Define the relationship to MediumVoltageCableSubsections
    subsections = relationship("MediumVoltageCableSubsection", back_populates="medium_voltage_cable_system")

    @hybrid_property
    def number_of_subsections(self):
        # This part will be used when accessing the attribute directly from an instance of the model
        return len(self.subsections)
    
    @number_of_subsections.expression
    def number_of_subsections(cls):
        # This part will be used when querying the database
        return select([func.count(MediumVoltageCableSubsection.id)]).where(MediumVoltageCableSubsection.cable_system_id == cls.id)
    
    #calculate the length as a hybrid property
    @hybrid_property
    def length_km(self):
        # This part will be used when accessing the attribute directly from an instance of the model
        return sum(subsection.length_km for subsection in self.subsections)
    
    @length_km.expression
    def length_km(cls):
        # This part will be used when querying the database
        return select([func.sum(MediumVoltageCableSubsection.length_km)]).where(MediumVoltageCableSubsection.cable_system_id == cls.id)

    # calculate the number of joints for the cable system
    @hybrid_property
    def number_of_joints(self):
        # This part will be used when accessing the attribute directly from an instance of the model
        return sum(subsection.number_of_joints for subsection in self.subsections)
    
    @number_of_joints.expression
    def number_of_joints(cls):
        # This part will be used when querying the database
        return select([func.sum(MediumVoltageCableSubsection.number_of_joints)]).where(MediumVoltageCableSubsection.cable_system_id == cls.id)
    
    # calculate the number of repairment sections for the cable system
    @hybrid_property
    def number_of_repairment_sections(self):
        # This part will be used when accessing the attribute directly from an instance of the model
        #Consider repairment_section is a boolean
        return sum(subsection.repairment_section for subsection in self.subsections)
    

class MediumVoltageCableSubsection(Base):
    __tablename__ = 'medium_voltage_cable_subsection'
    id = Column(Integer, primary_key=True)
    cable_system_id = Column(Integer, ForeignKey('medium_voltage_cable_system.id'))
    #sub_sektion_number = Column(Integer)
    number_of_conductors_primary = Column(Integer)
    conductor_size_primary_mm = Column(Float)  
    conductor_material = Column(String(255))
    insulation = Column(String(255))
    conductor_type = Column(String(255))  
    manufacturer = Column(String(255))
    in_service_date = Column(Date)  
    length_km = Column(Float)  
    coordinates = Column(Geometry('LineString'))
    medium_voltage_cable = relationship("MediumVoltageCableSystem", back_populates="subsections")
    repairment_section = Column(Boolean)
    out_of_service = Column(Boolean)
    joins_as_first = relationship("CableJoints", back_populates="first_cable_section", foreign_keys="[CableJoints.first_cable_section]")
    joins_as_second = relationship("CableJoints", back_populates="second_cable_section", foreign_keys="[CableJoints.second_cable_section]")

    @property 
    def number_of_joints(self):
        return len(self.joins_as_first) + len(self.joins_as_second)
    
    

class CableJoints(Base):
    __tablename__ = 'cable_joints'
    id = Column(Integer, primary_key=True)
    first_cable_section = Column(Integer, ForeignKey('medium_voltage_cable_subsection.id'))
    second_cable_section = Column(Integer, ForeignKey('medium_voltage_cable_subsection.id'))
    joint_type = Column(String(255))
    coordinates = Column(Geometry('POINT'))


# class LowVoltageCables(Base):
# Define Database tables for the Failures
class Failures(Base):
    __tablename__ = 'failures'
    id = Column(Integer, primary_key=True)
    #asset_category_id = Column(Integer, ForeignKey('asset_category.id'))
    cable_subsection_id = Column(Integer, ForeignKey('medium_voltage_cable_subsection.id'))
    date = Column(Date)
    failure_type = Column(String(255))
    failure_cause = Column(String(255))
    #affected_customers = Column(Integer)
    failure_location = Column(Geometry('POINT', srid=4326))
    #add weather conditions 


class CableRepairmentSections(Base):
    __tablename__ = 'cable_repairment'
    failures_id = Column(Integer, ForeignKey('failures.id'), primary_key=True)
    failed_cable_section = Column(Integer, ForeignKey('medium_voltage_cable_subsection.id'), primary_key=True)
    repairment_cable_section = Column(Integer, ForeignKey('medium_voltage_cable_subsection.id'), primary_key=True)
    #Add more attributes 
    # The repairment entity follows the assumption that a repairment cannot change the cable system id 

# Define Database Tables for Reliability Drivers (Events): Digging Activities, Lightning, Extreme Weather events, etc.  

class DiggingActivities(Base):
    __tablename__ = 'digging_activities'
    id = Column(Integer, primary_key=True)
    #diggingInquiryNumber = Column(Integer)
    diggingPeriodFrom = Column(Date)
    diggingPeriodTo = Column(Date)
    utilityType = Column(String)
    utilityTypeOther = Column(String)
    diggingType = Column(String)
    diggingTypeOther = Column(String)
    coordinates = Column(Geometry('POLYGON'))
    cable_details_requested = Column(Boolean)


class DiggingImpactOnCables(Base):
    __tablename__ = 'digging_impact_on_cables'
    digging_activities_id = Column(Integer, ForeignKey('digging_activities.id'), primary_key=True)
    medium_voltage_cable_subsection_id = Column(Integer, ForeignKey('medium_voltage_cable_subsection.id'), primary_key=True)
    digging_activities = relationship("digging_activities", back_populates="medium_voltage_cable_subsection")
    medium_voltage_cable_subsection = relationship("medium_voltage_cable_subsection", back_populates="digging_activities")
    #TODO: Add other attributes e.g. spatial overlap percentage, time overlap, etc. 

class CableFailuresDueToDigging(Base): 
    __tablename__ = 'cable_failures_due_to_digging'
    digging_activities_id = Column(Integer, ForeignKey('digging_activities.id'), primary_key=True)
    failures_id = Column(Integer, ForeignKey('failures.id'), primary_key=True)
    #TODO: Add other attributes e.g. spatial information, time overlap, etc. 
    




#Create entities for location based drivers 

class Roads(Base):
    __tablename__ = 'roads'
    id = Column(Integer, primary_key=True)
    road_type = Column(String(255))
    coordinates = Column(Geometry('LINESTRING', srid=4326))
    # #derive length of the road as a hybrid property from coordinates 
    # @hybrid_property
    # def length_km(self):
    #     return func.ST_Length(self.coordinates)/1000

class Rails(Base):
    __tablename__ = 'rails'
    id = Column(Integer, primary_key=True)
    rail_type = Column(String(255))
    coordinates = Column(Geometry('LINESTRING', srid=4326))

class WaterBodies(Base):
    __tablename__ = 'water_bodies'
    id = Column(Integer, primary_key=True)
    water_body_type = Column(String(255))
    coordinates = Column(Geometry('MULTIPOLYGON', srid=4326))

class SoilType(Base):
    __tablename__ = 'soil_type'
    id = Column(Integer, primary_key=True)
    soil_type = Column(String(255))
    coordinates = Column(Geometry('MULTIPOLYGON', srid=4326))

#Create a weather conditions entity
class LocationBasedWeatherConditions(Base): 
    __tablename__ = 'location_based_weather_conditions'
    id = Column(Integer, primary_key=True)
    Average_temperature = Column(Float)
    Average_wind_speed = Column(Float)
    Average_humidity = Column(Float)
    Average_precipitation = Column(Float)
    Max_temperature = Column(Float)
    Min_temperature = Column(Float)
    Max_wind_speed = Column(Float)
    Max_humidity = Column(Float)
    Max_precipitation = Column(Float)
    Time_range_for_calculation_start = Column(Date)
    Time_range_for_calculation_end = Column(Date)
    #location can be added through station or grid values 
    #station_coordinates = Column(Geometry('POINT', srid=4326))
    grid_coordinates = Column(Geometry('MULTIPOLYGON', srid=4326))

#Create cample placment conditions based on the location based drivers
class CablePlacementConditions(Base):
    __tablename__ = 'cable_placement_conditions'
    id = Column(Integer, primary_key=True)
    medium_voltage_cable_subsection_id = Column(Integer, ForeignKey('medium_voltage_cable_subsection.id'))
    #add a foreign key that can originate from the location based drivers
    loaction_driver_id = Column(Integer, ForeignKey('roads.id', 'rails.id', 'water_bodies.id', 'soil_type.id', 'location_based_weather_conditions.id'))
    #add more attributes e.g. spatial overlap percentage? 

#NOTE: If the attributes of the extreme weather events are repetitive we can create a class of "extreme weather events"

class Lightnings(Base):
    __tablename__ = 'lightning'
    id = Column(Integer, primary_key=True)
    Impact_Time = Column(Date)
    coordinates = Column(Geometry('POINT'))
    #TODO: Add features

class Heatwaves(Base):
    __tablename__ = 'heatwaves'
    id = Column(Integer, primary_key=True)
    Max_Temperature = Column(Float)
    Min_Temperature = Column(Float)
    Average_Temperature = Column(Float)
    Start = Column(Date)
    End = Column(Date)
    #Calculate derived attributes e.g. duration
    @hybrid_property
    def duration(self):
        return self.End - self.Start
    
    @duration.expression
    def duration(cls):
        return cls.End - cls.Start    
    coordinates = Column(Geometry('MultiPolygon'))

class Coldwaves(Base):
    __tablename__ = 'coldwaves'
    id = Column(Integer, primary_key=True)
    Max_Temperature = Column(Float)
    Min_Temperature = Column(Float)
    Average_Temperature = Column(Float)
    Start = Column(Date)
    End = Column(Date)
    #Calculate derived attributes e.g. duration
    @hybrid_property
    def duration(self):
        return self.End - self.Start
    
    @duration.expression
    def duration(cls):
        return cls.End - cls.Start    
    coordinates = Column(Geometry('MultiPolygon'))

class Floods(Base):
    __tablename__ = 'floods'
    id = Column(Integer, primary_key=True)
    #Check available data to add features here
    Start = Column(Date)
    End = Column(Date)
    #Calculate derived attributes e.g. duration
    @hybrid_property
    def duration(self):
        return self.End - self.Start
    
    @duration.expression
    def duration(cls):
        return cls.End - cls.Start    
    coordinates = Column(Geometry('MultiPolygon'))
    coordinates = Column(Geometry('MultiPolygon'))


# #Create an entity to track the events on the cables over time 
class EventsImpactingCables(Base):
    __tablename__ = 'events_impacting_cables'
    id = Column(Integer, primary_key=True)
    medium_voltage_cable_subsection_id = Column(Integer, ForeignKey('medium_voltage_cable_subsection.id'))
    event_id = Column(Integer, ForeignKey('failures.id', 'digging_activities.id', 'lightning.id', 'heatwaves.id', 'coldwaves.id', 'floods.id'))
    



# Create all tables stored in this metadata
Base.metadata.create_all(engine)
print("Tables created successfully.")

