#!/usr/bin/env python

from flask import Flask
from flask_ask import Ask, statement, question , session


app =Flask(__name__)
ask = Ask(app, "/")

@app.route('/')
def homepage():
    return "Hello"


if __name__ == '__main__':
	app.run(debug=True)