import json

from psycopg2.extras import RealDictCursor


class ContractsHandler:

  def __init__(self, web3):
    self.web3 = web3

  def initialize_contract(self, contract_address, contract_abi):
    # Get the contract abi
    abi = json.dumps(contract_abi)

    # Instantiate the contract
    contract = self.web3.eth.contract(address=contract_address, abi=abi)

    return contract

  def get_contracts(self, database_object, contract_address="All"):
    #Get the database connection
    database_connection = database_object.get_database_connection()

    cursor = database_connection.cursor(cursor_factory=RealDictCursor)
    if contract_address == "All":
      query = "SELECT * FROM contracts"
      cursor.execute(query)
      contracts = cursor.fetchall()
    else:
      query = "SELECT * FROM contracts WHERE contract_address = %s"
      cursor.execute(query, (contract_address, ))
      contracts = cursor.fetchone()

    cursor.close()
    database_connection.close()

    return contracts

  def add_contract(self, database_object, contract_address, contract_abi):

    #Get the database connection
    database_connection = database_object.get_database_connection()

    if (self.is_duplicate_contract(database_object, contract_address,
                                   contract_abi)):
      return "Contract Exist"
    else:
      cursor = database_connection.cursor()

      insert_query = "INSERT INTO contractS (contract_address, contract_abi) VALUES (%s, %s); "

      cursor.execute(insert_query, (contract_address, contract_abi))

      database_connection.commit()
      cursor.close()
      database_connection.close()

      return "Contract Added"

  def is_duplicate_contract(self, database_object, contract_address,
                            contract_abi):
    #Get the database connection
    database_connection = database_object.get_database_connection()

    cursor = database_connection.cursor()

    query = "SELECT EXISTS ( SELECT 1 FROM contracts WHERE contract_address = %s OR contract_abi = %s);"

    cursor.execute(query, (contract_address, contract_abi))
    exists = cursor.fetchone()[0]

    cursor.close()
    database_connection.close()

    return exists

  def create_contract_data_table(self, database_object, contract_address,
                                 data_type):
    #Get the database connection
    database_connection = database_object.get_database_connection()

    cursor = database_connection.cursor(cursor_factory=RealDictCursor)

    if (data_type == "Events"):
      query = "CREATE TABLE IF NOT EXISTS contract_" + contract_address + "_events ( id SERIAL PRIMARY KEY, event_name TEXT NOT NULL, transaction_hash TEXT NOT NULL,    event_data JSONB,    recorded_at TIMESTAMP DEFAULT NOW());"
    elif (data_type == "Views"):
      query = "CREATE TABLE IF NOT EXISTS contract_" + contract_address + "_views ( id SERIAL PRIMARY KEY, view_name TEXT NOT NULL, view_data JSONB,    created_at TIMESTAMP DEFAULT NOW());"
    else:
      return

    cursor.execute(query)

    database_connection.commit()

    cursor.close()
    database_connection.close()
