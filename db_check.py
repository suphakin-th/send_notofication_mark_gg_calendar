import json
import mysql.connector

def read_config(file_path):
    with open(file_path, 'r') as file:
        config = json.load(file)
    return config

# Replace these values with your actual database credentials
def connect_to_database(config):
    database_config = {
        'user': config['database']['user'],
        'password': config['database']['password'],
        'host': config['database']['host'],
        'port': config['database']['port'],
        'database': config['database']['database_name'],
        'raise_on_warnings': True
    }

    try:
        # Connect to the database
        connection = mysql.connector.connect(**database_config)
        
        if connection.is_connected():
            print("Connected to the database.")
            return connection

        # Create a cursor object to execute SQL queries
        cursor = connection.cursor()

        # Example: Execute a simple query
        cursor.execute("SELECT cr.values FROM compose_record cr WHERE rel_module = '353947921997627395';")

        # Fetch and print the results
        result = cursor.fetchall()
        for row in result:
            print(row)

    except mysql.connector.Error as err:
        print(f"Error: {err}")

    finally:
        # Close the cursor and connection
        if 'cursor' in locals() and cursor is not None:
            cursor.close()
        if 'connection' in locals() and connection is not None:
            connection.close()
    
def main():   
    # Read configuration from JSON file
    config = read_config('database_config.json')

    # Establish a connection to the database
    connection = connect_to_database(config)

    # Perform database operations here...

    # Close the database connection when done
    if connection:
        connection.close()
        print("Connection closed.")

if __name__ == "__main__":
    main()