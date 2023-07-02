from datetime import datetime

import json

from modules.get_event_data import EventDataExtracter

class EventDataStore:
    def __init__(self, database_object):
        self.database_object = database_object
    
    def store_event_data(self, contract_address, event_name, transaction_hash, event_data):
        #Get the database connection
        database_connection = self.database_object.get_database_connection()
        
        cursor = database_connection.cursor() 
                        
        insert_query = "INSERT INTO contract_" + contract_address + "_events (event_name, transaction_hash, event_data) VALUES (%s, %s, %s); "
        
        event_data_json_string = json.dumps(event_data)
        cursor.execute(insert_query, (event_name, transaction_hash, event_data_json_string))

        database_connection.commit()
        cursor.close()
        database_connection.close()
        
    def is_duplicate_event(self, contract_address, event_name, transaction_hash):
        #Get the database connection
        database_connection = self.database_object.get_database_connection()
        
        cursor = database_connection.cursor() 
        
        query = "SELECT EXISTS ( SELECT 1 FROM contract_" + contract_address + "_events WHERE event_name = %s AND transaction_hash = %s);"
        
        cursor.execute(query, (event_name, transaction_hash))
        exists = cursor.fetchone()[0]
        
        cursor.close()
        database_connection.close()
        
        return exists

    def process_events(self, contracts_handler, database_initializer, web3_initializer):
        while True:
                    
            #Get the contracts from the database
            contracts = contracts_handler.get_contracts(database_object=database_initializer)
            
            for contract_data in contracts:
                contract = contracts_handler.initialize_contract(contract_data['contract_address'], contract_data['contract_abi'])
                
                for event in contract.events:   
                    #Create the event data extracter
                    event_data_extracter = EventDataExtracter(web3_initializer.web3, contract); 
                    
                    #Get Event logs for the given event
                    event_logs = event_data_extracter.get_event_logs(event.__name__)
                                        
                    if len(event_logs) > 0:
                        # Record the unrecorded events
                        counter = 1
                        while counter < len(event_logs):
                            
                            # Log as an AttribDict
                            attribdict_log = event_logs[counter*-1]  
                            
                            json_log = event_data_extracter.event_log_to_json(attribdict_log)                        
                                                                
                            contract_address = contract_data['contract_address']                
                            
                            #Create the events table if it does not exist
                            contracts_handler.create_contract_data_table(database_object=database_initializer, contract_address=contract_address, data_type="Events")
                                            
                            #Make sure it is not a duplicate
                            is_duplicate_event = self.is_duplicate_event(contract_address, event.__name__, json_log['transactionHash'])
                            if(is_duplicate_event == False):                            
                                self.store_event_data(contract_address, event.__name__ , json_log['transactionHash'], json_log)
                                
                                current_time = datetime.now()
                                formatted_time = current_time.strftime("%Y-%m-%d %H:%M:%S")
                                
                                print("Event " + event.__name__ + ": " + json_log['transactionHash'] + " recorded on " + formatted_time)
                                print()
                            else:
                                break

                            counter = counter + 1
            