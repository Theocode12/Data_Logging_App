#!.venv/bin/python3
from models.db_engine.db import TempDB, FileDB

def format_data(data_line):
    # Parse the input line
    data_parts = data_line.split(',')

    # Create a dictionary to hold the parsed data
    data_dict = {}
    for part in data_parts:
        key, value = part.split('=')
        data_dict[key.strip()] = value.strip()

    # Initialize the formatted data string
    formatted_data = ""

    # Check and format location data
    location_data = []
    if 'longitude' in data_dict and 'latitude' in data_dict:
        location_data.append(f"  - Longitude: {data_dict['longitude']}")
        location_data.append(f"  - Latitude: {data_dict['latitude']}")
    if location_data:
        formatted_data += "\nLocation Data:\n" + "\n".join(location_data) + "\n"

    # Check and format additional information
    additional_info = []
    for key in data_dict:
        if not key in ['longitude', 'latitude', 'date', 'time']:
            additional_info.append(f"  - {key.capitalize()}: {data_dict[key]}")

    if additional_info:
        formatted_data += "\nAdditional Information:\n" + "\n".join(additional_info) + "\n"

    # Check and format timestamp
    timestamp_info = []
    if 'date' in data_dict:
        timestamp_info.append(f"  - Date: {data_dict['date']}")
    if 'time' in data_dict:
        timestamp_info.append(f"  - Time: {data_dict['time']}")
    if timestamp_info:
        formatted_data += "\nTimestamp:\n" + "\n".join(timestamp_info) + "\n"

    # Return the formatted data
    return formatted_data

if __name__ == "__main__":
    tmpdb = TempDB()
    path = tmpdb.get_tmp_db_path()
    curr_db_line = 0

    print("\n====================")
    print("Sensor Data Summary")
    print("====================")

    while True:
        with FileDB(path, 'r') as db:
            lines = db.readlines()

        if curr_db_line != len(lines):
            print(len(lines))
            if len(lines) != 0:
                new_line = lines[-1]
                print(format_data(new_line))
                print("====================")
        
        curr_db_line = len(lines)
