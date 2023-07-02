from datetime import datetime


import json

class ViewDataStore:
    def __init__(self, database_object):
        self.database_object = database_object
    
    def store_view_data(self, contract_address, view_name, view_data):
        #Get the database connection
        database_connection = self.database_object.get_database_connection()
        
        cursor = database_connection.cursor() 
                        
        insert_query = "INSERT INTO contract_" + contract_address + "_views (view_name, view_data) VALUES (%s, %s); "
              
        cursor.execute(insert_query, (view_name, view_data))

        database_connection.commit()
        cursor.close()
        database_connection.close()
    
    def is_duplicate_view(self, contract_address, view_name, view_data):
        #Get the database connection
        database_connection = self.database_object.get_database_connection()
        
        cursor = database_connection.cursor() 
                
        query = "SELECT EXISTS ( SELECT 1 FROM contract_" + contract_address + "_views WHERE view_name = %s AND view_data = %s);"
        
        cursor.execute(query, (view_name, view_data))
        exists = cursor.fetchone()[0]
        
        cursor.close()
        database_connection.close()
        
        return exists
    
    def process_view(self, contract_data, contracts_handler, database_initializer, web3_initializer, view_getter):
        contract = contracts_handler.initialize_contract(contract_data['contract_address'], contract_data['contract_abi'])
        
        # The user chooses the function they want to call and the result(view) is printed
        view_data = view_getter.perform_view_function_call(web3_initializer.web3, contract)
        
        if 'Error' in view_data:
            print()
            print(view_data['Status'])
            print(view_data['Error'])
            print()
        else:
            contract_address = contract_data['contract_address']
            
            view_data_json_string = json.dumps(view_data)
                        
            #Create the views table if it does not exist
            contracts_handler.create_contract_data_table(database_object=database_initializer, contract_address=contract_address, data_type="Views")
                   
            function_name = view_data['function_name']       
                                         
           
            #Make sure it is not a duplicate
            is_duplicate_event = self.is_duplicate_view(contract_address, function_name, view_data_json_string)
            if(is_duplicate_event == False):                            
                self.store_view_data(contract_address, function_name, view_data_json_string)
                
                current_time = datetime.now()
                formatted_time = current_time.strftime("%Y-%m-%d %H:%M:%S")
                
                print()
                print("Output for " + function_name + ": " + view_data_json_string + " recorded on " + formatted_time )
                print()
                            
        