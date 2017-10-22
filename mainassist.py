#!/usr/bin/env python


from flask import Flask, render_template, jsonify
from flask_ask import Ask, statement, question , session, convert_errors
import requests
from geopy.geocoders import Nominatim
import geopy.distance
import datetime
from afg import Supervisor
import random
import urllib


app =Flask("Bank")
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
#initialise account types for checks in transfer, balance and pay modules
AccountTypes = [
	"savings",
	"checking",
	"isa"
]


#functions for security checks at login
#reset number of tries
def PinCheckReset():
	session.attributes["PinCorrectTotal"] = 0
	session.attributes["PinIncorrectTotal"] = 0
#remove position from rand position generator list after position has been generated
def PinRemoveCurrentPosition():
	session.attributes["AllowedValues"].remove(session.attributes["PinPosition"])
#generate current pin position for the user to input
def PinGenPosition():
	session.attributes["PinPosition"] = random.choice(session.attributes["AllowedValues"])
#convert number to word using nth dictionary e.g. "0" -> "first"
def PinGetMsg():
	return nth[session.attributes["PinPosition"]]
#increase correct entry total by 1 after successful entry
def PinTotalAdd():
	session.attributes["PinCorrectTotal"] += 1
#increase incorrect entry by 1 after unsuccessful entry
def PinTotalSub():
	session.attributes["PinIncorrectTotal"] += 1
#operation looper controls
def ResetLooperSelector():
	session.attributes["LooperSelector"] = 0



#initialise session start and end functions etc.
#very important
@ask.on_session_started
@sup.start
def new_session():
	#initiate looperselector for later operations
	ResetLooperSelector()
	app.logger.debug('new session started')

@sup.stop
def close_user_session():
    app.logger.debug("user session stopped")

@ask.session_ended
def session_ended():
    close_user_session()
    return "", 200
#initialise help function (user says "Help" during anytime inside main route for help message)
@ask.intent('AMAZON.HelpIntent')
def help_user():
    context_help = sup.get_help()
    # context_help string could be extended with some dynamic information
    return question(context_help)


#Start scenario after skill calling
@ask.launch
@sup.guide
def launched():
	return question(render_template("welcome"))
#initiate looping functions (empty functions that gets called to trigger difference routes in scenario.yaml)
#holy shit loops!!!
@sup.guide
def NoMoveOn():
	print "do not move on"

@sup.guide
def MoveOn():
	print "move on"

@sup.guide
def LockAccount():
	print "fraud? account locked"

#Layer 1 of scenario
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

#nearest ATM
@ask.intent('NearestATM')
@sup.guide
def nearest_atm():
	geolocator = Nominatim()
	location = geolocator.geocode(Person().address)
	
	userlong = location.longitude
	userlat = location.latitude

	url = "https://api.hsbc.com/x-open-banking/v1.2/atms/geo-location/lat/%s/long/%s" %(userlat, userlong)

	respc = requests.get(url)
	smallest = []
	response = respc.json()

	if not response:
		return statement("Sorry, I could not find any ATM's near your address")

	for atm in response:
		atmlat = atm['GeographicLocation']['Latitude']
		atmlong = atm['GeographicLocation']['Longitude']

		distance = geopy.distance.vincenty((userlat, userlong), (atmlat,atmlong))
		smallest.append(distance)

	pos = smallest.index(min(smallest))

	miles = smallest[pos].miles
	objadd = response[pos]["Address"]

	address = "%s %s, %s" %(objadd["StreetName"], \
	objadd["TownName"], objadd["PostCode"])

	msg = "Based on your location the closest ATM is %.2f miles away. The address is %s. \
	" %(miles, address)

	return statement(msg)
	
#Nearest branch
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
		return statement("Sorry, I could not find any HSBC banks near your address")

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
	
	msg = "Based on your location the closest HSBC bank is %.2f miles away. The address is %s. \
	The bank hours for today are %s to %s " %(miles, address, opentime, closingtime)

	return statement(msg)

#Id check for bank account operations
@ask.intent("LoginModule")
@sup.guide
def LoginSelected():
	user = Person()

	PinCheckReset()
	session.attributes["AllowedValues"] = list(range(len(user.pin)))

	PinGenPosition()
	PinRemoveCurrentPosition()
	positionToMsg = PinGetMsg()


	return question("Please say the " + positionToMsg + " number of your pin.")


#layer 2 of scenario
#id checking with pin check loop
@ask.intent("InputPin", convert={"PinNum":int})
@sup.guide
def PinCheck(PinNum):
	#ignore any none single digit entries
	if PinNum not in [0,1,2,3,4,5,6,7,8,9]:
		return sup.reprompt_error()
	#find correct pin for the current position
	user = Person()
	correctPin = user.pin[session.attributes["PinPosition"]]
	#checks with input
	#proceed to next layer for three times correct
	#lock account for three times incorrect
	if (PinNum == int(correctPin)):
		PinTotalAdd()
		if (session.attributes["PinCorrectTotal"] >= 3):
			MoveOn()
			PinCheckReset()
			return question(render_template("account_welcome"))
		else:
			NoMoveOn()
			PinGenPosition()
			PinRemoveCurrentPosition()
			msg = PinGetMsg()
			return question("Pin correct. Please say the " + msg + " number of your pin.")
	else:
		PinTotalSub()
		if (session.attributes["PinIncorrectTotal"] >= 3):
			LockAccount()
			PinCheckReset()
			return statement("Too many incorrect entries. account locked.")
		else:
			NoMoveOn()
			msg = PinGetMsg()
			return question("Pin incorrect. please say the " + msg + " number of your pin.")


#layer 3 account operations hub
#hub functions to explain how to initiate each type of operation
@ask.intent("TransferExplaination")
@sup.guide
def TransferExplain():
	return question(render_template("transfer_welcome"))

@ask.intent("BalanceExplaination")
@sup.guide
def BalanceExplain():
	return question(render_template("balance_welcome"))


#layer 4 actual account operations
#show account balance
@ask.intent("ViewBalance", convert={"accountToView":"ACCOUNT"})
@sup.guide
def ViewBalance(accountToView):
	if accountToView not in AccountTypes:
		return sup.reprompt_error()

	account = Person()
	for item in AccountTypes:
		if item == accountToView:
			accountBalance = getattr(account, item)
			session.attributes["LooperSelector"] = 2
			return question("Your %s account balance is: %s pounds. Would you like to view another account balance?" %(item, accountBalance))

#transfer between accounts
@ask.intent("TransferIntent", convert={"amount":int, "accountone": "ACCOUNT", "accounttwo": "ACCOUNT"})
@sup.guide
def transfer_internal(amount, accountone, accounttwo):

	account = Person()

	if accountone not in AccountTypes:
		return sup.reprompt_error()

	if accounttwo not in AccountTypes:
		return sup.reprompt_error()

	msg1 = ""
	msg2 = ""

	for item in AccountTypes:
		if item == accountone:
			old = getattr(account, item)
			current = getattr(account, item) - amount
			if (current < 0):
				session.attributes["LooperSelector"] = 1
				return question("not enough funds in %s for transfer. Would you like to make another transfer?" %(item))
			else:
				setattr(account, item, current)
				msg1 = "Your %s before was %s. Now it is %s. " %(item, old, current)  

		if item == accounttwo:
			old = getattr(account, item)
			current = getattr(account, item) + amount
			setattr(account, item, current)
			msg2 = " Your %s before was %s. Now it is %s. " %(item, old, current)  
	session.attributes["LooperSelector"] = 1
	return question(msg1 + msg2 + "Would you like to make another transfer?")

@ask.intent("AMAZON.YesIntent")
@sup.guide
def OperationLoop():
	if (session.attributes["LooperSelector"] == 1):
		RepeatTransfer()
		ResetLooperSelector()
		return question(render_template("transfer_welcome"))
	elif (session.attributes["LooperSelector"] == 2):
		RepeatBalance()
		ResetLooperSelector()
		return question(render_template("balance_welcome"))
	else:
		return statement("looper broken, please contact system admin.")

@ask.intent("AMAZON.NoIntent")
@sup.guide
def NoLoop():
	return statement("thank you for using hsbc service.")


@sup.guide
def RepeatTransfer():
	print "repeating transfer"
  
@sup.guide
def RepeatBalance():

#stop and cancel commands to cancel anything
@ask.intent('AMAZON.StopIntent')
def stop():
    #close_user_session()
    return statement(render_template('stop'))

@ask.intent('AMAZON.CancelIntent')
def cancel():
	#close_user_session()
	return statement(render_template('cancel'))



#stub class for user info
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
		self.checking = 10000
		self.savings = 5000
		self.isa = 1000


if __name__ == '__main__':
	app.run(debug=True)
