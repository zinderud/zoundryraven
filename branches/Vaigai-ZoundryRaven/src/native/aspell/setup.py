from distutils.core import setup, Extension

import os
import sys
import shutil

outputFile = os.path.join(os.getcwd(), "build", "lib." + sys.platform + "-2.4", "aspell.pyd")
finalOutputFile = os.path.join(os.getcwd(), "..", "..", "python", "zoundry", "appframework", "services", "spellcheck", "aspell", "aspell.pyd")

module1 = Extension('aspell', 
    libraries = ['aspell-15'], 
    library_dirs = ['./aspell-dev/lib'], 
    include_dirs = ['./aspell-dev/include'], 
    sources = ['aspell.c'])

setup (name = 'GNU Aspell wrapper',
	version = '1.0',
	ext_modules = [module1])

print ("\n\nBuild successful - copying native library to src/python/zoundry/appframework/services/spellcheck/aspell/aspell.pyd")
shutil.copyfile(outputFile, finalOutputFile)
print ("Done")
    