import unittest
import psycopg2
import os
import requests
import datetime
import json

# TODO - Create a tests folder and separate each test into it's own py file
# TODO - Add a Makefile test target for each separated test and a test-all to run all tests

# Get environment variables for database details
DB_USER = os.getenv('DB_USER')
DB_PASSWORD = os.getenv('DB_PASSWORD')
DB_HOST = "localhost"
DB_NAME = os.getenv('DB_NAME')
DB_PORT = os.getenv('DB_PORT')
API_PORT = os.getenv('API_PORT')

SERVER_URL = f"http://localhost:{API_PORT}/hello"

DATE_OF_BIRTH = "1995-04-12"
USERNAME = "jorge"


def calculate_dates(birthday, now, username):
    # Function to compute the number of days until the next birthday
    delta1 = datetime.datetime(now.year, birthday.month, birthday.day).date()
    delta2 = datetime.datetime(now.year+1, birthday.month, birthday.day).date()

    days = ((delta1 if delta1 > now else delta2) - now).days
    if days == 365:
        message = {"message": f"Hello, {username}! Happy Birthday!"}
    else:
        message = {
            "message": f"Hello, {username}! Your birthday is in {days} day(s)"}
    return message


def connection():
    # Database connection object
    conn = psycopg2.connect(
        f"dbname='{DB_NAME}' user='{DB_USER}' host='{DB_HOST}' port='{DB_PORT}' password='{DB_PASSWORD}'")
    return conn


def connection_test():
    # Connecting to the database
    try:
        conn = connection()
        conn.close()
        return True
    except:
        return False


def insert_test():
    json_data = {'dateOfBirth': f'{DATE_OF_BIRTH}', }
    response = requests.put(f'{SERVER_URL}/{USERNAME}', json=json_data)
    return response.status_code


def get_test():
    _ = insert_test()
    response = requests.get(f'{SERVER_URL}/{USERNAME}')
    expected_response = calculate_dates(datetime.datetime.strptime(
        DATE_OF_BIRTH, "%Y-%m-%d"), datetime.date.today(), USERNAME)
    if response.json() == expected_response and response.status_code == 200:
        return True
    else:
        return False


def future_date_test():
    json_data = {'dateOfBirth': '2050-04-12', }
    response = requests.put(f'{SERVER_URL}/{USERNAME}', json=json_data)
    expected_response = {
        "message": "Error! Date of birth provided is in the future!"}
    if response.json() == expected_response and response.status_code == 400:
        return True
    else:
        return False


def username_test():
    response = requests.get(f'{SERVER_URL}/user1234')
    expected_response = {"message": "Error! Username not valid!"}
    if response.json() == expected_response and response.status_code == 400:
        return True
    else:
        return False


def wrong_date_test():
    json_data = {'dateOfBirth': '1995-20-12', }
    response = requests.put(f'{SERVER_URL}/{USERNAME}', json=json_data)
    expected_response = {
        "message": "Error! The date provided is incorrect. It should be YYYY-MM-DD"}
    if response.json() == expected_response and response.status_code == 400:
        return True
    else:
        return False


def missing_body_test():
    response = requests.put(f'{SERVER_URL}/{USERNAME}')
    expected_response = {
        "message": "Error! Request payload and Content-Type: application/json header are required"}
    if response.json() == expected_response and response.status_code == 400:
        return True
    else:
        return False


class Testing(unittest.TestCase):
    def test_db_connection(self):
        connection = connection_test()
        self.assertEqual(connection, True)

    def test_insert(self):
        insert = insert_test()
        self.assertEqual(str(insert), "204")

    def test_get(self):
        get = get_test()
        self.assertEqual(get, True)

    def test_future_date(self):
        future_date = future_date_test()
        self.assertEqual(future_date, True)

    def test_username(self):
        future_date = future_date_test()
        self.assertEqual(future_date, True)

    def test_wrong_date(self):
        wrong_date = wrong_date_test()
        self.assertEqual(wrong_date, True)

    def test_missing_body(self):
        missing_body = missing_body_test()
        self.assertEqual(missing_body, True)


if __name__ == '__main__':
    unittest.main()
