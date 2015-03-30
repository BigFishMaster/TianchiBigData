import logging
import sys
from ConfigParser import ConfigParser
import numpy
# use sklearn to classify something.
import sklearn 
import cPickle
import os
import userfeatureextractor
import itemfeatureextractor
import pairfeatureextractor
import labelextractor
from timemapper import timemapper

class LabelExtractor(object):
    def __int__(self, configurefile, prefix = "general", field):
        self.configurefile = configurefile
        self.conf = ConfigParser()
        self.sectionname = prefix
        self.field = field
        if not os.path.exists(configurefile):
            logging.error("fail to call self.conf.init(%s)",configurefile)
            raise Exception('%s not exist'%configurefile)
        self.conf.readfp(open(configurefile,'r'))
        self.initlabelcal()
    def caltimeperiod(self, timelist):
        if len(timelist)%2 != 0:
            logging.error("the time length of the %s set is %d, it must be even!", self.field, len(timelist))
            raise Exception('time list lenght ERROR')
        period = []
        for i in range(len(timelist)/2):
            t1, t2 = timelist[2*i: 2*i + 2]
            period.append(timemapper[t1],timemapper[t2])
        return period
        
    def initlabelcal(self):
        # field-specific parameters
        timelist = self.conf.get(self.sectionname,self.field+"label.time").split(',')
        period = self.caltimeperiod(timelist)
        self.period = period
        savename = self.conf.get(self.sectionname,self.field+"label.savename")
        self.savename = savename     
        # globale 
        self.savefolder = self.conf.get(self.sectionname, "savefolder")
    def process(self):
        #labels:
        # userid, itemid, label
        labels = labelextractor.extract(self)
        if self.savename != "":
            #save 
            np.save(os.path.join(self.savefolder, self.savename), labels)
            # load
            # lab = np.load("name").all()
        
    def combine(self, fea, feaindex):
        if "pair" not in fea:
            logging.error("No pair feature calcualted")
            raise Exception('NO PAIR FEATURE ERROR!')
        #useridlist = fea['pair']['userid']
        #itemidlist = fea['pair']['itemid']
        if len(fea) == 1 and "pair" in fea:
            return fea["pair"]
        
        for index in feaindex:
            emptycount = 0
            f = fea[index]
            ids = f['id'] # elements in ids are unique to each other.
            ff = f['fea']
            ff_len = len(ff[0])
            for i, idd in enumerate(fea['pair'][index+"id"]):
                ind = [c for c, j in enumerate(ids) if j==idd]
                if ind == []:
                    fea['pair']['fea'][i] += [0]*ff_len
                    emptycount += 1
                else: # only one element in ind indeed.
                    fea['pair']['fea'][i] += ff[ind[0]] # concat to pair feature
            logging.debug("the empty count of %s feature is %d", index, emptycount)
        logging.debug("the length of final feature is %d", len(fea['pair']['fea'][0]))
         
        return fea['pair'] 
         
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
        self.initfeaturecal()
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
        timelist = self.conf.get(self.sectionname,self.field+"data.time").split(',')
        period = self.caltimeperiod(timelist)
        self.period = period
        savename = self.conf.get(self.sectionname,self.field+"data.savename")
        self.savename = savename
        # global parameters: feature types
        self.savefolder = self.conf.get(self.sectionname, "savefolder")
        self.featureconfname = self.conf.get(self.sectionname, "confname")
        self.featurenames = self.conf.get(self.sectionname, "featurenames").split(",")
        self.featurelist = {}
        for name in self.featurenames:
            self.featurelist[name] = self.conf.get(self.sectionname, name + ".list").split(",")
    
    def process(self):
        fea = {}
        feaindex = []
        # user feature:
        # fea['user']['id']: [,,,]
        # fea['user']['fea']: [,,,]      
        if "user" in self.featurelist:
            fea['user'] = userfeatureextractor.extract(self)
            feaindex.append("user")
        # item feature: 
        # fea['item']['id']: [,,,]
        # fea['item']['fea']: [,,,]            
        if "item" in self.featurelist:
            fea['item'] = itemfeatureextractor.extract(self)
            feaindex.append("item")
        # pair feature: 
        # fea['pair']['userid']: [,,,]
        # fea['pair']['itemid']: [,,,]
        # fea['pair']['fea']: [,,,]          
        if "pair" in self.featurelist:       
            fea['pair'] = pairfeatureextractor.extract(self)
            
        combfeature = self.combine(fea, feaindex)
        if self.savename != "":
            #save 
            np.save(os.path.join(self.savefolder, self.savename), combfeature)
            # load
            # fea = np.load("name").all()
        
    def combine(self, fea, feaindex):
        if "pair" not in fea:
            logging.error("No pair feature calcualted")
            raise Exception('NO PAIR FEATURE ERROR!')
        #useridlist = fea['pair']['userid']
        #itemidlist = fea['pair']['itemid']
        if len(fea) == 1 and "pair" in fea:
            return fea["pair"]
        
        for index in feaindex:
            emptycount = 0
            f = fea[index]
            ids = f['id'] # elements in ids are unique to each other.
            ff = f['fea']
            ff_len = len(ff[0])
            for i, idd in enumerate(fea['pair'][index+"id"]):
                ind = [c for c, j in enumerate(ids) if j==idd]
                if ind == []:
                    fea['pair']['fea'][i] += [0]*ff_len
                    emptycount += 1
                else: # only one element in ind indeed.
                    fea['pair']['fea'][i] += ff[ind[0]] # concat to pair feature
            logging.debug("the empty count of %s feature is %d", index, emptycount)
         
        logging.debug("the length of final feature is %d", len(fea['pair']['fea'][0]))
         
        return fea['pair'] 
# field: train, val, test
# configfilename: used to initialize time period and feature type.
def calfeatures(field, configfilename):
    feacal  = FeatureExtractor(configfilename,'featurecal', field)
    features = feacal.process()
    return features
# combine the feature and label together.
def calcombine(field, configfilename):
    conf = ConfigParser()
    loadfolder = conf.get("label", "loadfolder")
    feafile = conf.get("label", field + ".feafile")
    #loda features from file
    features = np.load(os.path.join(loadfolder, feafile)).all()
    # load labels from file    
    labfile = conf.get("label", field + ".labfile")
    labels = np.load(os.path.join(loadfolder, labfile)).all()
    
def callabels(field, configfilename):
    labcal = LabelExtractor(configfilename, 'label', field)
    labels = labcal.process()
    return labels
# classification:
# feature: [[],[],[]]
# label: [,,]
def train(field, configfilename):
    pass
# evaluate the F-score on validation set
def evaluate(field, configfilename):
    pass
# submit the result of test data according to target item.
def submit(field, configfilename):
    pass
    
if __name__ == '__main__':
    LOG_LEVEL = logging.DEBUG
    logging.basicConfig(level=LOG_LEVEL,
                format="%(levelname)s:%(name)s:%(funcName)s->%(message)s",  #logging.BASIC_FORMAT,
                datefmt='%a, %d %b %Y %H:%M:%S')
    if len(sys.argv)>1 :
        func = getattr(sys.modules[__name__], sys.argv[1])
        func(*sys.argv[2:])
    else:
        print >> sys.stderr,'none'