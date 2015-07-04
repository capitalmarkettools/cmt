import os
import sys

fileList = []
fileSize = 0
folderCount = 0
rootdir = sys.argv[1]

for root, subFolders, files in os.walk(rootdir):
    for file in files:
        if file.startswith("XYZ"):
			f = os.path.join(root,file)
			fnew = os.path.join(root,file[2:])
			os.rename(f, fnew)
#			print f
#			print fnew


#...    os.rename(filename, filename[7:])
#        fileSize = fileSize + os.path.getsize(f)
        #print(f)
 #       fileList.append(f)