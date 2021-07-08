import os
import re
import shutil

# purt r"directorypath" within os.walk parameter.
path = [os.getcwd()]


for p in path:
	genobj = os.walk(p)#gives you a generator function with all directorys

	nfold=0
	for _, dirlist, _ in genobj:
		for i in dirlist: #checking if a folder called 1 exsists 
		    if re.search(r'output', i):
		    	shutil.rmtree(p+'/'+i)
		    	nfold+=1
		    	print('n of removed folder : {}'.format(nfold))

