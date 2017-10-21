#!/usr/bin/env python


from flask import Flask, render_template, jsonify
from flask_ask import Ask, statement, question , session, convert_errors
import requests
from geopy.geocoders import Nominatim
import geopy.distance
import datetime
from afg import Supervisor
from random import randint
import urllib


app =Flask("Bank")



app =Flask(__name__)
ask = Ask(app, "/")
sup = Supervisor("scenario.yaml")


#dictionary for converting number to messages
#need to decide max pin length
nth = {
	0: "first",
	1: "second",
	2: "third",
	3: "fourth"
}


@ask.on_session_started
@sup.start
def new_session():
    app.logger.debug('new session started')


@sup.stop
def close_user_session():
    logger.debug("user session stopped")


@ask.session_ended
def session_ended():
    close_user_session()
    return "", 200

@ask.intent('AMAZON.HelpIntent')
def help_user():
    context_help = sup.get_help()
    # context_help string could be extended with some dynamic information
    return question(context_help)

#start module after calling skill
@ask.launch
@sup.guide
def launched():
    return question(render_template("welcome"))

#select branch module
@ask.intent("SelectBranchModule")
@sup.guide
def BranchSelected():
	return question(render_template("branch_welcome"))


#number of nearby branches
@ask.intent("BranchesNearby")
def num_branches_nearby():
	geolocator = Nominatim()
	location = geolocator.geocode("School of Computing, Leeds")

	link = "https://api.hsbc.com/x-open-banking/v1.2/branches/geo-location/lat/53.8054848/long/-1.5534523?radius=1"
	f = urllib.urlopen(link)
	myfile = f.read()
	count = myfile.count("GeographicLocation")
	return statement("There are %s branches within a mile." %count)

#nearest branch
@ask.intent('NearestLocation')
@sup.guide
def nearest_branch():
	
	geolocator = Nominatim()
	location = geolocator.geocode(Person().address)
	
	userlong = location.longitude
	userlat = location.latitude

	url = "https://api.hsbc.com/x-open-banking/v1.2/branches/geo-location/lat/%s/long/%s" %(userlat, userlong)

	respc = requests.get(url)
	smallest = []
	response = respc.json()

	if not response:
		return statement("Sorry, I could not find any stores near your address")

	for store in response:
		storelat = store['GeographicLocation']['Latitude']
		storelong = store['GeographicLocation']['Longitude']

		distance = geopy.distance.vincenty((userlat, userlong), (storelat,storelong))
		smallest.append(distance)

	pos = smallest.index(min(smallest))

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
	
	msg = "Based on your location the closest store is %.2f miles away. The address is %s. \
	The store hours for today are %s to %s " %(miles, address, opentime, closingtime)

	return statement(msg)


@ask.intent("SelectBalanceModule")
@sup.guide
def BalanceSelected():
	user = Person()

	session.attributes["PinPosition"] = randint(0, len(user.pin)-1)
	positionToMsg = nth[session.attributes["PinPosition"]]


	return question("Please say the " + positionToMsg + " number of your pin.")

@ask.intent("InputPin", convert={"PinNum":int})
@sup.guide
def PinCheck(PinNum):
	if PinNum not in [0,1,2,3,4,5,6,7,8,9]:
		return sup.reprompt_error()

	user = Person()
	correctPin = user.pin[session.attributes["PinPosition"]]

	if (PinNum == int(correctPin)):
		return statement("pin correct. Logging in")
	else:
		return statement("Pin incorrect. returning to module selection")







#Add ability to query last months bills
#Class for information about user if needed
class Person:
	def __init__(self):
		self.name = "User1"
		self.email = "user1@example.com"
		self.bankid = "12345"
		self.passwd = "password123"
		self.securityq = "December"

		self.pin = "1234"

		self.balance = 124000
		self.postcode = "LS13EY"
		self.address = "Calverley St, Leeds"



if __name__ == '__main__':
	app.run(debug=True)
