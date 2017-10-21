#!/usr/bin/env python

from flask import Flask
from flask_ask import Ask, statement, question , session


app =Flask(__name__)
ask = Ask(app, "/")

@app.route('/')
def homepage():
    return "Hello"

@ask.launch
def start():
    welcome_message = 'Hello there, Welcome to the HSBC Alexa App. \
    Would you like to hear your balance.'
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