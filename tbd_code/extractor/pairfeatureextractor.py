# -*- coding: utf-8 -*-
import timemapper
import weekmapper
class PFE(object):
    def __int__(self, params):
        self.period = params['user'].period
        self.featurelist = params['user'].featurelist
        self.featureconfname = params['user'].featureconfname
        self.inputname = params['user'].inputname
        self.feafunc = {}
        # initialize feafunc:
        self.feafunc['clickbuystorecart'] = self.clickbuystorecart
        
        #fea 1: the distribute of click,buy,store,cart in :
        # time : last friday, weekends, Mon. to Tues: 3 types
        # dim : 4-dim distribution
        # input : metadata: {[userid],[itemid], [behavior]}

    def clickbuystorecart( mdata ):
        
        
    def extract():
        metadata = self.preprocess()
        res = {}
        res['userid'] = []
        res['itemid'] = []
        res['fea'] = []
        for key in metadata:
            mdata = metadata[key]
            mfea = []
            for name in self.featurelist:
                if name in self.feafunc:
                    f = self.feafunc[name]( mdata )
                    mfea += f
            userid, itemid = key.split(',')
            res['userid'].append(userid)
            res['itemid'].append(itemid)
            res['fea'].append(mfea)
        
        return res
        
    # formulate data to metadate 
    # denoise
    # input original data
    def preprocess( ):
        list = open(self.inputname, 'r').readlines()
        metadata = {}
        for i, item in enumerate(list):
            if i == 0: # skip the first line
                    continue
            tmp, hour = item.strip().split(" ")
            userid, itemid, behavior_type, user_geohash, item_category, day = tmp.strip(',')
            key = userid + "," + itemid
            if key not in metadata:
                metadata[key] = []
                
            metadata[key].append([behavior_type, user_geohash, item_category, day, hour])
                
        return metadata