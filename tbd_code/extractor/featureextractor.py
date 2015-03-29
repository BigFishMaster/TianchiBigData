import logging
import sys
from ConfigParser import ConfigParser
import numpy
# use sklearn to classify something.
import sklearn 

import userfeatureextractor
import itemfeatureextractor
import pairfeatureextractor
from timemapper import timemapper

class FeatureExtractor(object):
    def __int__(self, configurefile, prefix = "general", field):
        self.configurefile = configurefile
        self.conf = ConfigParser()
        self.sectionname = prefix
        self.field = field
        if not os.path.exists(configurefile):
            logging.error("fail to call self.conf.init(%s)",configurefile)
            raise Exception('%s not exist'%configurefile)
        self.conf.readfp(open(configurefile,'r'))
        self.featureconfigurefile  =  self.conf.get(self.sectionname,"confname")
    
    def caltimeperiod(self, timelist):
        if len(timelist)%2 != 0:
            logging.error("the time length of the %s set is %d, it must be even!", self.field, len(timelist))
            raise Exception('time list lenght ERROR')
        period = []
        for i in range(len(timelist)/2):
            t1, t2 = timelist[2*i: 2*i + 2]
            period.append(timemapper[t1],timemapper[t2])
        return period
        
    def initfeaturecal(self):
        # field-specific parameters
        timelist = self.conf.get(self.sectionname,self.field+".time").split(',')
        period = self.caltimeperiod(timelist)
        self.period = period
        savename = self.conf.get(self.sectionname,self.field+".savename")
        self.savename = savename
        # global parameters: feature types
        self.featureconfname = self.conf.get(self.sectionname, confname)
        self.featurename = {}
        self.featurename['user'] = self.conf.get(self.sectionname, "user.list").split(",")
        self.featurename['item'] = self.conf.get(self.sectionname, "item.list").split(",")
        self.featurename['pair'] = self.conf.get(self.sectionname, "pair.list").split(",")
        self.featureindex['user'] = self.conf.get(self.sectionname, "user.index")
        self.featureindex['item'] = self.conf.get(self.sectionname, "item.index")
        self.featureindex['pair'] = self.conf.get(self.sectionname, "pair.index")
       
        self.conf.get(self.sectionname, "user.list").split(",")
        
        featcalusedindex = []
        featurecalnames = []
        self.inputimagenames = []
        self.feacals = {}
        self.featureinfos = []
        for i,name in enumerate(featurenames):
            feainfo = self.getnameconf(name)
            index = feainfo['index']
            if feainfo['inputimagename'] not in self.inputimagenames:
                self.inputimagenames.append(feainfo['inputimagename'])
            feacalkey = ( feainfo['classname'],feainfo['prefix'])
            if feacalkey  not in self.feacals:
                self.feacals[feacalkey]= {'cal':None,'usedindex':[index]}
            else:
                if index not in self.feacals[feacalkey]['usedindex']:
                    self.feacals[feacalkey]['usedindex'].append(index)
            self.featureinfos.append(feainfo)
# field: train, val, test
# configfilename: used to initialize time period and feature type.
def calfeatures(field, configfilename):
    feacal  = FeatureExtractor(configfilename,'featurecal', field)

# classification:
# feature: [[],[],[]]
# label: [,,]
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