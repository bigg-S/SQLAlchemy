import json
from datetime import date, timedelta, datetime


class EventsAccessor:

  def __init__(self, database_object):
    self.database_object = database_object

  def access_events(self, contract_address, days_back, event_name="All"):

    try:

      # Get current date
      current_date = date.today()

      # User desired date
      user_desired_date = current_date - timedelta(days=int(days_back))

      # Check if the user desired date exists
      database_connection = self.database_object.get_database_connection()
      cursor = database_connection.cursor()

      contract_logs_table = "contract_" + contract_address + "_events"


      #Check if the events table exists
    
      cursor.execute(f"SELECT NOT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = '{contract_logs_table.lower()}')")

      # Fetch the result
      not_exists = cursor.fetchone()[0]

      # Print the result
      if  not_exists:
          cursor.close()
          database_connection.close()
          return "There are no events logs in the database for the provided details"

      
      if event_name == "All":
        query = f"SELECT recorded_at FROM " + contract_logs_table + "  WHERE CAST(recorded_at AS DATE) = DATE %s "
        cursor.execute(query, (user_desired_date, ))
      else:
        query = f"SELECT recorded_at FROM " + contract_logs_table + "  WHERE CAST(recorded_at AS DATE) = DATE %s AND event_name = %s;"
        cursor.execute(query, (user_desired_date, event_name))

      desired_date_log = cursor.fetchone()

      
      # Fetch all the logs
      # IF the desired date is beyond the available logs' dates, we give all the available logs
      time = datetime.now()
      current_time = datetime.time(time)
      current_date_time = datetime.combine(current_date, current_time)

      # Get all the event logs
      if event_name == "All":
        query = "SELECT * FROM " + contract_logs_table + " WHERE (recorded_at BETWEEN %s AND %s)"
        cursor.execute(query, (user_desired_date, current_date_time))
      else:
        query = "SELECT * FROM " + contract_logs_table + " WHERE (recorded_at BETWEEN %s AND %s) AND event_name = %s"
        cursor.execute(query,
                       (user_desired_date, current_date_time, event_name))

      event_logs = cursor.fetchall()

      cursor.close()
      database_connection.close()
      # If there are logs for the date
      if len(event_logs) > 0:
        
        event_logs = self.jsonify_events(event_logs)
        return event_logs

      else:
        cursor.close()
        database_connection.close()
        return "There are no event logs for the given detail"

    except Exception as e:
      # Handle the exception/error
       return "An error occurred:" + str(e)
      
  def jsonify_events(self, events):
    events_data = []
    for event_data in events:
      event_data = event_data[3]  #The data is in the third item of the log
      data = {}
      data["event"] = event_data["event"]
      data["logIndex"] = event_data["logIndex"]
      data["transactionIndex"] = event_data["transactionIndex"]
      data["transactionHash"] = event_data["transactionHash"]
      data["address"] = event_data["address"]
      data["blockNumber"] = event_data["blockNumber"]
      data["blockHash"] = event_data["blockHash"]
      data["args"] = event_data["args"]

      events_data.append(data)

    return json.dumps(events_data, indent=4)
