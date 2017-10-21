#!/usr/bin/env python

from flask import Flask
from flask_ask import Ask, statement, question , session


from geopy.geocoders import Nominatim
import urllib



app =Flask(__name__)
ask = Ask(app, "/")

@app.route('/')
def homepage():
    return "Hello"

@ask.launch
def start():
    welcome_message = 'Hello there, Welcome to the HSBC Alexa App. \
    How can I help.'
    return question(welcome_message)

@ask.intent("YesIntent")
def yes_intent():
	return statement("Your balance is $120.00")

@ask.intent("NoIntent")
def no_intent():
	return statement("I'm sorry to hear that.")


@ask.intent("CheckBalance")
def last_transaction():
	return statement("Your balance is $120.00.")


@ask.intent("LastTransaction")
def last_transaction():
	return statement("Your last transaction was $3.95 at Starbucks on Saturday mornning.")






geolocator = Nominatim()
location = geolocator.geocode("School of Computing, Leeds")

link = "https://api.hsbc.com/x-open-banking/v1.2/branches/geo-location/lat/53.8054848/long/-1.5534523?radius=1"
f = urllib.urlopen(link)
myfile = f.read()

count = myfile.count("GeographicLocation")



@ask.intent("BranchesNearby")
def branches_nearby():
	return statement("There are %s branches within a mile." %count)





@ask.intent("PasswordIntent")

def passwordCheck():

	user = Person()
	password = user.passwd

	pwLength = len(password)

	return question("your password is" + password)


@ask.intent("PasswordLetterIntent", convert={"myNum":int})
def numbers(myNum):
	return statement("number is {}".format(myNum))

#Add ability to query last months bills


#Class for information about user if needed
class Person:
	def __init__(self):
		self.name = "User1"
		self.email = "user1@example.com"
		self.bankid = "12345"
		self.passwd = "password123"
		self.securityq = "December"


if __name__ == '__main__':
	app.run(debug=True)