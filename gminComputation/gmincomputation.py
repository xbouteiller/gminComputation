
import numpy as np
import matplotlib.pyplot as plt
from scipy import signal
from loess.loess_1d import loess_1d
from statsmodels.nonparametric.smoothers_lowess import lowess
import pandas as pd
import time
import sys
from scipy import stats
import os
from matplotlib import colors as mcolors
import re
import time  
from tkinter import Tk
from tkinter.filedialog import askopenfilename, askdirectory

from .gmininit import ParseTreeFolder





class gminComput(ParseTreeFolder):

    def __init__(self,
                TIME_COL, 
                SAMPLE_ID,
                YVAR,
                T,
                RH, 
                PATM,
                AREA,
                rwc_sup, 
                rwc_inf, 
                choices):
        super().__init__(TIME_COL, 
                        SAMPLE_ID,
                        YVAR,
                        T,
                        RH, 
                        PATM,
                        AREA,
                        rwc_sup, 
                        rwc_inf,
                        choices)  

    def _compute_time_delta(self, df):
        # transform time to TRUE date time
        try:
            df['delta_time']
        except:
            print('delta time column is leaking ... computing ...')
            df['TIME_COL2'] = pd.to_datetime(df[self.TIME_COL] , infer_datetime_format=True)  
            # compute time delta between measures
            # WARNING : the points need to be regurlarly sampled with a constant frequency
            df['delta_time'] = (df['TIME_COL2']-df['TIME_COL2'][0])   
            # convert time to minute
            df['delta_time'] = df['delta_time'].dt.total_seconds() / 60 # minutes 

        print(df.head())

        return df

    
    def _compute_rwc():
        pass
    
    def _plot_gmin():
        pass

    def _compute_gmin():
        pass

    


