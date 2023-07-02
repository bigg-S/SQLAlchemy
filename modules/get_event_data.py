import json

from attributedict.collections import AttributeDict

class EventDataExtracter:
    def __init__(self, web3, contract):
        self.web3 = web3
        self.contract = contract
        
    
    def get_event_logs(self, event_name):
        # Get the event logs for the given event name
        event_logs = self.contract.events[event_name]().get_logs(
            {
                "fromBlock": 0,
                "toBlock": 'latest'
            }
        )
        
        return event_logs
    
    # Convert AttribDict to Dict
    def attrib_dict_to_dict(self, attribdict):        
        parsed_dict = dict(attribdict)
        for key, val in parsed_dict.items():
            if 'list' in str(type(val)):
                parsed_dict[key] = [self.parse_dict_key_value(x) for x in val]
            else:
                parsed_dict[key] = self.parse_dict_key_value(val)
        return parsed_dict
    
    # Check for nested dict structures to iterate through
    def parse_dict_key_value(self, val):
        if 'dict' in str(type(val)).lower():
            return self.attrib_dict_to_dict(val)
        #convert 'HexBytes' type to 'str'
        elif 'HexBytes' in str(type(val)):
            return val.hex()
        else:
            return val
    
    def event_log_to_json(self, event_log):
        json_data = json.dumps(self.attrib_dict_to_dict(event_log))
        json_object = json.loads(json_data)
        
        return json_object

        