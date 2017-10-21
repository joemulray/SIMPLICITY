#!/usr/bin/env python

from flask import Flask, render_template
from flask_ask import Ask, statement, question , session, convert_errors
from afg import Supervisor
from random import randint

app =Flask("Login")
ask = Ask(app, "/")
sup = Supervisor("scenario.yaml")

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


@ask.launch
@sup.guide
def launched():
    return question(render_template("welcome"))


@ask.intent("SelectBranchModule")
@sup.guide
def BrachSelected():
	return statement("your branch is here. returning to the start")



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

#dictionary for converting number to messages
#need to decide max pin length
nth = {
	0: "first",
	1: "second",
	2: "third",
	3: "fourth"
}

@ask.intent("YesIntent")
@sup.guide
def yes_intent():
	return statement("Your balance is $120.00")

@ask.intent("NoIntent")
@sup.guide
def no_intent():
	return statement("I'm sorry to hear that.")

#Class for information about user if needed
class Person:
	def __init__(self):
		self.name = "User1"
		self.email = "user1@example.com"
		self.bankid = "12345"
		self.passwd = "password123"
		self.securityq = "December"
		self.pin = "1234"


if __name__ == '__main__':
	app.run(debug=True)