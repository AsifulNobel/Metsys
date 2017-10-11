from .BanglaNLP.banglaResponder import response_message as banglaMessage
from .BanglaNLP.banglaResponder import initialize as initBangla
from .BanglaNLP.banglaResponder import train as trainBangla
from .EnglishNLP.englishResponder import response_message as englishMessage
from .EnglishNLP.englishResponder import initialize as initEnglish
from .EnglishNLP.englishResponder import train as trainEnglish
import logging

logger = logging.getLogger(__name__)

def isEnglish(s):
    try:
        s.encode(encoding='utf-8').decode('ascii')
    except UnicodeDecodeError:
        return False
    else:
        return True

def response_message(message):
    if isEnglish(message):
        logger.debug("English Message found, passing to english agent")
        return englishMessage(message)
    else:
        logger.debug("Bangla Message found, passing to bangla agent")
        return banglaMessage(message)

def initAgents():
    initEnglish()
    initBangla()

def trainEnglishAgent():
    trainEnglish()
    initEnglish()

def trainBanglaAgent():
    trainBangla()
    initBangla()
