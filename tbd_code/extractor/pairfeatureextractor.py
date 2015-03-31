# -*- coding: utf-8 -*-
from timemapper import timemapper
from weekmapper import weekmapper
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

    def clickbuystorecart( mdata ): # 12-dim
        fea = np.zeros(12)           
        for item in mdata:
            behavior_type, user_geohash, item_category, day, hour = item
            if day not in weekmapper:
                continue
            specday = weekmapper[day]
            btype = float(behavior_type)
            if specday in [5]:
                fea[4*0+btype] += btype
            elif specday in [6, 7]:
                fea[4*1+btype] += btype
            elif specday in [1, 2, 3, 4]:
                fea[4*2+btype] += btype

        fea = fea/(np.sum(fea)+0.000001)
        return fea

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
        start_day = self.period[0]
        end_day = self.period[1]
        period_day = range(star_day, end_day+1)
        metadata = {}
        for i, item in enumerate(list):
            if i == 0: # skip the first line
                    continue
            tmp, hour = item.strip().split(" ")
            
            tmp_item = tmp.strip(',')
            if len(tmp_item) != 6:
                continue
            userid, itemid, behavior_type, user_geohash, item_category, day = tmp_item
            # FATAL day is not allowed            
            if day not in timemapper:
                continue
            current_day = timemapper[day]
            # day is limited by configuration
            if current_day not in period_day:
                continue
            key = userid + "," + itemid
            if key not in metadata:
                metadata[key] = []
                
            metadata[key].append([behavior_type, user_geohash, item_category, day, hour])
                
        return metadata