## Trivia skill with local stt
This skill starts a game of general trivia with local speech-to-text.

## Description 
This skill uses mycrofts pocketsphinx STT with a small dict.

It uses a localstt.dic (dictionary) and localstt.lm (language model) in the res folder.

At the moment, the skill will ask you 3 "general knowledge" questions. 
You can answer by choosing 1,2,3 or 4.

Yes, No, Stop, Repeat and Start should also work.

This started out as an experiment, checking if a faster method could make the  game more playable. 
And it actually does seem to work pretty good. 

Translations might be a problem with this method, but this skill uses questions in english. 



## Current state
Working features:
- Version seems to work fine, the skill uses naptime during the skill
- great speed improvement on speech results.

## Known issues:
Master version is using @JArbasAI local-listener, seems to work, using a dict with numbers.

## Examples 
* "Hey Mycroft, start local speech"
* "Hey Mycroft, play trivia"
* "Hey Mycroft, game of trivia"

## Credits 
Theun Kohlbeck, https://github.com/tjoen
Steen Bentall, https://github.com/barricados
JarbasAI, https://github.com/JarbasAI

## Require 
platform_mark1 platform_picroft platform_plasmoid 
