import sys
import os
from os.path import dirname
from mycroft.skills.core import MycroftSkill
from mycroft.skills.core import intent_handler, intent_file_handler
from adapt.intent import IntentBuilder
from mycroft.configuration import ConfigurationManager
from mycroft.util import resolve_resource_file
from mycroft.util.log import getLogger
from subprocess import Popen, PIPE, check_output
from HTMLParser import HTMLParser
import requests
import json
import random
import time

# @JarbasAI local listener
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from localstt import *

__author__ = 'tjoen'

LOGGER = getLogger(__name__)

validmc = [ '1', '2', '3', '4']
yesno = [ 'yes', 'no']
score = 0
right = ['Right!', 'That is correct', 'Yes, you are right', 'That is the right answer', 'Yes, good answer', 'Excellent choice']
wrong = ['That is incorrect', 'Wrong answer', 'Sorry, you are wrong', 'That is not the right answer', 'You are wrong']
config = ConfigurationManager.get()
end = False
restart = False

class LsttSkill(MycroftSkill):
    def __init__(self):
        super(LsttSkill, self).__init__(name="LsttSkill")
        LOGGER.info("Starting Lstt")

    def initialize(self):
	lstt_intent = IntentBuilder("LsttIntent").\
            require("LsttKeyword").build()
        self.register_intent(lstt_intent, self.handle_lstt_intent)
	
    def invalid(self):
        self.say("I did not understand you.")
	self.runpocketsphinx("Please choose 1, 2, 3 or 4.", False, validmc)
	
    def repeat(self):
        self.say('I will repeat the question')
        self.repeatquestion( self.settings.get('cat'), self.settings.get('question'), self.settings.get('answers'), self.settings.get('correct_answer'))
	self.runpocketsphinx("Please choose 1, 2, 3 or 4.", False, validmc)

    def askstop(self):
	response = self.runpocketsphinx("Would you like to stop?", False, yesno)
	if response == 'yes':
            global end
            end = True
	    self.endgame()
	else:
	    self.runpocketsphinx("Choose 1,2,3 or 4", False, validmc)
	
    def help(self):
	self.runpocketsphinx("I can not help you. What is your answer?", False, validmc)


    def start(self):
	response = self.runpocketsphinx("Would you like to restart?", False, yesno)
	if response == 'yes':
	    self.handle_trivia_intent()
            global end
            end = True
            global restart
            restart = True
	else:
	    self.runpocketsphinx("Choose 1,2,3 or 4", False, validmc)

	
    def mychoice(self, x):
        try:
            return {
        'ONE': '1',
        'TWO': '2',
        'THREE': '3',
        'FOUR': '4',
        'FIVE': '5',
        'SIX': '6',
        'SEVEN': '7',
        'EIGHT': '8',
        'NINE': '9',
        'TEN': '10',
        'REPEAT': 'repeat',
        'STOP': 'stop',
        'PAUZE': 'pauze',
        'END': 'stop',
        'START': 'start',
        'QUIT': 'stop',
        'NEVER': 'invalid',
        'MIND': 'invalid',
        'HELP': 'help',
        'PLAY': 'start',
        'YES': 'yes',
        'NO': 'no',
            }[x]
        except KeyError:
            return 'invalid'

    def say(self, text):
        cmd = ['mimic','--setf','int_f0_target_mean=107','--setf' 'duration_stretch=0.83','-t']
        cmd.append(text)
        p = Popen(cmd)
	p.wait()

    def playsmpl(self, filename):
        cmd = ['aplay', str(filename)]
	p = Popen(cmd)

    def handle_record_begin(self):
        LOGGER.info("Lsst - Begin Recording...") 
        # If enabled, play a wave file with a short sound to audibly
        # indicate recording has begun.
        if config.get('confirm_listening'):
            file = resolve_resource_file(
                config.get('sounds').get('start_listening'))
            if file:
                self.playsmpl(file)

    def handle_record_end(self):
        LOGGER.info("Lsst - End Recording...")
    
    def score(self, point):
        global score
        score = score+point
        self.enclosure.mouth_text( "SCORE: "+str(score) )
        return

    def wrong(self, right_answer):
        self.enclosure.mouth_text( "WRONG!" )
	self.say(random.choice(wrong))
        self.playsmpl( self.settings.get('resdir')+'false.wav' )
        self.say("The answer is "+right_answer)
        return

    def right(self):
        self.enclosure.mouth_text( "CORRECT!" )
        self.say(random.choice(right))
        self.playsmpl( self.settings.get('resdir')+'true.wav' )
        self.score(1)
        return    

    def preparequestion(self, category, question, answers, right_answer):
        h = HTMLParser()
        quest = h.unescape( question )
        self.say("The category is "+ category+ ".")
        correct_answer = h.unescape( right_answer )
        allanswers = list()
        allanswers.append(h.unescape(right_answer))
        for a in answers:
            allanswers.append(h.unescape(a))
        random.shuffle(allanswers)
        self.settings['cat'] = category
        self.settings['question'] = quest
        self.settings['answers'] = allanswers
        self.settings['correct_answer'] = correct_answer
        self.askquestion( category, quest, allanswers, correct_answer )
    
    def repeatquestion(self, category, question, answers, right_answer):
        self.say( question )
        i=0
        for a in answers:
            i = i + 1
            self.say(str(i) + ".    " + a)
        return

    def runpocketsphinx(self, msg, somefunc, arr):
        reset_decoder( None, self.settings.get('resdir')+'localstt.lm' , self.settings.get('resdir')+'localstt.dic')
	self.say( msg )
	local = LocalListener()
        rt = local.listen_once()
        selection = self.mychoice(rt)
        if selection in arr:
            # Do the thing
            self.settings['myanswer'] = selection
            return selection
        elif selection == 'repeat':
            self.repeat()
        elif selection == 'stop':
            self.askstop()
        elif selection == 'help':
            self.help()
        elif selection == 'start':
            self.start()
        else:
            self.invalid()      


    def askquestion( self, category, quest, allanswers, correct_answer):
        i=0
        self.enclosure.mouth_text( "?   ?   ?   ?   ?   ?   ?   ?   ?   ?   ?" )
        self.say( quest )
        for a in allanswers:
            i = i + 1
            self.say(str(i) + ".    " + a)
        self.runpocketsphinx("Choose 1,2,3 or 4.", False, validmc)
        response2 = self.settings.get('myanswer')
	if not end:
            self.say("Your answer is "+ str(response2))
            if correct_answer == allanswers[int(response2)-1]:
                self.right()
            else:
                self.wrong(correct_answer)
        return 

    def endgame(self):
	if restart:
            global score
            score = 0
            self.handle_trivia_intent()
        else:
            self.enclosure.mouth_text( "SCORE: "+str(score) )
            self.say("You answered " +str(score)+ " questions correct")
            self.say("Thanks for playing!")
	    global end
	    end = False
            self.playsmpl( self.settings.get('resdir')+'end.wav' )
            self.stop()
    
    def handle_trivia_intent(self):
        self.enclosure.deactivate_mouth_events()
        # Display icon on faceplate
        self.enclosure.mouth_display("aIMAMAMPMPMPMAMAAPAPADAAIOIOAAAHAMAMAHAAIOIOAAAPAFAFAPAAMLMLAAAAAA", x=1, y=0, refresh=True)
        self.settings['cat'] = None
        self.settings['question'] = None
        self.settings['answers'] = None
        self.settings['myanswer'] = None
        self.settings['correct_answer'] = None
        self.settings['resdir'] = '/opt/mycroft/skills/lstt-skill/res/'
        # get mycroft location for hmm model
        cmd = 'pip show mycroft_core | grep Location'
        reply = check_output(cmd, shell=True) 
        self.settings['hmm'] = reply .split()[1]+'/mycroft/client/speech/recognizer/model/en-us/hmm/'
        #url = "https://opentdb.com/api.php?amount=5&type=multiple"
	url = "https://opentdb.com/api.php?amount=3&category=9&type=multiple"
        headers = {'Accept': 'text/plain'}
        r = requests.get(url, headers)
        m = json.loads(r.text)
        questions = m['results'];
        global score
        score = 0
        self.playsmpl( self.settings.get('resdir')+'intro.wav' )
        self.say("Okay, lets play a game of trivia. Get ready!")
        for f in questions:
	    if not end:
            self.preparequestion( f['category'], f['question'], f['incorrect_answers'], f['correct_answer'])
	self.endgame()
    
    def stop(self):
        self.enclosure.reset()    
        LOGGER.info("Starting speech-client" )
        pass

    def handle_lstt_intent(self, message):
        LOGGER.info("Stopping speech-client")
	self.handle_trivia_intent()        


def create_skill():
      return LsttSkill()
