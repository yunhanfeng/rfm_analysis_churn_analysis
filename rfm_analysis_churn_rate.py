
### RFM Model and Chrun Rate

import pandas as pd
import numpy as np
from matplotlib import pyplot as plt
import datetime as dt

### Generate RFM Model
NOW = dt.datetime(2018,12,20)
rfmtable = df.groupby('UserID').agg({'DepatureTime':lambda x:(NOW-x.max()).days, \
                                        'UserID': lambda x:len(x), 'TotalSpent':lambda x:x.sum()})

rfmtable.rename(columns = {'DepatureTime':'recency', 'UserID':'frequency','TotalSpent':'monetary'}, inplace = True)

quantiles = rfmtable.quantile(q=[0.25, 0.5, 0.75])
quantiles = quantiles.to_dict()

def RScore(x,p,d):
    if x <= d[p][0.25]:
        return 1
    elif x <= d[p][0.50]:
        return 2
    elif x <= d[p][0.75]:
        return 3
    else:
        return 4

def FMScore(x,p,d):
    if x <= d[p][0.25]:
        return 4
    elif x <= d[p][0.50]:
        return 3
    elif x <= d[p][0.75]:
        return 2
    else:
        return 1

seg_rfmtable = rfmtable
seg_rfmtable['r_quartile'] = seg_rfmtable['recency'].apply(RScore, args = ('recency', quantiles,))
seg_rfmtable['f_quartile'] = seg_rfmtable['frequency'].apply(FMScore, args = ('frequency', quantiles,))
seg_rfmtable['m_quartile'] = seg_rfmtable['monetary'].apply(FMScore, args = ('monetary', quantiles,))

seg_rfmtable.reset_index(level = 0, inplace = True)

### combine data from shopping mall
catmap = {'LOW':1, 'MEDIUMLOW':2, 'MEDIEUMHIGH':3, 'HIGH':4 ,'VIP':5}
user = user.applymap(lambda s: catmap.get(s) if s in catmap else s)

single_user = user.groupby(['UserID']).aggregate({'spent_all':lambda x:x.sum(),'user_category':lambda x:round(x.median(),0)})
single_user.reset_index(level=0, inplace = True)

### Merge two data frame (seg_rfmtable & single_user)

final_metrics = pd.merge(seg_rfmtable, single_user, how='left', on = ['UserID'])

from scipy import stats
from sklearn.cluster import KMeans

cluster_data = final_metrics.dropna(subset=['spent_all'])
cols = ['recency', 'frequency','monetary','spent_all']
kmean_data = stats.zscore(cluster_data[cols])

km = KMeans(n_clusters = 5, random_state=0)

km.fit(kmean_data)

labels = km.labels_
cluster = labels.tolist()

final_cluster = pd.DataFrame(dict(cluster_label = cluster, UserId = cluster_data['UserID']))

verify_final = pd.merge(cluster_data, final_cluster, how = 'left', on = ['UserID'])

cols2 = ['recency', 'frequency','monetary','spent_all', 'cluster_label', 'user_category']
verify_final[cols2].groupby(['cluster_label']).agg({'recency':lambda x:x.mean(), \
                                                    'frequency':lambda x:x.mean(), \
                                                    'monetary':lambda x:x.mean(), \
                                                    'spent_all':lambda x:x.mean(), \
                                                    'user_category': lambda x:x.mode(), \
                                                    'cluster_label':'size'})

### Churn Rate (Based on the money spent in mall)

stay3 = df[df['Stay_days']>=3]
stay3 = stay3[stay3['Stay_days']<=10] 

userid_stay3 = list(stay3.UserID.unique())

user_stay3 = user[user['UserID'].isin(userid_stay3)]

user_stay_adt = user_stay3.sort_values(['UserID','Date'], ascending=[True, False])

user_stay_adt['Year'] = user_stay_adt['Date'].dt.year
user_stay_adt['Month'] = user_stay_adt['Date'].dt.month

user_stay_adt['n_day']=user_stay_adt.groupby(['UserID','Year','Month'])['Date'].rank(ascending=True,method='dense').astype(int)

user_stayday_adt = user_stay_adt.pivot_table(index=['UserID','Year','Month'], columns = 'n_day', values='spent_all')

longstay['2-1'] = (longstay[2]-longstay[1])/longstay[1]
longstay['3-2'] = (longstay[3]-longstay[2])/longstay[2]
longstay['4-3'] = (longstay[4]-longstay[3])/longstay[3]
longstay['5-4'] = (longstay[5]-longstay[4])/longstay[4]
longstay['6-5'] = (longstay[6]-longstay[5])/longstay[5]
longstay['7-6'] = (longstay[7]-longstay[6])/longstay[6]
longstay['8-7'] = (longstay[8]-longstay[7])/longstay[7]
longstay['9-8'] = (longstay[9]-longstay[8])/longstay[8]
longstay['10-9'] = (longstay[10]-longstay[9])/longstay[9]

def usercat(s):
    if s[1] <= 200:
        return 1
    elif s[1] <= 500:
        return 2
    elif s[1] <= 800:
        return 3
    elif s[1] < = 1000:
        return 4
    else:
        return 5
    
longstay['user_category'] = longstay.apply(usercat, axis = 1)

longstay_low = longstay[longstay['user_category']==1]
longstay_medlow = longstay[longstay['user_category']==2]
longstay_medhigh = longstay[longstay['user_category']==3]
longstay_high= longstay[longstay['user_category']==4]
longstay_vip = longstay[longstay['user_category']==5]

def day_decrease_portion(longstay):
    d2 = round(sum(longstay['2-1']<0)/len(longstay['2-1']),3)
    d3 = round(sum(longstay['3-2']<0)/len(longstay.dropna(subset=['3-2'])),3)
    d4 = round(sum(longstay['4-3']<0)/len(longstay.dropna(subset=['4-3'])),3)
    d5 = round(sum(longstay['5-4']<0)/len(longstay.dropna(subset=['5-4'])),3)
    d6 = round(sum(longstay['6-5']<0)/len(longstay.dropna(subset=['6-5'])),3)
    d7 = round(sum(longstay['7-6']<0)/len(longstay.dropna(subset=['7-6'])),3)
    d8 = round(sum(longstay['8-7']<0)/len(longstay.dropna(subset=['8-7'])),3)
    d9 = round(sum(longstay['9-8']<0)/len(longstay.dropna(subset=['9-8'])),3)
    d10 = round(sum(longstay['10-9']<0)/len(longstay.dropna(subset=['10-9'])),3)
    return (d2, d3, d4,d5,d6,d7,d8,d9,d10)

def day_decrease_rate(longstay):
    d2 = round(longstay[longstay['2-1']<0]['2-1'].mean(),3)
    d3 = round(longstay[longstay['3-2']<0]['3-2'].mean(),3)
    d4 = round(longstay[longstay['4-3']<0]['4-3'].mean(),3)
    d5 = round(longstay[longstay['5-4']<0]['5-4'].mean(),3)
    d6 = round(longstay[longstay['6-5']<0]['6-5'].mean(),3)
    d7 = round(longstay[longstay['7-6']<0]['7-6'].mean(),3)
    d8 = round(longstay[longstay['8-7']<0]['8-7'].mean(),3)
    d9 = round(longstay[longstay['9-8']<0]['9-8'].mean(),3)
    d10 = round(longstay[longstay['10-9']<0]['10-9'].mean(),3)
    return (d2, d3, d4,d5,d6,d7,d8,d9,d10)
