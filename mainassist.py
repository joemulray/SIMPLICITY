#!/usr/bin/env python

from flask import Flask, jsonify
from flask_ask import Ask, statement, question , session
import requests
from geopy.geocoders import Nominatim
import geopy.distance
import datetime

app =Flask(__name__)
ask = Ask(app, "/")

@app.route('/')
def homepage():
    return "Hello"

@ask.launch
def start():
    welcome_message = 'Hello there, Welcome to the HSBC Alexa App. \
    What can we help you with?'
    return question(welcome_message)

@ask.intent("YesIntent")
def yes_intent():
	return statement("Your balance is $120.00")

@ask.intent("NoIntent")
def no_intent():
	return statement("I'm sorry to hear that.")


@ask.intent("LastTransaction")
def last_transaction():
	return statement("Your last transaction was $3.95 at Starbucks on Saturday mornning.")


@ask.intent("PasswordIntent")
def passwordCheck():
	user = Person()
	password = user.passwd
	pwLength = len(password)
	return question("your password is" + password)


@ask.intent("PasswordLetterIntent", convert={"myNum":int})
def numbers(myNum):
	return statement("number is {}".format(myNum))


@ask.intent('AccountBalance')
def balance():
	return statement("Your Account balance is ${}".format(Person().balance))


#@app.route('/test')
@ask.intent('NearestLocation')
def nearest_branch():
	
	geolocator = Nominatim()
	location = geolocator.geocode(Person().address)

	
	userlong = location.longitude
	userlat = location.latitude

	url = "https://api.hsbc.com/x-open-banking/v1.2/branches/geo-location/lat/%s/long/%s" %(userlat, userlong)
	respc = requests.get(url)

	smallest = []
	response = respc.json()

	for store in response:
		storelat = store['GeographicLocation']['Latitude']
		storelong = store['GeographicLocation']['Longitude']

		distance = geopy.distance.vincenty((userlat, userlong), (storelat,storelong))
		smallest.append(distance)

	print smallest
	pos = smallest.index(min(smallest))
	print pos

	miles = smallest[pos].miles
	objadd = response[pos]["Address"]

	address = "%s %s %s, %s" %(objadd["BuildingNumberOrName"], objadd["StreetName"], \
	 objadd["TownName"], objadd["PostCode"])

	weekday = datetime.datetime.now().strftime("%A")
	hours = response[pos]["OpeningTimes"]

	opentime = '0AM'
	closingtime = '0AM'

	for hour in hours:
		if str(hour["OpeningDay"]) == str(weekday):
			opentime = hour["OpeningTime"]
			closingtime = hour["ClosingTime"]


	opentime = opentime[:-8]
	closingtime = closingtime[:-8]
	
	msg = "Based on your location the closest store is %.2f miles away. The address is %s \
	. The store hours for today are %s to %s " %(miles, address, opentime, closingtime)

	return statement(msg)



#Add ability to query last months bills
#Class for information about user if needed
class Person:
	def __init__(self):
		self.name = "User1"
		self.email = "user1@example.com"
		self.bankid = "12345"
		self.passwd = "password123"
		self.securityq = "December"
		self.balance = 124000
		self.postcode = "LS13EY"
		self.address = "The School of Computing, Leeds"


if __name__ == '__main__':
	app.run(debug=True)
