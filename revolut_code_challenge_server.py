import flask
import time
import math
import datetime
import psycopg2
import os

app = flask.Flask(__name__)


def calculate_dates(birthday, now, username):
    '''
    Calculates the number of days between today and the next birthday.
    Returns the correspondant message.
    '''
    # Function to compute the number of days until the next birthday
    delta1 = datetime.datetime(now.year, birthday.month, birthday.day).date()
    delta2 = datetime.datetime(now.year+1, birthday.month, birthday.day).date()

    days = ((delta1 if delta1 > now else delta2) - now).days
    # TODO - Implement leap year check (366 days year)
    if days == 365:
        return flask.jsonify({"message": f"Hello, {username}! Happy Birthday!"})
    else:
        return flask.jsonify({"message": f"Hello, {username}! Your birthday is in {days} day(s)"})


def table_exists(dbcon, tablename):
    '''
    Checks if the given table exists.
    '''
    dbcur = dbcon.cursor()
    dbcur.execute("""
        SELECT COUNT(*)
        FROM information_schema.tables
        WHERE table_name = %s
        """, (tablename,))
    if dbcur.fetchone()[0] == 1:
        dbcur.close()
        return True

    dbcur.close()
    return False


def get_user_birthday(dbcon, username):
    '''
    Returns birthday date of the username provided or None if username does not exists.
    '''
    # TODO - return more meaningful error messages instead of only 500
    with dbcon.cursor() as dbcur:
        if not table_exists(dbcon, "users"):
            # Table does not exist similar outcome for the client as user does not exist
            return None

        dbcur.execute(
            """SELECT birthday from users WHERE username = %s""", (username,))
        birthday = dbcur.fetchone()
        if birthday != None:
            return birthday[0]
        else:
            return None


def update_user_birthday(dbcon, username, birthday):
    '''
    Creates users table if it does not exists.
    Inserts new username and birthday into the database if it is not present already.
    Updates username birthday date if it already exists.
    '''
    with dbcon.cursor() as dbcur:
        # TODO - return more meaningful error messages instead of only False
        # Create the users table if not exists
        try:
            dbcur.execute(
                """CREATE TABLE IF NOT EXISTS users(username varchar(50), birthday DATE, PRIMARY KEY (username))""")
        except:
            return False
        # Insert into the database or update if the row already exists
        try:
            insert_query = """INSERT INTO users (username, birthday) VALUES (%s, %s) ON CONFLICT (username) DO UPDATE SET birthday = EXCLUDED.birthday;"""
            dbcur.execute(insert_query, (username, birthday))
            return True
        except Exception as e:
            print(e)
            return False


# API hello route definition
@app.route('/hello/<username>', methods=['GET', 'PUT'])
# Main function for the /hello route
def home(username):
    # Checking if the username is valid
    if not username.isalpha():
        return flask.make_response(
            flask.jsonify(
                {"message": "Error! Username not valid!"}), 400
        )

    # Connecting to the database with error handling
    try:
        # Get environment variables for database details
        DB_USER = os.getenv('DB_USER')
        DB_PASSWORD = os.getenv('DB_PASSWORD')
        DB_HOST = os.getenv('DB_HOST')
        DB_NAME = os.getenv('DB_NAME')
        # Database connection object
        conn = psycopg2.connect(
            f"dbname='{DB_NAME}' user='{DB_USER}' host='{DB_HOST}' password='{DB_PASSWORD}'")
        # Setting auto commit to True
        conn.autocommit = True
    except:
        # Returning a 500 Internal server error when the database connection fails
        return flask.make_response(
            flask.jsonify(
                {"message": f"Connection error please check your environment variables"}), 500
        )
    # Checking the request's method type
    if flask.request.method == 'GET':
        # Get user birthday from the database
        birthday = get_user_birthday(conn, username)

        if birthday == None:
            # Returning a 404 Not found response if the user does not exists
            return flask.make_response(
                flask.jsonify(
                    {"message": f"Error! User {username} not found"}), 404
            )
        else:
            # Returning the required message depending on the number of days left until next birthday
            return calculate_dates(birthday, datetime.date.today(), username)

    elif flask.request.method == 'PUT':
        # Checking if the request has a payload in a JSON format and error handling response
        if not flask.request.data:
            # Returning a 400 Bad Request response if no body or Content-Type: application/json header are provided
            return flask.make_response(
                flask.jsonify(
                    {"message": "Error! Request payload and Content-Type: application/json header are required"}), 400
            )
        # Get request body
        data = flask.request.get_json()
        birthday = data['dateOfBirth']
        # Check if the date is valid
        try:
            birthday = datetime.datetime.strptime(birthday, '%Y-%m-%d').date()
        except ValueError:
            return flask.make_response(
                flask.jsonify(
                    {"message": "Error! The date provided is incorrect. It should be YYYY-MM-DD"}), 400
            )

        # Check if the date of birth sent by the client is not in the future, i.e < today
        if birthday > datetime.date.today():
            # Returning a 400 Bad Request response if the date is in the future
            return flask.make_response(
                flask.jsonify(
                    {"message": "Error! Date of birth provided is in the future!"}), 400
            )
        else:
            # Insert/update the date of birth into the Database
            if update_user_birthday(conn, username, birthday):
                # Returning 204 No content response when the update is successful
                return ('', 204)
            else:
                # Returning a 500 Internal server error when the update/insert fails
                return flask.make_response(
                    flask.jsonify(
                        {"message": f"Internal server error"}), 500
                )
    conn.close()


# Run Flask API for all network local address and on port 8080 instead of default 127.0.0.1:5000
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
