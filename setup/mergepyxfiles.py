# Merges many .pyx files from the upper directory into one big .pyx file.

mainfile = "cefpython.pyx"

import os
import glob

pyxfiles = glob.glob("../*.pyx")
pyxfiles = [file for file in pyxfiles if file.find(mainfile) == -1]
pyxfiles.insert(0, ".."+os.sep+mainfile)

if os.path.exists("setup"):
	print "Wrong directory, we should be inside setup!"
	exit()

# Remove old file.
if os.path.exists(mainfile):
	os.remove(mainfile)

content = ""
for file in pyxfiles:
	with open(file, "r") as file:
		content += file.read()+"\n\n"

with open(mainfile, "w") as file:
	file.write(content)

print "Merged files: %s into one big file: %s" % (pyxfiles, mainfile)
