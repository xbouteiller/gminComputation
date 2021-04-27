

print('------------------------------------------------------------------------')
print('---------------                                    ---------------------')
print('---------------            gminComputation         ---------------------')
print('---------------                  V0.1              ---------------------')
print('---------------                                    ---------------------')
print('------------------------------------------------------------------------')

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



time.sleep(0.5)
colors = dict(mcolors.BASE_COLORS, **mcolors.CSS4_COLORS)





class ParseFile():
    import pandas as pd
    import numpy as np
    import re       

    def __init__(self, path, skipr=1, sepa=',', encod = "utf-8"):
        '''
        initialization
        path of the file
        skipfoot : number of rows to skip at the end of the txt file

        portability : allow manual definition of skiprows and delimiter
                    test the file format and provide the good function for reading the file
        '''

        try:
            self.file = pd.read_csv(path,sep=sepa, skiprows=skipr)
        except:
            self.file = pd.read_csv(path, skiprows=skipr, sep=sepa, encoding=encod)
    

    def clean_file(self):
        '''
        clean the file

        Currently do nothing but can be adapted in order to clean file individually
        '''        
        return self.file





class ParseTreeFolder(): 
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


    def __init__(self,                
                time_col, 
                sample_id,
                yvar,
                temp,
                rh,
                patm,
                area,               
                rwc_sup,
                rwc_inf):

        self.TIME_COL = time_col
        self.SAMPLE_ID = sample_id
        self.YVAR = yvar
        self.T = temp
        self.RH = rh
        self.PATM = patm
        self.AREA = area     

        self.rwc_sup = rwc_sup
        self.rwc_inf = rwc_inf

        # global class variables
        self.global_score = []        


        print('''
        WELCOME TO GMIN COMPUTATION

        What do you want to do ?

        1: Parse all files from a folder
        2: Select some ID from a file        
        ''')
        self.file_or_folder = self._get_valid_input('What do you want to do ? Choose one of : ', ('1','2'))

        # fixed value for self.file_or_folder attribute, to be cleaned in the future
    
        # self.file_or_folder = self._get_valid_input('Type 1 to start : ', ('1'))
        if self.file_or_folder== '1':
            root_path = os.getcwd()
            Tk().withdraw()
            folder = askdirectory(title = 'What is the root folder that you want to parse ?',
                                initialdir = root_path)            
            self.path = folder
            print('\n\nroot path is {}'.format(self.path))
            
        if self.file_or_folder== '2':
            Tk().withdraw()
            file = askopenfilename(title='What is the file that you want to check ?')
            self.path = file.replace('/','/')
            print('\n\nfile path is {}'.format(self.path)) 
            print('\n')


        # options allowed for the action method    
        self.choices = {
        "1": self._execute_computation,
        "2": self._execute_computation,
        "3": self._execute_computation,
        "4": self._quit
        # "4": self.erase,
        # "5": self.extract_strings_and_nums
        }       
    

    def _listdir_fullpath(self, p, s):
        '''
        method for creating a list of csv file
        '''

        d=os.path.join(p, s)
        return [os.path.join(d, f) for f in os.listdir(d) if f.endswith('.csv')]

    
    def parse_folder(self):
        '''
        parse the folder tree and store the full path to target file in a list
        '''

        if self.file_or_folder=='2':
            self.listOfFiles=[[self.path]]


        if self.file_or_folder=='1':
            file_root=[]
            self.listOfFiles = []

            # method with csv detection            
            try:
                # basedir
                file_root = [os.path.join(self.path, f) for f in os.listdir(self.path) if f.endswith('.csv')]
                self.listOfFiles.append(file_root)
                #print(file_root)
            except:
                print('no file detected within root directory')
                pass

            try:
                #subfolders
                for pa, subdirs, files in os.walk(self.path):
                    for s in subdirs:
                        self.listOfFiles.append(self._listdir_fullpath(p=pa, s=s))
            except:
                print('no file detected within childs directory')
                pass       

            print('\n')
            try:
                [print("-found : {0} matching files in folder {1}".format(len(i),j)) for i,j in zip(self.listOfFiles, range(1,len(self.listOfFiles)+1))]
                print('\n')
            except:
                print('no files detected at all')
                print('\n')
                pass

            time.sleep(1)

            return self.listOfFiles


    def display_menu(self):
        print("""
        --------------------
        -----   MENU   -----
        --------------------

        List of actions

        1. Select points on curve
        2. Compute gmin between RWC boundaries (semi auto)
        3. Compute gmin between RWC boundaries (full auto)
        4. Exit


        """)
    
    def run(self):
        '''Display the menu and respond to choices.'''
        
        while True:
            self.display_menu()
            choice = input("Enter an option: ")

            # redirection to the self.choices attribute in the __init__
            action = self.choices.get(choice)

            if action:
                action()
            else:
                print("{0} is not a valid choice".format(choice))
                self.run()


    def _quit(self):
        print("Thank you for using your gminComputation today.\n")
        sys.exit(0)


    def _evaluate_file(self, elem, skip):
        try:
            dffile = ParseFile(path = elem, skipr=skip).clean_file()
        except:
            encodi='latin'
            dffile = ParseFile(path = elem, skipr=skip, encod=encodi).clean_file()
            
        if dffile.shape[1] == 1:                
            separ=';'
            try:
                dffile = ParseFile(path = elem, sepa=separ, skipr=skip).clean_file()
            except:
                encodi='latin'
                dffile = ParseFile(path = elem, skipr=skip, sepa=separ, encod=encodi).clean_file()

        return dffile


    def _robust_import(self, elem):

        '''
        try to open a csv file using several methods
        should be relatively robust
        future : robustness could be improved

        use parsefile class        
        '''

        skip = 0
        if self.file_or_folder == '2': 
            dffile = self._evaluate_file(elem = elem, skip = skip)        
        

            uniqueid = dffile[self.SAMPLE_ID].unique()
            print('''
            Unique ID within selected file are: 
            {}
                        
            '''.format(uniqueid))
            
            listodidtoanalyse = []   
            count = 0
            idtoanalyse = ''
            while True:
                while ((idtoanalyse not in uniqueid) and (idtoanalyse not in ['exit', 'e'])):
                    idtoanalyse = input("\nwhich ID do you want to analyse ?\nPlease select one among:\n{}\nEnter --exit-- to stop\n\nYour choice: ".format(uniqueid))
            
                if  idtoanalyse in uniqueid:
                    print(' \nAppending : {}'.format(idtoanalyse))
                    listodidtoanalyse.append(idtoanalyse)
                    count += 1
                    idtoanalyse = ''
                        
                elif (idtoanalyse == 'exit' or idtoanalyse == 'e'):
                    if count>0:
                        print(' \nExiting')
                        break
                    else:
                        print('\nYou need to choose at least one ID before')
                        idtoanalyse = ''            
                
            
            boollistofid = [True if id in listodidtoanalyse else False for id in dffile[self.SAMPLE_ID] ]
            dffile = dffile[boollistofid].copy()
            print('\nselected ID are: {}'.format(dffile[self.SAMPLE_ID].unique()))                        

        if self.file_or_folder == '1':            
            dffile = self._evaluate_file(elem = elem, skip = skip) 

        return dffile
        

    def _create_saving_folder(self):
        try:
            self.fig_folder
        except:
            self.fig_folder = 'None'

        if self.fig_folder == 'None':
            starting_name = 'output_fig'
            i = 0
            while True:
                i+=1
                fig_folder = starting_name+'_'+str(i)
                if not os.path.exists(fig_folder):
                    os.makedirs(fig_folder)
                    os.makedirs(fig_folder+'/'+'rmse')
                    os.makedirs(fig_folder+'/'+'diff')
                    os.makedirs(fig_folder+'/'+'rwc')
                    break
            self.fig_folder = fig_folder 

        try:
            temp_name = self.rep_name                
        except:
            self.rep_name = 'None'
        
        if self.rep_name == 'None':
            starting_name = 'output_files'
            i = 0
            while True:
                i+=1
                temp_name = starting_name+'_'+str(i)
                if not os.path.exists(temp_name):
                    os.makedirs(temp_name)
                    break
            self.rep_name = temp_name





    # def _parse_samples(self, dffile): 
    #     '''
    #     for each file, each unique ID will be analyzed
    #     using a FUNC
        
    #     this function will ask if we want to work on raw or smoothed data
    #     '''



    #     # for each file, slice each unique ID
    #     for sample in dffile[self.SAMPLE_ID].unique():            
    #         self.sample = sample
    #         df = dffile.loc[dffile[self.SAMPLE_ID]==sample,:].copy().reset_index()
    #         return df
    
            # # transform time to TRUE date time
            # try:
            #     df['delta_time']
            # except:
            #     print('delta time column is leaking ... computing ...')
            #     df['TIME_COL2'] = pd.to_datetime(df[self.TIME_COL] , infer_datetime_format=True)  
            #     # compute time delta between measures
            #     # WARNING : the points need to be regurlarly sampled with a constant frequency
            #     df['delta_time'] = (df['TIME_COL2']-df['TIME_COL2'][0])   
            #     # convert time to minute
            #     df['delta_time'] = df['delta_time'].dt.total_seconds() / 60 # minutes 

            # ################# PUT HERE THE RWC METHOD
            # df, t80, t50 = self._compute_rwc(df)
            # self.t80 = t80
            # self.t50 = t50
            # #########################################

            # self.Xselected = df['delta_time'].values
            # self.yselected = df[self.YVAR].copy().values
            # #print(FRAC_P)
            # #print(DELTA_MULTI)
            # self.Ysmooth = self._smoother(self.Xselected , self.yselected, fr = FRAC_P, delta_multi = DELTA_MULTI)

            # df['raw_data'] = df[self.YVAR].copy()
            # df['smooth_data'] = self.Ysmooth.copy()
            # df['Work_on_smooth'] = 'No'

            # if not self.Conductance or self.Conductance:  
            #     # strange code : but always ask for smoothing
            #     # future : can be modified (either always allow smoothing and self.conductance is not useful or smoothinf is forbiden for robust differential)
            #     plt.plot(self.Xselected, self.yselected, linestyle='-', marker='.', label = 'raw data')
            #     plt.plot(self.Xselected, self.Ysmooth, linestyle='-', marker='.', label = 'smooth')
            #     plt.title(self.sample)
            #     plt.ylabel(self.sample)
            #     plt.legend()    
            #     # plt.pause(PAUSE_GRAPH/10)
            #     plt.waitforbuttonpress(0)
            #     # input()
            #     plt.close() 

            
            #     print('''
            #     Do you want to work on smoothed data ?

            #     1: Yes
            #     2: Yes, But I want to adjust smoothing parameters
            #     3: No            
            #     ''') 

            #     what_to_do = self._get_valid_input('What do you want to do ? Choose one of : ', ('1','2','3'))
            #     ########################################################################
            #     if what_to_do=='1':
            #         df[self.YVAR] = self.Ysmooth.copy()
            #         df['Work_on_smooth'] = 'yes'
            #     if what_to_do=='2':
            #         while True:          
            #             while True:
                            
            #                 try:
            #                     _FRAC=0.1
            #                     FRAC_P2 = float(input('What is the frac value ? (current value : {}) '.format(_FRAC)) or _FRAC)
            #                     _FRAC = FRAC_P2
            #                     break
            #                 except ValueError:
            #                     print("Oops!  That was no valid number.  Try again...")                    
            #             while True:

            #                 try:
            #                     _DELTA_MULTI=0.01
            #                     DELTA_MULTI2= float(input('What is the delta value ? (current value : {}) '.format(_DELTA_MULTI)) or _DELTA_MULTI)
            #                     _DELTA_MULTI = DELTA_MULTI2
            #                     break
            #                 except ValueError:
            #                     print("Oops!  That was no valid number.  Try again...")

            #             self.Ysmooth = self._smoother(self.Xselected , self.yselected, fr = FRAC_P2, delta_multi = DELTA_MULTI2)
            #             plt.plot(self.Xselected, self.yselected, linestyle='-', marker='.', label = 'raw data')
            #             plt.plot(self.Xselected, self.Ysmooth, linestyle='-', marker='.', label = 'smooth')
            #             plt.legend()    
            #             # plt.pause(PAUSE_GRAPH/10)
            #             plt.waitforbuttonpress(0)
            #             # input()
            #             plt.close()   
            #             print('''
            #             Do you want to keep this values?

            #             1: Yes
            #             2: No            
            #             ''')
            #             what_to_do = self._get_valid_input('What do you want to do ? Choose one of : ', ('1','2'))
            #             if what_to_do == '1':
            #                 break
            #             if what_to_do == '2':
            #                 pass
                    
            #         df[self.YVAR] = self.Ysmooth.copy()
            #         df['Work_on_smooth'] = 'yes'
        
            # FUNC(df)


    def _execute_computation(self):
        '''
        parse all the files within the folder tree       
        '''

        print('\n Starting Gmin computation\n')

        
        from .gmincomputation import gminComput

        print('\nchoices is {}\n'.format(self.choices))

        self._create_saving_folder()

        dimfolder = len(self.listOfFiles)
        li_all = []

        for d in np.arange(0,dimfolder):
            print('\n\n\n---------------------------------------------------------------------')
            print(d)            
            li = []
            try:
                self.presentfile=self.listOfFiles[d][0]
            except:
                self.presentfile = 'No file'
            
            self.df_rmse = None
            self.df_value = None
            print('parsing list of files from : {}'.format(self.presentfile))
            

            list_of_df = []
            if self.presentfile != 'No file':
                for elem in self.listOfFiles[d]:
                    dffile = self._robust_import(elem) 

                    print(dffile.head())
                    print(dffile.shape)

                    for sample in dffile[self.SAMPLE_ID].unique():            
                        self.sample = sample
                        df = dffile.loc[dffile[self.SAMPLE_ID]==sample,:].copy().reset_index()

                        gmc = gminComput(self)

                        gmc._compute_time_delta(df)

                
                    
            #         # fit after rwc removal, if you want to use the full curve set tinf to 0 and tsup to 100
            #         # dffile, t80, t50 = self._compute_rwc(dffile)
                    
            #         # future : do i need to use global var as self.globalscore ... ?
            #         self._parse_samples(dffile = dffile, FUNC = self._change_det)
            #         temp_df = pd.DataFrame(self.global_score, columns = ['Sample_ID', 'Change_points','slope', 'Rsquared', 'Gmin_mean', 'pack'])
            #         temp_df2 = pd.DataFrame(temp_df["pack"].to_list(), columns=['K', 'VPD', 'mean_T', 'mean_RH', 'mean_Patm', 'mean_area'])
            #         temp_df = temp_df.drop(columns='pack')
                    
            #         # remove the .csv extension from the name
            #         temp_folder = os.path.splitext(str(os.path.basename(elem)))[0]

            #         if not os.path.exists(temp_name + temp_folder ):
            #             os.makedirs(temp_name + temp_folder)
            #         # concat df
            #         temp_df = pd.concat([temp_df,temp_df2], axis = 1)
            #         temp_df['Campaign'] = temp_folder

            #         # NEW ##
            #         temp_df['fit_mode'] = self.fit_exp_rmse
            #         temp_df['transfo_mode'] = self.transfo_rmse

            #         temp_df['percentage_rwc_sup']=self.rwc_sup
            #         temp_df['percentage_rwc_inf']=self.rwc_inf

            #         temp_df['time_rwc_sup']=self.t80
            #         temp_df['time_rwc_inf']=self.t50

            #         # append df to list
            #         list_of_df.append(temp_df)
            #         temp_df.to_csv(temp_name + temp_folder + '/RMSE_detection_' + str(os.path.basename(elem))) 
            #         #pd.concat([temp_df,temp_df2], axis = 1).to_csv('output_files/'+ temp_folder + '/RMSE_detection_' + str(os.path.basename(elem)))                 
                                        
            #         self.df_rmse.to_csv(temp_name+ temp_folder + '/RMSE_score_'+str(os.path.basename(elem)))
            #         self.df_value.to_csv(temp_name+ temp_folder + '/RMSE_df_complete_'+str(os.path.basename(elem)))
            #         self.df_rmse = None
            #         self.df_value = None
            #         self.global_score = []

            # # save the appended df in a global file
            # # explode remove the square bracket [] from cells and convert to multiline
            # pd.concat(list_of_df).reset_index().explode('Change_points').to_csv(temp_name+'RMSE_df_complete_full.csv')
            # pd.concat(list_of_df).reset_index().explode('Change_points').drop_duplicates(subset=['Campaign','index','Sample_ID','slope']).to_csv(temp_name+'RMSE_df_complete_full_No_duplicates.csv')
                
    