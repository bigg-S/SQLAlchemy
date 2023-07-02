import json
from datetime import date, timedelta, datetime


class ViewAccessor:

  def __init__(self, database_object):
    self.database_object = database_object

  def access_views(self, contract_address, days_back, function_name="All"):
    try:

      # Get current date
      current_date = date.today()

      # User desired date
      user_desired_date = current_date - timedelta(days=int(days_back))

      # Check if the user desired date exists
      database_connection = self.database_object.get_database_connection()
      cursor = database_connection.cursor()

      contract_views_table = "contract_" + contract_address + "_views"

      #Check if the events table exists
    
      cursor.execute(f"SELECT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = '{contract_views_table.lower()}')")

      # Fetch the result
      exists = cursor.fetchone()[0]

      # Print the result
      if  exists == 0:
          cursor.close()
          database_connection.close()
          return "There are no views recorded in the database for the given details."
      
      if function_name == "All":
        query = f"SELECT created_at FROM " + contract_views_table + "  WHERE CAST(created_at AS DATE) = DATE %s "
        cursor.execute(query, (user_desired_date, ))
      else:
        query = f"SELECT created_at FROM " + contract_views_table + "  WHERE CAST(created_at AS DATE) = DATE %s AND view_name = %s;"
        cursor.execute(query, (user_desired_date, function_name))

      desired_date_view = cursor.fetchone()

      # Fetch all the views
      # IF the desired date is beyond the available views' dates, we give all the available views
      time = datetime.now()
      current_time = datetime.time(time)
      current_date_time = datetime.combine(current_date, current_time)

      # Get all the event views
      if function_name == "All":
        query = "SELECT * FROM " + contract_views_table + " WHERE (created_at BETWEEN %s AND %s)"
        cursor.execute(query, (user_desired_date, current_date_time))
      else:
        query = "SELECT * FROM " + contract_views_table + " WHERE (created_at BETWEEN %s AND %s) AND view_name = %s"
        cursor.execute(query,
                       (user_desired_date, current_date_time, function_name))

      views = cursor.fetchall()

      # If there are views for the date
      if len(views) > 0:
        print()
        print("These are the available views.")
        # Display the views

        views = self.jsonify_views(views)

        return views

      else:

        return "There are no views available for the given details."

    except Exception as e:
      # Handle the exception/error
      return "An error occurred:" + str(e)
      

  def jsonify_views(self, views):
    views_data = []
    for view_data in views:
      data = {}
      data["Function Name"] = view_data[1]
      data["Result"] = view_data[2]["Result"]
      data["Created"] = str(view_data[3])

      views_data.append(data)

    return json.dumps(views_data, indent=4)
