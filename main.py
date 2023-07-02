from fastapi import FastAPI, Request, Query
from fastapi.responses import JSONResponse, Response

import json

from modules.database_initialization import DatabaseInitializer
from modules.web3_initialization import Web3Initializer
from modules.contracts_handler import ContractsHandler

from modules.store_event_data import EventDataStore

from modules.store_view import ViewDataStore
from modules.get_view import ViewExtracter

from modules.access_events import EventsAccessor
from modules.access_views import ViewAccessor
from modules.get_event_data import EventDataExtracter

# Setup
from web3 import Web3

app = FastAPI()

#Initialize Web3
web3_initializer = Web3Initializer(
  "https://goerli.optimism.io") #This endpoint is for Goerli Optimism endpoint


#Create the contracts handler
contracts_handler = ContractsHandler(web3_initializer.web3)

#Initialize the database
database_initializer = DatabaseInitializer("config.json")

#Prepare to store event logs to the database
event_data_store = EventDataStore(database_object=database_initializer)

#Prepare to store views
view_data_store = ViewDataStore(database_object=database_initializer)

#Prepare the object that facilitates the retieval of a view from the contract
view_getter = ViewExtracter()

#Prepare to access the event logs
events_accessor = EventsAccessor(database_object=database_initializer)

#Prepare to access the views
views_accessor = ViewAccessor(database_object=database_initializer)


#Routes
@app.get("/")
def routes_examples():

  data = "New Contract: base_url/new_contract/0xD74D825286961b06986943CA3Bb97D9B6b7aAd92/<contract_abi_in_json_format>\n\n"
  data = data + "Listen for Events Logs: base_url/get_events_logs/\n\n"
  data = data + "Access Event Logs: base_url/access_events/{contract_address}/{days_back}/{event_name}\n  Example one: base_url/access_events/0xD74D825286961b06986943CA3Bb97D9B6b7aAd92/1/All\n  Example two: base_url/access_events/0xD74D825286961b06986943CA3Bb97D9B6b7aAd92/1/Initialized\n\n"
  data = data + "Display view funcions & inputs: base_url/view_functions_and_inputs/{contract_address}\n Example: base_url/view_functions_and_inputs/0xD74D825286961b06986943CA3Bb97D9B6b7aAd92\n\n"
  data = data + "Call view function: base_url/invoke_view_function/{contract_address}/{function_name}/{arguments}\n  Example without arguments: base_url/invoke_view_function/0xD74D825286961b06986943CA3Bb97D9B6b7aAd92/winnerNumber?arguments=\n  Example with arguments: base_url/invoke_view_function/0xD74D825286961b06986943CA3Bb97D9B6b7aAd92/entries?arguments=0xD74D825286961b06986943CA3Bb97D9B6b7aAd92&arguments=\n\n"
  data = data + "Accessing Views: base_url/access_views/{contract_address}/{days_back}/{function_name}\nExample one: base_url/access_views/0xD74D825286961b06986943CA3Bb97D9B6b7aAd92/1/All\n Example two: base_url/access_views/0xD74D825286961b06986943CA3Bb97D9B6b7aAd92/1/winnerNumber"
  
  return Response(content=data, media_type="application/json")
      
#add new contract
@app.get("/new_contract/{contract_address}/{contract_abi}")
def new_contract_endpoint(contract_address: str, contract_abi: str):

  status = contracts_handler.add_contract(database_object=database_initializer,
                                          contract_address=contract_address,
                                          contract_abi=contract_abi)

  return Response(content=status, media_type="application/json")


# Processing the event logs
@app.get("/get_events_logs/")
def get_event_logs():
  event_data_store.process_events(contracts_handler=contracts_handler,
                                  database_initializer=database_initializer,
                                  web3_initializer=web3_initializer)


# Print view functions
# Error Handling(none)
@app.get("/view_functions_and_inputs/{contract_address}")
def print_view_functions_and_inputs(contract_address: str):
  view_functions = view_getter.print_view_functions(
    contracts_handler=contracts_handler,
    database_initializer=database_initializer,
    contract_address=contract_address)

  return Response(content=view_functions, media_type="application/json")


# The user chooses the function they want to call and the result(view) is printed
@app.get("/invoke_view_function/{contract_address}/{function_name}")
def invoke_view_function(contract_address: str,
                         function_name: str,
                         arguments: list = Query(...)):
  result = view_getter.get_view(web3_initializer=web3_initializer,
                                contracts_handler=contracts_handler,
                                database_initializer=database_initializer,
                                contract_address=contract_address,
                                function_name=function_name,
                                arguments=arguments)

  return Response(content=result, media_type="application/json")


# Access the event logs
@app.get("/access_events/{contract_address}/{days_back}/{event_name}")
def access_events_endpoint(contract_address: str, days_back: int,
                           event_name: str):

  events = events_accessor.access_events(contract_address=contract_address,
                                         days_back=days_back,
                                         event_name=event_name)

  return Response(content=events, media_type="application/json")


# Access the views
@app.get("/access_views/{contract_address}/{days_back}/{function_name}")
def access_view_endpoint(contract_address: str, days_back: int,
                         function_name: str):

  views = views_accessor.access_views(contract_address=contract_address,
                                      days_back=days_back,
                                      function_name=function_name)

  return Response(content=views, media_type="application/json")
