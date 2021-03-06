# Python Program for computing leaf conductance


Current version is: **1.5**

<img src="img/B17_LITU_BL_11.png" width="75%" height="75%">

**NEW: you can now provide dry and fresh weight in the data frame to compute RWC: see sections program flow step3 and data format below**

## How to install?

### Install Python version if needed

[Anaconda](https://www.anaconda.com/products/individual)

[Miniconda](https://docs.conda.io/en/latest/miniconda.html)


### Download full folder from git

1. Direct download

From the green box  named 'clone' in the right corner > download .zip

2. From the terminal

>
> git clone https://github.com/xbouteiller/gminComputation.git
>


### Install dependencies


>
> pip install -r requirements.txt 
>

### Install package

Open a terminal in the DetectEvent folder, then :

>
> python setup.py install
>


### Program Execution

Copy the file **gminExec.py** in the desired folder

Then open a terminal 


>
> python gminExec.py
>



I also provided some additonal for simplifying execution in the **exec** folder

if you are on a windows platform:

- create a shorcut for the *launch.bat* file
- place the shortcut in an ampty folder and double click on it
- the program will be executed in the terminal and files & figures will be saved in the empy folder


if you are on a linux platform:

1. in the *bash-ex-linux.sh* file
    - replace the path */home/xavier/anaconda3/bin/python* with the path linking to your python version 
    - if you use anaconda you should have to replace only *xavier* with you user name
    - replace the path */home/xavier/Documents/development/gmin/gminExec.py* with the correct path linking to the *gminExec.py* file
2. in the *launch-linux.desktop*
    - replace the path */home/xavier/Documents/development/gmin/exec/bash-ex-linux.sh* with the correct path to *bash-ex-linux.sh*
    - you can now copy the *launch-linux.desktop* file in a new folder and double click on it



### Installing updates

>
> git pull origin main
>
> python setup.py install
>

<br> </br>

## Program flow


#### Step 1
1. The program ask to chose:
    - A folder that will be parsed 
    - Some unique ID from a single file
<img src="img/Screenshot from 2021-04-28 15-38-37.png" width="75%" height="75%">

The program writes the number of files found
<img src="img/Screenshot from 2021-04-28 15-39-10.png" width="75%" height="12%">

#### Step 2
2. You have to chose which method you will use:
    - Select time interval manually then compute gmin in the interval time
    - Filtering the data based on RWC and then compute gmin in the interval time
<img src="img/Screenshot from 2021-04-28 15-39-13.png" width="75%" height="120%">

#### Step 3 - Option 1
3. If you chose the manual points selection:
    - You have to select two points on the curve
    - Gmin is computed based on a linear regression between these two points
<img src="img/B17_LITU_BL_11.png" width="75%" height="75%">


#### Step 3 - Option 2
4. If you chose the method based on RWC:
    - the semi auto method will plot curve each time
    - the full auto will precede to the gmin computation automatically


5. The data are first filtered based on RWC:
<img src="img/VIAL12.png" width="75%" height="75%">

Default values for the RWC filtering are 80% and 50%, but thsi can be changed manually:
>
> python gminExec.py --rwc_sup 90 --rwc_inf 20 # Superior threshold : 90%, inferior : 20%  
> 
> python gminExec.py -rs 90 -ri 20 # It is a shortcut for the code above
>

6. **New** if the columns Dry_weight and Fresh_weight are provided, he software use the provided values to compute RWC    


7. Gmin is computed based on a linear regression between the two boundaries of the RWC filtered data
<img src="img/VIAL12 g.png" width="75%" height="75%">

#### Step 5
8. Synthetic figures and data frames are saved within the output_fig and output_files folder

<br> </br>

## Data format

Data must be stored within files
For a better files recognition, first row of the csv file should contain the string "conductance" otherwise all csv from a folder will be parsed

Columns should be named as follows:


#### Quantitative columns

- weight_g : leaf weight as a function of time (g)
- T_C : temperature (??C)
- RH : Relative Humidity
- Patm : atmospheric pressure (KPa)
- Area_m2 : area of the leaf (m2)
- Fresh_weight : fresh (saturated) weight of the leaf (g)
- Dry_weight : dry weight of the leaf (g)

#### Qualitative columns

- campaign : campaign name
- sample_ID : ID of the sample, should be unique for each sample

#### Date

- date_time : time **(best with the format YEAR/MONTH/DAY HOUR:MINUTE )**

<br> </br>

