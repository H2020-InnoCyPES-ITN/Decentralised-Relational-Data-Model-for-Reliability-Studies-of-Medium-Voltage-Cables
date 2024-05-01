# Decentralised-Relational-Data-Model-for-Reliability-Studies-of-Medium-Voltage-Cables

In the context of reliability prediction of MV cables, there is an opportunity for Distribution System Operators (DSOs) to standardize data collection. This repository provides an Entity-Relationship (ER) data model created to facilitate this standardization. The ER data model ensures that all data adheres to specified formats and relationships, fulfilling a prerequisite for decentralized data storage.

A simplified visualisation of the data schema is provided below: 

![image](https://github.com/H2020-InnoCyPES-ITN/Decentralised-Relational-Data-Model-for-Reliability-Studies-of-Medium-Voltage-Cables/assets/101191232/c25c021a-8931-4b33-aaed-9b638c2c58ba)


The ER diagram is color-coded to represent different components:

- Yellow: Topics grid components
- Blue: Cable events
- Red: External cable event impacts
- Green: Cable placement conditions

## Automatic Database Schema Creation 

This repository includes an SQLAlchemy script (`create_schema.py`) that facilitates the automatic creation of the described database structure in a PostgreSQL database.

### Usage

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
   
This will connect to the PostgreSQL database and create the necessary tables and relationships based on the defined data model.
