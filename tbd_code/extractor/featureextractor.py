import logging
import sys
from ConfigParser import ConfigParser

import userfeatureextractor
import itemfeatureextractor
import pairfeatureextractor


class FeatureExtractor(object):
    def __int__(self, configurefile):
        self.configurefile = configurefile
        self.conf = ConfigParser()
def calfeatures(field, configfilename):
    # field: train, val, test
    # configfilename: used to initialize time period and feature type.

def train(field, configfilename):
    
def evaluate(field, configfilename):

def submit(field, configfilename):

    
if __name__ == '__main__':
    LOG_LEVEL = logging.DEBUG
    logging.basicConfig(level=LOG_LEVEL,
                format="%(levelname)s:%(name)s:%(funcName)s->%(message)s",  #logging.BASIC_FORMAT,
                datefmt='%a, %d %b %Y %H:%M:%S')
    if len(sys.argv)>1 :
        func = getattr(sys.modules[__name__], sys.argv[1])
        func(*sys.argv[2:])
    else:
        print >> sys.stderr,'debugsearch.py command'