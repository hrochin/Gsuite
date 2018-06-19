"""
Using boilerplate from googles quickstart.py for this project and altering
the code so that we can update all current user's phone numbers located in
companyNumbers.csv

This will be later used to create a more generalized API functions script

"""
import pprint
import re
import os, sys
from apiclient import errors
from apiclient.discovery import build
from httplib2 import Http
from oauth2client import file, client, tools

from time import sleep

# Helper functions derived from csv_test.py -- Generator
def csvData(file_name):
    ''' Takes CSV file and returns its content through an iterator.
        params: file_name   : Path to CSV
        returns: yields next line in file
    '''

    with open(file_name) as csvFile:
        for line in csvFile.readlines():
            yield line


def clean_phone_data(data):
    '''  Takes an iterable object from the CSV file and creates a list of
         all users and phone numbers to be saniticed.

         params: data   : iterable object
         return: List of lists of users, phone numbers
    '''

    # Using list comprehension to generate new list with strings split
    data = [user.split(',') for user in data]

    # Clean up phone numbers using regex
    # (\d{,3})?     Area Code
    # [\.\-\s]*     Separator
    # (\d{3})       First 3
    # [\.\-\s]*     Separator
    # (\d{4})       Last for of the phone number

    phoneReg = re.compile(r'(\d{,3})?[\.\-\s]*(\d{3})[\.\-\s]*(\d{4})')

    # Correc the phones using the regEx groups

    for item in data:
        # Try to search for the groups in each item.
        # If it fails, it returns a 'NoneType' with no group attribute

        try:
            # Grab user and append domain for a full valid email address
            item[0] += '@renovaenergy.com'
            # User the groups tupple and join them into a corrected string
            item[1] = ''.join(phoneReg.search(item[1]).groups())

        # Catch this error and empty out the value
        except AttributeError:
            item[1]=''

    return data

def build_dict(phone_list):
    ''' iterate through the new list of [user, phone #] entries
        Create new list with new [email, body] format
        format: body ={'phones': [{'type': 'mobile', 'value': '7601234567'}]}

        params: phone_list  : list of lists
        return: list of lists [ str , dict ]
    '''

    for user in phone_list:
        user[1] = {'phones': [{'type': 'mobile' , 'value': user[1]}]}
    return phone_list

def get_service():
    ''' Boilerplate from google to access API '''

    # Setup the Admin SDK Directory API

    # Admin SDK directory scope for users
    SCOPES = 'https://www.googleapis.com/auth/admin.directory.user'

    # Pull credentials if they exist, otherwise authenticate and create/save
    # new credentials
    store = file.Storage('credentials.json')
    creds = store.get()
    if not creds or creds.invalid:
        flow = client.flow_from_clientsecrets('client_secret.json', SCOPES)
        creds = tools.run_flow(flow, store)
    # Build the request object
    return build('admin', 'directory_v1', http=creds.authorize(Http()))

def main():

    # Call the Admin SDK Directory and build API object
    service = get_service()
    # Service is up and now we have to get the csv and create the object
    # for the calls
    results = []  # if needed
    if len(sys.argv):

        dataIter = csvData(sys.argv[1])
        cleanData = clean_phone_data(dataIter)
        for user in build_dict(cleanData):
            try:
                results.append( service.users().update(userKey=user[0], body=user[1]).execute() )
                sleep(.10)
            except errors.HttpError as error:
                print ("An error has occured while upadtating user: {error}".format(error=error))

    print("User numbers updated!")

if __name__ == '__main__':
    main()

"""
    Snip for testing single api call.
    #service.users().update(userKey='hrochin@renovaenergy.com', body=bodyUpdate).execute()
    #bodyUpdate={'phones': [{'type': 'mobile', 'value': '7601234567'}]}

"""