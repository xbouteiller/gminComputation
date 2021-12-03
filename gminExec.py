#!/home/xavier/anaconda3/bin/python
# python Leaf_exec.py -tr 4 -fr 2 -td 2 -fd 2 
# python Leaf_exec.py --transfo_rmse 4 --fit_rmse 2 --transfo_diff 2 --fit_diff 2 
# import matplotlib
# matplotlib.use("Qt5agg")

def float_range(mini,maxi):
    """Return function handle of an argument type function for 
       ArgumentParser checking a float range: mini <= arg <= maxi
         mini - maximum acceptable argument
         maxi - maximum acceptable argument"""

    # Define the function with default arguments
    def float_range_checker(arg):
        """New Type function for argparse - a float within predefined range."""

        try:
            f = float(arg)
        except ValueError:    
            raise argparse.ArgumentTypeError("must be a floating point number")
        if f < mini or f > maxi:
            raise argparse.ArgumentTypeError("must be in range [" + str(mini) + " .. " + str(maxi)+"]")
        return f

    # Return function handle to checking function
    return float_range_checker


if __name__=="__main__":

    #%% Dependencies
    import os
    import argparse
    from gminComputation.gmininit import ParseFile, ParseTreeFolder


    # Parser for defining parameters values using the shell
    # default  values can be modified directly HERE in the script or using the shell command line prompt
    parser = argparse.ArgumentParser()
    
    parser.add_argument('-tc','--time_col', default='date_time', 
                        help='which time col', 
                        type = str)

    parser.add_argument('-sid','--sample_id', default='sample_ID', 
                        help='which sample id col', 
                        type = str)

    parser.add_argument('-y','--yvar', default='weight_g', 
                        help='which Y col', 
                        type = str)
                        
    parser.add_argument('-t','--temp', default='T_C', 
                        help='which temp col', 
                        type = str)

    parser.add_argument('-rh','--rh', default='RH', 
                        help='which RH col', 
                        type = str)

    parser.add_argument('-fw','--fresh_weight', default='Fresh_weight', 
                        help='which fresh weight col', 
                        type = str)

    parser.add_argument('-dw','--dry_weight', default='Dry_weight', 
                        help='which dry weight col', 
                        type = str)       
                        
    parser.add_argument('-p','--patm', default='Patm', 
                        help='which P col', 
                        type = str)

    parser.add_argument('-a','--area', default='Area_m2', 
                        help='which area col', 
                        type = str)    

    parser.add_argument('-rs','--rwc_sup', default=80, 
                        help='upper percentage boundary of RWC [0 .. 100]',                         
                        type=float_range(0,100))
    
    parser.add_argument('-ri','--rwc_inf', default=50, 
                        help='lower percentage boundary of RWC [0 .. 100]',                         
                        type=float_range(0,100))
    
    parser.add_argument('-sm','--screen_move', default=800, 
                        help='parameter for avoidinf figure and terminal overlapping',                         
                        type=float_range(0,10000))

    parser.add_argument('-uc','--use_conf', default='False', 
                        help='use conf file ?',
                        choices=['True', 'False'],                         
                        type=str)


    args = parser.parse_args()
    
    time_col = args.time_col
    sample_id = args.sample_id
    yvar = args.yvar
    temp = args.temp
    rh = args.rh
    patm = args.patm
    area = args.area

    rwc_inf = args.rwc_inf
    rwc_sup = args.rwc_sup

    fresh_weight = args.fresh_weight
    dry_weight =  args.dry_weight

    screen_move = args.screen_move

    use_conf = args.use_conf

    # assert rwc_inf+rwc_sup < 100, 'sum of rwc boundaries should be < 100'
    assert rwc_inf < rwc_sup, 'rwc boundary inf should be < to rwc boundary sup'

    print('\n')
    print('Parametrizable parameters are :')
    print('--------------------------------\n')

    for arg in vars(args):
        print(arg,' : ', getattr(args, arg))
    
    print('\n')


    parse_folder = ParseTreeFolder(time_col = time_col,
                                   sample_id = sample_id,
                                   yvar = yvar,
                                   temp = temp,
                                   rh = rh,
                                   patm = patm,
                                   area = area,                                 
                                   rwc_inf = rwc_inf,
                                   rwc_sup = rwc_sup,
                                   fresh_weight = fresh_weight,
                                   dry_weight = dry_weight,
                                   screen_move = screen_move,
                                   use_conf = use_conf
                                  )

    parse_folder.parse_folder()    
    parse_folder.run()

