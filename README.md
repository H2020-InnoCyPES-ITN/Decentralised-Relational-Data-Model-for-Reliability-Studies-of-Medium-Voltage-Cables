# Decentralised-Relational-Data-Model-for-Reliability-Studies-of-Medium-Voltage-Cables

In the context of reliability prediction of MV cables, there is an opportunity for Distribution System Operators (DSOs) to standardise data collection. This repository provides an Entity-Relationship (ER) data model created to facilitate this standardisation. The ER data model ensures that all data adheres to specified formats and relationships, fulfilling a prerequisite for decentralised data storage.

A simplified visualisation of the data schema is provided below: 

![image](https://github.com/H2020-InnoCyPES-ITN/Decentralised-Relational-Data-Model-for-Reliability-Studies-of-Medium-Voltage-Cables/assets/101191232/c25c021a-8931-4b33-aaed-9b638c2c58ba)


The ER diagram is colour-coded to represent different components:

- Yellow: Topics grid components
- Blue: Cable events
- Red: External cable event impacts
- Green: Cable placement conditions

## Automatic Database Schema Creation 

This repository includes an SQLAlchemy script (`create_schema.py`) that facilitates the automatic creation of the described database structure in a PostgreSQL database.

1. **Requirements**: Ensure you have Python installed on your system.
2.  **Virtual Environment (Optional but Recommended)**: It's recommended to create a virtual environment to isolate the dependencies for this project. Run the following command to create a virtual environment named `venv`:
     ```bash
     python -m venv venv
     ```
3. **Activate Virtual Environment**: Activate the virtual environment. The command to activate depends on your operating system:

   - On Windows:

     ```bash
     venv\Scripts\activate
     ```

   - On macOS and Linux:

     ```bash
     source venv/bin/activate
     ```
4. **Installation**: Install the required Python packages by running:

     ```bash
     pip install -r requirements.txt
     ```
6. **Configuration**: Modify the database connection details (e.g., host, port, username, password, database name) in the script to match your PostgreSQL setup.

7. **Execution**: Run the script using the following command:

   ```bash
   python create_schema.py
   ```
   
This will connect to the PostgreSQL database and create the necessary entities, attributes and relationships based on the defined data model.

## Key Entities and Attributes

In the following, key entities and attributes of the proposed ER design are listed and explained.

### DSOs
The DSO entity is essential; it maps the Distribution System Operator (DSO) object into an entity, in this way, different network characteristics and management decisions can be investigated. Further, it isn’t sufficient to model DSOs as an attribute of other entities, because this would limit the possibility to store DSO-specific attributes, such as name, DSO supply area or reliability indices and others. 

### Substations
To model substation connections within the MV cable network, a substation entity is created with attributes such as DSO-id, voltage levels, installation date, station type, and coordinates. As shown in Figure 2, the substation is a super-entity from which the sub-entities ”primary station” and ”secondary substation” are derived. In this way, all of the attributes of the substation entity are inherited, while specific attributes per sub-entity types can be stored as well, such as the ”primary parent station” for the ”secondary substation”.

### MV Cable Systems
The ”MV cable systems” consists of the foreign keys: station-from-id and station-to-id, which can thereby link to both main or secondary substation and link to high-level attributes such as operating DSO. Beyond that, to align operational parameters and to ensure naming conventions, further attributes are introduced, such as operating voltage, average and max loading.

### MV Cable Subsections
The entity ”MV cable subsections” links via a foreign key to the ”MV cable systems” entity and thus reflects that the system is divided into one or more subsections. Moreover, a list of subsection-specific parameters
is added, such as conductor material and type, number of conductors, insulation, manufacturer, in-service date, length, and coordinates. Tracking the connection to other subsections is also possible. Lastly, two boolean attributes are introduced that reflect if the MV section was installed due to a repair and if the section is still in operation.

### MV Cable Joints
MV subsections are connected via cable joints. These can represent a weakness in the cable system and present additional attributes such as joint type and location. They should thus be integrated into the data model as a separate entity.

### Cable Failures & Repairs
To model events that impact one specific MV cable subsection, such as failures and repairs a cable event entity is created. Via a foreign key, it links to the affected MV cable subsection and obtains date attributes, such as event start and event end. Next, the Sub-entities ”Cable Failures” and ”Cable repairs” can be created from the ”Cable Event” entity. The failures contain attributes such as failure type, cause and location, whereas the repairs link to repair specifications and the related failure event.

### External Events
Despite events that always involve the cable, the data schema also includes external events, such as digging activities and weather-based events, including lightning, heatwaves, cold waves, floods, etc., that might have an impact on the cable reliability prediction and thus need to be reflected in the database schema. Consequently, this study proposes the creation of an entity called ”external events,” from which all subsequent external event types inherit
their start and end times. Due to different ways of storing geographical information, e.g. polygons for digging activities and point coordinates for lightning, the location attributes are saved on the sub-entity level. Furthermore, for each external event type, more specific attributes are added, such as utility and digging type for the digging activities or number of strokes and intensity for lightning. 

### Cable External Event Impacts
One key requirement for predicting the reliability of MV cables is to query external events that have affected them. To reflect this, an entity ”Cable External Event Impacts” is created that links MV subsections to external events. The definition of a cable being affected by an event is then defined, given the location and time.

### Location-Based Drivers
Other static mini-world entities, such as roads, rails, water bodies, ground water level, etc., might also influence the reliable operation of the MV cables if they are in proximity. Because they are location-specific, they can be summarised in the entity of ”location-based drivers”. More attributes can be added on a sub-entity level, such as road, rail, or waterbody type. This study proposes to add environmental observation to the entity of location-based
drivers. In this way, favourable or unfavourable conditions with regard to environmental parameters such as temperature, humidity or precipitation can also be tracked and taken into account 

### Cable Placement Conditions
Within the ”Cable Placement Conditions” entity, the previously described location-based drivers are spatially linked to the MV cable subsections. Consequently, this facilitates data retrieval of the location-specific placement conditions of the cables.

## Derived Attributes

Many data requests related to reliability prediction of MV cables require aggregated information on either MV cable subsection, MV cable system, or at the cable failure level. Therefore, the computation of derived attributes, such as the number of subsections or joints per MV cable system, can be beneficial for several reasons. First, the computation of derived attributes can be more efficient than doing the same computation externally. Further, it can be expected that if the derived attributes are used in multiple queries or reports, computing them in SQL (Structured Query Language) can improve code re-usability and maintainability. Moreover, the derived attributes can help to maintain Data integrity, as a computation within the DBMS (Database Management System) can ensure that the computations are based directly on the source data. One use case for derived attributes is given by  the aggregation of information on the MV cable system level. For example, the length of an MV cable system can be derived from the individual lengths of the respective subsections. Also, in the context of cable events, the formulation of derived attributes is feasible, taking into account external events as well as cable placement conditions. Therefore, features such as the number of digging activities affecting one cable system, as well as the number of crossing roads of a cable system, can be easily derived by using the provided data schema. It should also be emphasised that the presented model design allows the formulation of nested derived attributes, such as the number of failures at the main station level. 
Further, the number of subsections or joints per MV cable system can be computed on the basis of the existing entity relations.



