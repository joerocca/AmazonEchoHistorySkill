"""
History
AUTHOR: JOE ROCCA
"""

from __future__ import print_function
import httplib
import json
from random import randint
from datetime import datetime
import calendar

# --------------- MAIN FUNCTIONS ----------------------

def lambda_handler(event, context):
    """ Route the incoming request based on type (LaunchRequest, IntentRequest,
    etc.) The JSON body of the request is provided in the event parameter.
    """
    print("event.session.application.applicationId=" +
          event['session']['application']['applicationId'])

    """
    Uncomment this if statement and populate with your skill's application ID to
    prevent someone else from configuring a skill that sends requests to this
    function.
    """
    if (event['session']['application']['applicationId'] !=
            "amzn1.echo-sdk-ams.app.31a363aa-6d34-48bc-bb56-1064a16a14c8"):
        raise ValueError("Invalid Application ID")

    if event['session']['new']:
        on_session_started({'requestId': event['request']['requestId']},
                           event['session'])

    if event['request']['type'] == "LaunchRequest":
        return on_launch(event['request'], event['session'])
    elif event['request']['type'] == "IntentRequest":
        return on_intent(event['request'], event['session'])
    elif event['request']['type'] == "SessionEndedRequest":
        return on_session_ended(event['request'], event['session'])


def on_session_started(session_started_request, session):
    """ Called when the session starts """

    print("on_session_started requestId=" + session_started_request['requestId']
          + ", sessionId=" + session['sessionId'])


def on_launch(launch_request, session):
    """ Called when the user launches the skill without specifying what they
    want
    """

    print("on_launch requestId=" + launch_request['requestId'] +
          ", sessionId=" + session['sessionId'])
    # Dispatch to your skill's launch
    return get_welcome_response()


def on_intent(intent_request, session):
    """ Called when the user specifies an intent for this skill """

    print("on_intent requestId=" + intent_request['requestId'] +
          ", sessionId=" + session['sessionId'])

    intent = intent_request['intent']
    intent_name = intent_request['intent']['name']

    # Dispatch to your skill's intent handlers
    
    if intent_name == "TodayInHistoryIntent":
        return get_today_in_history()
    elif intent_name == "TodayInHistoryWithDateIntent":
        return get_today_in_history_for_date(intent, session)
    elif intent_name == "AMAZON.HelpIntent":
        return get_welcome_response()
    elif intent_name == "AMAZON.CancelIntent" or intent_name == "AMAZON.StopIntent":
        return handle_session_end_request()
    else:
        raise ValueError("Invalid intent")


def on_session_ended(session_ended_request, session):
    """ Called when the user ends the session.

    Is not called when the skill returns should_end_session=true
    """
    print("on_session_ended requestId=" + session_ended_request['requestId'] +
          ", sessionId=" + session['sessionId'])
    # add cleanup logic here

# --------------- FUNCTIONS THAT CONTROL THE SKILLS BEHAVIOR ------------------


def get_welcome_response():
    """ If we wanted to initialize the session to have some attributes we could
    add those here
    """

    session_attributes = {}
    card_title = "Welcome"
    speech_output = "Welcome to History. " \
                    "Ask me about history on any date." 
                    
    # If the user either does not reply to the welcome message or says something
    # that is not understood, they will be prompted again with this text.
    reprompt_text = "Ask for a historical fact by saying, " \
                    "What happened today in history."
    should_end_session = False
    return build_response(session_attributes, build_speechlet_response(
        card_title, speech_output, reprompt_text, should_end_session))


def handle_session_end_request():
    card_title = "Session Ended"
    speech_output = "Thank you for trying history. " \
                    "Have a nice day! "
    # Setting this to true ends the session and exits the skill.
    should_end_session = True
    return build_response({}, build_speechlet_response(
        card_title, speech_output, None, should_end_session))

# --------------- HANDLE HISTORY INTENTS ----------------------

def get_today_in_history():
    session_attributes = {}
    reprompt_text = None
    fact = fetchFactForToday()
    should_end_session = True

    return build_response(session_attributes, build_speechlet_response(
        'Today in History', fact, reprompt_text, should_end_session))
        
def get_today_in_history_for_date(intent, session):
    date = intent['slots']['DATE']['value']
    dt = datetime.strptime(date, '%Y-%m-%d')
    month = dt.month
    day = dt.day
    session_attributes = {}
    reprompt_text = None
    fact = fetchFactForDay(month, day)
    should_end_session = True
    
    return build_response(session_attributes, build_speechlet_response(
        'History', fact, reprompt_text, should_end_session))

# --------------- HELPERS THAT BUILD ALL RESPONSES ----------------------


def build_speechlet_response(title, output, reprompt_text, should_end_session):
    return {
        'outputSpeech': {
            'type': 'PlainText',
            'text': output
        },
        'card': {
            'type': 'Simple',
            'title': title,
            'content': output
        },
        'reprompt': {
            'outputSpeech': {
                'type': 'PlainText',
                'text': reprompt_text
            }
        },
        'shouldEndSession': should_end_session
    }


def build_response(session_attributes, speechlet_response):
    return {
        'version': '1.0',
        'sessionAttributes': session_attributes,
        'response': speechlet_response
    }
    
# --------------- HISTORY FACT FETCHERS ----------------------

def fetchFactForToday():
	conn = httplib.HTTPConnection('history.muffinlabs.com')
	conn.request("GET", "/date")
	r1 = conn.getresponse()
	facts = json.loads(r1.read())['data']['Events']
	count = len(facts)
	i = randint(0, count)
	factObject = facts[i]
	factText = factObject['text']
	factYear = factObject['year']
	formattedFact = 'Today in ' + factYear + ', ' + factText
	print (factYear)
	print (factText)
	print (formattedFact)
	return formattedFact

def fetchFactForDay(month, day):
	conn = httplib.HTTPConnection('history.muffinlabs.com')
	conn.request("GET", "/date/" + str(month) + "/" + str(day))
	r1 = conn.getresponse()
	facts = json.loads(r1.read())['data']['Events']
	count = len(facts) - 1
	i = randint(0, count)
	factObject = facts[i]
	factText = factObject['text']
	factYear = factObject['year']
	formattedFact = 'On ' + calendar.month_name[month] + ' ' + str(day) + ' in ' + factYear + ', ' + factText
	print (factYear)
	print (factText)
	print (formattedFact)
	return formattedFact

    