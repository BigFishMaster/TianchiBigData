# -*- coding: utf-8 -*-

class PFE(object):
    def __int__(self, params):
        period = params['user'].period
        featurelist = params['user'].featurelist
        inputname = params['user'].inputname
        #click,buy,store,cart,avgtime2deadline
        feafunc = {}
        feafunc[''] = 
    
        #fea 1: the distribute of click,buy,store,cart in :
        # time : last friday, weekends, Mon. to Tues: 3 types
        # dim : 4-dim distribution
        # input : metadata: {[userid],[itemid], [behavior]}

    def clickbuystorecart( metadata ):
        
    def extract(params):

        metadata = preprocess( inputname )
        for key in metadata:
            mdata = metadata[key]
            mfea = []
            for name in featurelist:
                if name in feafunc:
                    f = feafunc[name]()

    # formulate data to metadate 
    # denoise
    # input original data
    def preprocess( file ):
        list = open(file, 'r').readlines()
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