

print('------------------------------------------------------------------------')
print('---------------                                    ---------------------')
print('---------------            gminComputation         ---------------------')
print('---------------                  V1.0              ---------------------')
print('---------------                                    ---------------------')
print('------------------------------------------------------------------------')

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
                rwc_inf,
                fresh_weight,
                dry_weight):

        self.TIME_COL = time_col
        self.SAMPLE_ID = sample_id
        self.YVAR = yvar
        self.T = temp
        self.RH = rh
        self.PATM = patm
        self.AREA = area   

        self.FW = fresh_weight
        self.DW = dry_weight  

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
        self.firstchoice = 0
        while True:
            self.display_menu()
            if self.firstchoice == 0:
                choice = input("Enter an option: ")
            else:
                choice = '4'

            # redirection to the self.choices attribute in the __init__
            action = self.choices.get(choice)

            self.action_choice = choice

            if action:
                action()
            else:
                print("{0} is not a valid choice".format(choice))
                self.run()
            self.firstchoice += 1


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
                    os.makedirs(fig_folder+'/'+'gmin')
                    # os.makedirs(fig_folder+'/'+'diff')
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


    def _execute_computation(self):
        '''
        parse all the files within the folder tree       
        '''

        print('\nStarting Gmin computation\n')

        
        from .gmincomputation import gminComput

        print('\nchoices is {}\n'.format(self.action_choice ))

        self._create_saving_folder()

        dimfolder = len(self.listOfFiles)
        # li_all = []
        list_of_df = []
        global_score = []

        # print(self.listOfFiles)
        # time.sleep(2)

        for d in np.arange(0,dimfolder):
            print('\n\n\n---------------------------------------------------------------------')
            print(d)            
            
            try:
                self.presentfile=self.listOfFiles[d][0]
            except:
                self.presentfile = 'No file'            
            
            print('parsing list of files from : {}'.format(self.presentfile))

            if self.presentfile != 'No file':
                for elem in self.listOfFiles[d]:
                    dffile = self._robust_import(elem)
                    # remove the .csv extension from the name                    
                    temp_folder = os.path.splitext(str(os.path.basename(elem)))[0]  
                    # print('tf1: ', temp_folder)                 

                    for sample in dffile[self.SAMPLE_ID].unique():            
                        self.sample = sample
                        df = dffile.loc[dffile[self.SAMPLE_ID]==sample,:].copy().reset_index()
                        # Analysing
                        print('Analysing: {}'.format(sample))

                        # initialising gmin computation class
                        gmc = gminComput(self.TIME_COL,
                                        self.SAMPLE_ID,
                                        self.YVAR,
                                        self.T,
                                        self.RH,
                                        self.PATM,
                                        self.AREA,
                                        self.rwc_sup,
                                        self.rwc_inf, 
                                        self.action_choice,
                                        self.fig_folder,
                                        self.rep_name,
                                        self.FW,
                                        self.DW)
                        # computing time delta
                        df = gmc._compute_time_delta(df)

                        # computing RWC
                        if 1>0:#(self.action_choice == '2') | (self.action_choice == '3'):
                            print('Computing RWC')
                            if self.action_choice == '2':
                                df, t80, t50, rwc_sup, rwc_inf, method_of_dfw= gmc._compute_rwc(df)
                            else:
                                df, t80, t50, rwc_sup, rwc_inf, method_of_dfw = gmc._compute_rwc(df, visualise = False)
                            # self.t80 = t80
                            # self.t50 = t50
                        else:
                            t80 = None
                            t50 = None
                            rwc_sup = None
                            rwc_inf = None
                            method_of_dfw = None

                        # plotting gmin
                        gs, selected_points = gmc._plot_gmin(df,t80, t50)
                        if (self.action_choice == '1'):
                            t80 = np.max(selected_points[0][0],0)
                            t50 = selected_points[1][0]



                        gs.extend([rwc_sup, rwc_inf, t80, t50, method_of_dfw])
                        # print('gs: ', gs)

                        global_score.append(gs)   

                        temp_df = pd.DataFrame(global_score, columns = ['Sample_ID', 'Interval_time','slope', 'Rsquared', 'Gmin_mean', 'pack',\
                             'percentage_rwc_sup', 'percentage_rwc_inf', 'time_sup', 'time_inf', 'method_of_rwc'])
                        temp_df2 = pd.DataFrame(temp_df["pack"].to_list(), columns=['K', 'VPD', 'mean_T', 'mean_RH', 'mean_Patm', 'mean_area'])
                        temp_df = temp_df.drop(columns='pack')
                        temp_df = pd.concat([temp_df,temp_df2], axis = 1)

                        # print('tf2: ', temp_folder) 
                        temp_df['Campaign'] = temp_folder

                        temp_df = temp_df.drop(columns='Interval_time')
                        temp_df = temp_df[['Campaign','Sample_ID', 'Gmin_mean', 'percentage_rwc_sup', 'percentage_rwc_inf', 'time_sup', 'time_inf', 'method_of_rwc', \
                                            'slope', 'Rsquared', 'K', 'VPD', 'mean_T', 'mean_RH', 'mean_Patm', 'mean_area']]
                        

                        # PROBLEM HERE ##################
                        # temp_df['percentage_rwc_sup']=rwc_sup
                        # temp_df['percentage_rwc_inf']=rwc_inf

                        # temp_df['time_rwc_sup']=t80
                        # temp_df['time_rwc_inf']=t50
                        ################################

                        if (self.action_choice == '2') | (self.action_choice == '3'):
                            temp_df['Mode']='RWC filtered'                             
                        else:
                            temp_df['Mode']='Manual Selection'

                        print('\n')

                        # append df to list
                        list_of_df.append(temp_df)
                        # print(pd.concat(list_of_df))
                        # global_score = []
                        pd.concat(list_of_df).reset_index().drop_duplicates(subset=['Campaign','index','Sample_ID','slope']).drop(columns='index').to_csv(self.rep_name+'/GMIN_df_complete.csv', index = False)
                        # time.sleep(1)
                        # print('saved !')
                    global_score = []
            else:
                pass

        # save the appended df in a global file
        # explode remove the square bracket [] from cells and convert to multiline
        # pd.concat(list_of_df).reset_index().explode('Interval_time').to_csv(self.rep_name+'/RMSE_df_complete_full.csv')
        # pd.concat(list_of_df).reset_index().explode('Interval_time').to_csv(self.rep_name+'/RMSE_df_complete_full.csv')
        # pd.concat(list_of_df).reset_index().explode('Interval_time').drop_duplicates(subset=['Campaign','index','Sample_ID','slope']).to_csv(self.rep_name+'/RMSE_df_complete_full_No_duplicates.csv')
        pd.concat(list_of_df).reset_index().drop_duplicates(subset=['Campaign','index','Sample_ID','slope']).drop(columns='index').to_csv(self.rep_name+'/GMIN_df_complete.csv', index = False)

        

                        
