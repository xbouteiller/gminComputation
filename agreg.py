import pandas as pd
import os

# just modify this line
path = '/home/xavier/Documents/development/gmin'

####################################################################################################
listOfFiles = []

def _listdir_fullpath(p, s):
        '''
        method for creating a list of csv file
        '''

        d=os.path.join(p, s)
        return [os.path.join(d, f) for f in os.listdir(d) if f == 'GMIN_df_complete.csv']


for pa, subdirs, files in os.walk(path):
    for s in subdirs:
        listOfFiles.extend(_listdir_fullpath(p=pa, s=s))

#print(listOfFiles)


df = pd.read_csv(listOfFiles[0])

for i in range(len(listOfFiles)):
    dftemp = pd.read_csv(listOfFiles[i])
    df = pd.concat([df, dftemp])

df['meantime'] = (df.time_sup + df.time_inf) / 2

df.to_csv('agregatedGmin.csv')
###############################################################################################
import matplotlib.pyplot as plt
import seaborn as sns

sns.lineplot(data=df, x="meantime", y="Gmin_mean", hue="Sample_ID")
plt.show()