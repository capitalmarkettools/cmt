import os
import settings
from os.path import join

lineCount = 0 
print settings.ROOT_PATH
for root, dirs, fileNames in os.walk(settings.ROOT_PATH):
	for fileName in fileNames:
		if '.py' in fileName and not '.pyc' in fileName: 
			file = open(join(root,fileName))
			fileCount = 0
			for line in file:
				lineCount = lineCount + 1
				fileCount = fileCount + 1
			print str(fileCount) + '\t\t' + fileName
print 'Line counted equals %d' % lineCount
