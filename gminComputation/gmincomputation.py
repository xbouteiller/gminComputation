
import numpy as np
import matplotlib.pyplot as plt
# from scipy import signal
# from loess.loess_1d import loess_1d
# from statsmodels.nonparametric.smoothers_lowess import lowess
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



colors = dict(mcolors.BASE_COLORS, **mcolors.CSS4_COLORS)

class gminComput(ParseTreeFolder):

    def __init__(self,
                time_col, 
                sample_id,
                yvar,
                temp,
                rh,
                patm,
                area,               
                rwc_sup,
                rwc_inf,
                choice,
                figfolder,
                repfolder):
        self.TIME_COL = time_col
        self.SAMPLE_ID = sample_id
        self.YVAR = yvar
        self.T = temp
        self.RH = rh
        self.PATM = patm
        self.AREA = area     

        self.rwc_sup = rwc_sup
        self.rwc_inf = rwc_inf 

        self.action_choice = choice

        self.fig_folder = figfolder
        self.rep_name = repfolder
    
    def _get_valid_input(self, input_string, valid_options):
            '''
            useful function in order to ask input value and assess that the answer is allowed

            input_string : question
            valid_options : authorized answers
            '''
            input_string += "({}) ".format(", ".join(valid_options))
            response = input(input_string)
            while response.lower() not in valid_options:
                response = input(input_string)
            return response

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

        # print(df.head())

        return df

    
    def _compute_rwc(self, df, nmean = 20,  visualise = True):           

        from matplotlib.patches import Circle, Wedge, Polygon

        rwc_thressup = self.rwc_sup
        rwc_thresinf = self.rwc_inf

        dry = np.mean(df[self.YVAR].values[-int(nmean):])
        saturated = np.mean(df[self.YVAR].values[0:nmean])## or np.max() ??
        rwc = 100*((df[self.YVAR].values-dry)/(saturated-dry))            

        def find_nearest(a, a0):
            "Element in nd array `a` closest to the scalar value `a0`"
            idx = np.abs(a - a0).argmin()
            
            return a.flat[idx]  

        rwc_sup = find_nearest(rwc, rwc_thressup)
        rwc_inf = find_nearest(rwc, rwc_thresinf)  

        # print('RWC boundary: [{}% .. {}%]'.format(np.round(rwc_sup,2), np.round(rwc_inf,2)))
        

        try:
            df['delta_time']
        except:
            def compute_time_lag(df):
                df['TIME_COL2'] = pd.to_datetime(df[self.TIME_COL] , infer_datetime_format=True)  
                # compute time delta between measures
                # WARNING : the points need to be regurlarly sampled with a constant frequency
                df['delta_time'] = (df['TIME_COL2']-df['TIME_COL2'][0])   
                # convert time to minute
                df['delta_time'] = df['delta_time'].dt.total_seconds() / 60 # minutes 

                return df
            
            df = compute_time_lag(df)

        # print(df.head(10))
        # print(df.tail(10))


        t80 = np.min(df.loc[rwc == rwc_sup, "delta_time"].values)
        t50 = np.max(df.loc[rwc == rwc_inf, "delta_time"].values)

        print('Detected RWC SUP {}% at {:.2f} min'.format(rwc_thressup,t80))
        print('Detected RWC INF {}% at {:.2f} min'.format(rwc_thresinf,t50))
        

        if t80>=t50:
            print('Warning, time at {}%: {} min, should be less than than time at {}%: {} min'.format(rwc_thressup,t80, rwc_thresinf,t50))
            print('keeping full data set')

            t80 = df['delta_time'].values[0]
            t50 = df['delta_time'].values[-1]

            rwc_sup = 100
            rwc_inf = 0

            print('New: Detected RWC SUP 0% at {:.2f} min'.format(t80))
            print('New: Detected RWC INF 100% at {:.2f} min'.format(t50))
        

        TITLE = str(df[self.SAMPLE_ID].unique()[0])            
            
        fig, ax1 = plt.subplots()

        plt.title(TITLE)
        color = 'tab:blue'
        ax1.set_xlabel('time (min)')
        ax1.set_ylabel(TITLE + '\nWeight (g)', color=color)
        ax1.plot(df['delta_time'], df[self.YVAR], color=color, linestyle='-', marker='.', label = 'data', alpha = 0.5)
        ax1.tick_params(axis='y', labelcolor=color)
        ax1.set_ylim([0.9*np.min(df[self.YVAR]), 1.1*np.max(df[self.YVAR])])        

        verts = [[0, 0],[t80, 0], [t80, 1.1*np.max(df[self.YVAR].values)] , [0, 1.1*np.max(df[self.YVAR].values)]]
        poly = Polygon(verts, facecolor='r', alpha = 0.5)
        ax1.add_patch(poly)   

        verts = [[t50, 0],[np.max(df['delta_time'].values), 0], [np.max(df['delta_time'].values), 1.1*np.max(df[self.YVAR].values)], [t50, 1.1*np.max(df[self.YVAR].values)] ]
        poly = Polygon(verts, facecolor='r', alpha = 0.5)
        ax1.add_patch(poly)

        ax2 = ax1.twinx()  # instantiate a second axes that shares the same x-axis
        color = 'tab:green' 
        ax2.set_ylabel('RWC (%)', color=color)  # we already handled the x-label with ax1
        ax2.plot(df['delta_time'],  rwc, color=color, marker='.', label = 'RWC', alpha = 0.5)
        ax2.tick_params(axis='y', labelcolor=color) 

        # Make the shaded region
        figname = self.fig_folder + '/' + 'rwc' + '/' + TITLE + '.png'
        plt.savefig(figname, dpi = 420, bbox_inches = 'tight')
        # plt.pause(PAUSE_GRAPH)
        #plt.show()
        if visualise:
            # plt.show()
            plt.waitforbuttonpress(0)
            # input()
        plt.close() 

        print('Slicing df between RWC80 and RWC50')
        # df = df[(rwc < rwc_thressup) & (rwc > rwc_thresinf)].copy()
        df = df[ (df.delta_time.values <= t50) & (df.delta_time.values >= t80)].copy()

        # print('t min : {} min'.format(df.delta_time.min().round(3)))
        # print('t max : {} min'.format(df.delta_time.max().round(3)))

        print('t min : {} min'.format(np.round(df.delta_time.min(), 3)))
        print('t max : {} min'.format(np.round(df.delta_time.max(), 3)))

        return df, t80, t50, rwc_sup, rwc_inf
    

    def _plot_gmin(self, df):
        '''
        detection of the crossing point of the rmse error from the exp & linear fitting
        yexp & ylin : rmse from the sliding window
        '''
        gmin_mean=''
        list_of_param=['', '', '', '', '', '']      
        selected_points=''
       
        # plot the figure of the detected crossing sections  
        #  
        TITLE = str(df[self.SAMPLE_ID].unique()[0])            
            
        fig, ax1 = plt.subplots()

        plt.title(TITLE)
        color = 'tab:blue'
        ax1.set_xlabel('time (min)')
        ax1.set_ylabel(TITLE + '\nWeight (g)', color=color)
        ax1.plot(df['delta_time'], df[self.YVAR], color=color, linestyle='-', marker='.', label = 'data', alpha = 0.5)
        ax1.tick_params(axis='y', labelcolor=color)
        ax1.set_ylim([0.9*np.min(df[self.YVAR]), 1.1*np.max(df[self.YVAR])])      
        
           
        if (self.action_choice =='1'):
            print('\nPlease select two points on the figure')
            # plt.waitforbuttonpress(0)
            while True: 
                selected_points = fig.ginput(2)
                slope, intercept, rsquared, fitted_values, Xreg = self._compute_slope(df,selected_points[0], True, selected_points[1])
                gmin_mean, list_of_param = self._compute_gmin(df=df, slope=slope, t1=selected_points[0][0], t2 = selected_points[1][0])
                ax1.plot(Xreg, fitted_values, c = 'black', lw = 2) 

                plt.show(block=False)
                plt.waitforbuttonpress(0)

                
                figname = self.fig_folder + '/' + 'gmin' + '/' + TITLE + '.png'
                plt.savefig(figname, dpi = 420, bbox_inches = 'tight')
                plt.close()  
                # input()
                print('''
                Do you want to try other values ?

                1: Yes
                2: No
                ''') 
                keepgoing = self._get_valid_input('Your choice', ('1', '2'))
                if (keepgoing == '1'):
                    TITLE = str(df[self.SAMPLE_ID].unique()[0])            
            
                    fig, ax1 = plt.subplots()

                    plt.title(TITLE)
                    color = 'tab:blue'
                    ax1.set_xlabel('time (min)')
                    ax1.set_ylabel(TITLE + '\nWeight (g)', color=color)
                    ax1.plot(df['delta_time'], df[self.YVAR], color=color, linestyle='-', marker='.', label = 'data', alpha = 0.5)
                    ax1.tick_params(axis='y', labelcolor=color)
                    ax1.set_ylim([0.9*np.min(df[self.YVAR]), 1.1*np.max(df[self.YVAR])])      
        
                else:
                    break


        else:
            Xidx = df['delta_time'].values[0]
            slope, intercept, rsquared, fitted_values, Xreg = self._compute_slope(df,Xidx1=Xidx)
            ax1.plot(Xreg, fitted_values, c = colors['black'], lw = 2)
            gmin_mean, list_of_param = self._compute_gmin(df=df, slope=slope, t1=Xidx, t2 = None)        
            
            # close the graph on a click
            # plt.pause(PAUSE_GRAPH)
            if (self.action_choice =='2'):
                plt.waitforbuttonpress(0)

            figname = self.fig_folder + '/' + 'gmin' + '/' + TITLE + '.png'
            plt.savefig(figname, dpi = 420, bbox_inches = 'tight')

            # input()
            plt.close()   

        
        if (self.action_choice =='1') :
            gs = [TITLE, [i[0] for i in selected_points ], slope, rsquared, gmin_mean, list_of_param]
        else:       
            gs = [TITLE, Xidx, slope, rsquared, gmin_mean, list_of_param]
        return gs, selected_points



    def _compute_gmin(self, df, slope, t1, t2 = None):
        '''
        compute gmin on a slice of a signal
        use the slope value
        '''
        if t2 is None:
            df = df[df['delta_time']>= t1].copy()
        if t2 is not None:            
            df = df[(df['delta_time']>= t1) & (df['delta_time']<= t2)].copy()

        k= (slope/18.01528)*(1000/60) #ici c'est en minutes (60*60*24)

        #Calcul VPD en kpa (Patm = 101.325 kPa)
        VPD =0.1*((6.13753*np.exp((17.966*np.mean(df[self.T].values)/(np.mean(df[self.T].values)+247.15)))) - (np.mean(df[self.RH].values)/100*(6.13753*np.exp((17.966*np.mean(df[self.T].values)/(np.mean(df[self.T].values)+247.15)))))) 

        #calcul gmin mmol.s
        gmin_ = -k * np.mean(df[self.PATM].values)/VPD

        #calcul gmin en mmol.m-2.s-1
        gmin = gmin_ / np.mean(df[self.AREA].values)

        print('gmin_mean: ', np.round(gmin, 3))

        return gmin, [k, VPD, np.mean(df[self.T].values), np.mean(df[self.RH].values), np.mean(df[self.PATM].values), np.mean(df[self.AREA].values)]

    def _compute_slope(self, df, Xidx1, interval = False, *args, **kwargs):
        '''
        fit a linear regression on a slice of a signal and return slope, intercept, rsqquared and fitted values
        '''         
        # this is useful for slicing X value returned by ginput
        # if len(Xidx1)>1:
        #     Xidx1 = Xidx1[0]  

        # print('Xidx1: ', Xidx1)     

        Xselected = df['delta_time'].values
        yselected = df[self.YVAR].values

        if interval: 
            Xidx1 = Xidx1[0]                      
            Xidx2 = args[0]
            if len(Xidx2)>1:
                Xidx2 = Xidx2[0]

            print('t min : {} min'.format(np.round(Xidx1,3)))
            print('t max : {} min'.format(np.round(Xidx2,3)))
            # print('Xidx1: ', Xidx1)
            # print('Xidx2: ', Xidx2)   
            X = Xselected[(Xselected >= Xidx1) & (Xselected <= Xidx2)].copy()
            y = yselected[(Xselected >= Xidx1) & (Xselected <= Xidx2)].copy()
        else:
            X = Xselected[Xselected >= Xidx1].copy()
            y = yselected[Xselected >= Xidx1].copy()

        try:
            slope, intercept, r_value, p_value, std_err = stats.linregress(X, y)
        except:
            print('Unable to fit regression')
            slope, intercept, r_value, p_value, std_err = 0, 0, 0, 0, 0

        fitted_values = slope*X + intercept
        rsquared = r_value**2

        return slope, intercept, rsquared, fitted_values, X

    


