<a href="https://www.buymeacoffee.com/mulrex" target="_blank"><img src="https://www.buymeacoffee.com/assets/img/custom_images/yellow_img.png" alt="Buy Me A Coffee" style="height: auto !important;width: auto !important;" ></a>

# SIMPLICITY
FinTech Hackathon

Integration of digital banking with personal assistant technology :thumbsup:
 

### Prerequisites
* virtualenv
* pip
* ngrok
* Amazon Developer Account

### Installation

```
git clone https://github.com/joemulray/SIMPLICITY.git
cd SIMPLICITY
```

### Activate virtualenv, install requirements

```
virtualenv .
source bin/activate

pip install -r requirements.txt
python mainassist.py

#Default port 5000 for flask environment
#In new shell, start ngrok service on same port as flask
ngrok http <port>
```

### Instructions
* Make sure ngrok is running on same port as flask_ask
* Put all the needed information in Amazon Dev account in Alexa Skill (All neccecities inside git repo)
* [Amazon Echo Skill Testing Tool](https://echosim.io/)
* Enjoy :)


### Usage
* Follow the instructions returned via alexa to navigate app features


### Features
* Scenario based conversation -> can not call functions that are outside the context of current conversation
* Smart identity confirmation -> asks for random number positions of a pin (just like signing in online banking)
* Broad range of functions:
    * Nearest branch
    * Number of nearby branches
    * Nearest ATM
    * Check account balance
    * Transfer between accounts


### Limitations
* Dependent on Alexa voice recognition software
    * Function calling phrases may be similar to default Alexa phrases, thus may result in incorrect redirections
    * Voice to text is not 100% accurate. This will break out of the scenario path
    * May have security issues -> do not know how voice data is transferred to backend (encryption)


### Acknoledgement
* Flask-Ask library to enable Alexa to python connection
* Alexa Flask-ASK Guide library as addon to Flask-Ask to allow scenario based conversations
* Echosim.io for Alexa emulation during testing
