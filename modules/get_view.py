import json
from modules.store_view import ViewDataStore


class ViewExtracter:

  def get_view(self, web3_initializer, contracts_handler, database_initializer,
               contract_address, function_name, arguments):
    contract_data = contracts_handler.get_contracts(
      database_object=database_initializer, contract_address=contract_address)


    #Make sure the contract address exists
    if contract_data == None:
      return "There is no contract with the given contract address in the database."
          
    contract = contracts_handler.initialize_contract(
      contract_data["contract_address"], contract_data["contract_abi"])

    user_inputs = []
    for argument in arguments:
      if (argument != None):
        user_inputs.append(argument)

    address_input = user_inputs[0]  #assuming the first argument is the address
    if address_input.startswith("0x") and len(address_input) == 42:
      # Remove the "0x" prefix and convert to lowercase
      address = address_input[2:].lower()
      address = web3_initializer.web3.to_checksum_address(address)
      address_input = address
      user_inputs[0] = address

    try:
      if len(user_inputs) > 1:
        result = contract.functions[function_name](user_inputs[0]).call(
        )  #Using a function with one input as the address address for testing
        #result = contract.functions[function_name](*user_inputs).call() #Using multiple argumnts
      else:
        result = contract.functions[function_name]().call()

      data = {}
      data["Function Name"] = function_name
      data["Result"] = result
      view_json_string = json.dumps(data)

      # Store the data
      #Create the views table if it does not exist
      contracts_handler.create_contract_data_table(
        database_object=database_initializer,
        contract_address=contract_address,
        data_type="Views")

      #Make sure it is not a duplicate
      view_data_store = ViewDataStore(database_initializer)

      is_duplicate_event = view_data_store.is_duplicate_view(
        contract_address, function_name, view_json_string)
      if (is_duplicate_event == False):
        view_data_store.store_view_data(contract_address, function_name,
                                        view_json_string)

      return json.dumps(data, indent=4)
    except Exception as e:      
      return f"Error retrieving data for function '{function_name}': {str(e)}"

  def print_view_functions(self, contracts_handler, database_initializer,
                           contract_address):
    contract_data = contracts_handler.get_contracts(
      database_object=database_initializer, contract_address=contract_address)

    #Make sure the contract address exists
    if contract_data == None:
      return "There is no contract with the given contract address in the database."
              
    contract = contracts_handler.initialize_contract(
      contract_data["contract_address"], contract_data["contract_abi"])

    #Get the list of view functions (constant functions)
    view_functions = [
      fn for fn in contract.abi
      if fn['type'] == 'function' and fn['stateMutability'] == 'view'
    ]

    view_functions_data = []
    # Loop through each view function and get its data

    for function in view_functions:
      view_function_data = {}
      function_name = function['name']

      view_function_data['Function name'] = function_name
      # Check if the function has inputs/arguments
      function_abi = next(
        (item for item in contract.abi
         if 'name' in item and item["name"] == function_name), None)

      if "inputs" in function_abi:
        inputs = function_abi["inputs"]

        for arg in inputs:
          view_function_data["Input: " + arg["name"]] = arg["type"]

      view_functions_data.append(view_function_data)

    return json.dumps(view_functions_data, indent=4)
