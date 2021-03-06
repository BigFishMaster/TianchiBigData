import logging
import sys
from ConfigParser import ConfigParser
import numpy as np
# use sklearn to classify something.
import sklearn 
import cPickle
import os
#from userfeatureextractor import UFE
#from itemfeatureextractor import IFE
from pairfeatureextractor import PFE
import labelextractor
from timemapper import timemapper

class LabelExtractor(object):
    def __init__(self, configurefile, prefix, field):
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
            raise Exception('time list length ERROR')
        period = []
        for i in range(len(timelist)/2):
            t1, t2 = timelist[2*i: 2*i + 2]
            period.append([timemapper[t1],timemapper[t2]])
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
        #labels: dict i.e. {"userid,itemid":label}
        # key:userid, itemid
        # value: label
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
    def __init__(self, configurefile, prefix, field ):
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
        self.inputname = self.conf.get(self.sectionname, "inputname")
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
            ufe = UFE(self)
            fea['user'] = ufe.extract()
            feaindex.append("user")
        # item feature: 
        # fea['item']['id']: [,,,]
        # fea['item']['fea']: [,,,]            
        if "item" in self.featurelist:
            ife = IFE(self)
            fea['item'] = ife.extract()
            feaindex.append("item")
        # pair feature: 
        # fea['pair']['userid']: [,,,]
        # fea['pair']['itemid']: [,,,]
        # fea['pair']['fea']: [,,,]          
        if "pair" in self.featurelist:   
            pfe = PFE(self)
            fea['pair'] = pfe.extract()
            
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
    loadfolder = conf.get("combine", "loadfolder")
    #loda features from file
    feafile = conf.get("combine", field + ".feafile")
    features = np.load(os.path.join(loadfolder, feafile)).all()
    # load labels from file    
    labfile = conf.get("combine", field + ".labfile")
    labels = np.load(os.path.join(loadfolder, labfile)).all()
    #load savename 
    savename = conf.get("combine", field + ".savename")
    # positive ratio
    flag, ratio = conf.get("combine", "sample_flag").split(',')
    ratio = float(ratio)
    
    savefolder = conf.get("combine", "savefolder")
    
    pos_label_count = 0
    neg_label_count = 0
        
    labs = []
    for i in range(len(features["userid"])):
        userid = features["userid"][i]
        itemid = features["itemid"][i]
        key = userid + "," + itemid
        label = 0
        if key in labels:
            label = labels[key]
        labs.append(label)
        
        if label == 0:
            neg_label_count += 1
        else:
            pos_label_count += 1
    logging.debug("the positive and negative labels are %d:%d", \
                    pos_label_count, neg_label_count)
    logging.debug("the positive ratio is %f", \
                    pos_label_count*1.0/(neg_label_count + pos_label_count))
    
    features = np.array(features)
    labs = np.array(labs)
        
    if flag != "1" or field == "val":
        if savename != "":        
            np.save(os.path.join(savefolder, savename), [features, labs])
        return [features, labs]
    
    
    possample = pos_label_count
    negsample = int(possample/ratio-possample)
    
    posfea = features[labs==1]
    negfea = features[labs==0]
    features = []
    # random sample
    import random
    ind = range(0, len(negfea))
    random.shuffle(ind)
    np.save("randomed_index_for_negative_sampling.npy", ind)
    ind = ind[:negsample]
    negfea = negfea[ind]
    
    # never shuffle again ,does it need ???    
    features = posfea + negfea
    labs = [1]*len(posfea) + [0]*len(negfea)
    
    if savename != "":
        np.save(os.path.join(savefolder, savename), [features, labs])
    return [features, labs]
    
def callabels(field, configfilename):
    labcal = LabelExtractor(configfilename, 'label', field)
    labels = labcal.process()
    return labels
# classification:
# feature: [[],[],[]]
# label: [,,]
from sklearn.linear_model import LogisticRegression
def train(field, configfilename):
    loadfolder = conf.get("train", "loadfolder")
    savefolder = conf.get("train", "savefolder")    
    traindatafile = conf.get("train","traindatafile")
    modelname = conf.get("train","modelname")
        
    features, labels = np.load(os.path.join(loadfolder, traindatafile))
    clf_l2_LR = LogisticRegression(C=10, penalty='l2', tol=0.01)
    clf_l2_LR.fit(features, labels)
    if savename != "":
        np.save(os.path.join(savefolder, savename), clf_l2_LR)
    return clf_l2_LR
# evaluate the F-score on validation set
def evaluate(field, configfilename):
    disable_val = conf.get("train", "disable_val")
    if disable_val == "1":
            return
    loadmodelfolder = conf.get("train", "loadmodelfolder")
    modelname = conf.get("train", "modelname")
    loadfeaturefolder = conf.get("train", "loadfeaturefolder")
    featurefile = conf.get("train", "featurefile")
    labelfile = conf.get("train", "labelfile")
    
    model = np.load(os.path.join(loadmodelfolder, modelname))
    features = np.load(os.path.join(loadfeaturefolder, featurefile))
    labels = np.load(os.path.join(loadfeaturefolder, labelfile))
        
    #pred = clf.score(features, labels)  
    pred = clf.predict(features)
    #get F-score
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
