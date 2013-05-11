import sys
import os
import glob
import shutil
import subprocess
import platform

BITS = platform.architecture()[0]
assert (BITS == "32bit" or BITS == "64bit")

PYVERSION = str(sys.version_info[0])+str(sys.version_info[1])
print("PYVERSION = %s" % PYVERSION)
print("BITS = %s" % BITS)

try:
	os.remove("./binaries_%s/cefpython_py%s.so" % (BITS, PYVERSION))
except OSError:
	pass

try:
	os.remove("./setup/cefpython_py%s.so" % PYVERSION)
except OSError:
	pass

pyx_files = glob.glob("./setup/*.pyx")
for f in pyx_files:
    os.remove(f)

try:
	shutil.rmtree("./setup/build")
except OSError:
	pass

os.chdir("./setup")

ret = subprocess.call(["python", "./fix_includes.py"])
if ret != 0:
	sys.exit("ERROR")

ret = subprocess.call(["python", "setup.py", "build_ext", "--inplace"])

os.chdir("../")

oldpyxfiles = glob.glob("./setup/*.pyx")
print("Removing old pyx files in /setup/: %s" % oldpyxfiles)
for pyxfile in oldpyxfiles:
    if os.path.exists(pyxfile):
       	os.remove(pyxfile)

if ret != 0:	
	sys.exit("ERROR")

os.rename("./setup/cefpython_py%s.so" % PYVERSION, "./binaries_%s/cefpython_py%s.so" % (BITS, PYVERSION))

shutil.copyfile("./../../cef1_api.py", "./binaries_%s/cefpython_py%s.py" % (BITS, PYVERSION))

print("DONE")

os.chdir("./binaries_%s" % BITS)
subprocess.call(["python", "./wxpython.py"])
