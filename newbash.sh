#!/usr/bin/env bash

for var in {0..80..10}

do	
	echo $var
	/home/xavier/anaconda3/bin/python /home/xavier/Documents/development/gmin/gminExec.py --use_conf True --rwc_sup $(($var+20)) --rwc_inf $(($var))


done


exec /bin/bash
	

