#!/usr/bin/env python

from flask import Flask
from flask_ask import Ask, statement, question , session


app =Flask(__name__)
ask = Ask(app, "/")

@app.route('/')
def homepage():
    return "HSBC Alexa Homepage"

@ask.launch
def start():
    welcome_message = 'Hello there, Welcome to the HSBC Alexa App\
    .. What can we help you with'
    return question(welcome_message)



@ask.intent("YesIntent")
def yes_intent():
	return statement("Your balance is $120.00")

@ask.intent("NoIntent")
def no_intent():
	return statement("I'm sorry to hear that.")

@ask.intent('AccountIntent')
def account_intent():

	return statement("Your Account number is {}".format(Person().balance))

@ask.intent('AccountBalance')
def balance():

	return statement("Your Account balance is ${}".format(Person().balance))



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


if __name__ == '__main__':
	app.run(debug=True)