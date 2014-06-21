from distutils.core import setup, Extension

import os
import sys
import shutil

PY24_HOME = u"C:/Tools/Python24"
VS_NET_HOME = u"C:/Program Files/Microsoft Visual Studio .NET 2003"
PY_WIN32_EXT_SRC_HOME = u"C:/Tools/pywin32-210"

# Generate the SDL include and lib paths
pythonIncludePath = PY24_HOME + "\\include"
win32IncludePath = PY24_HOME + "\\Lib\\site-packages\\win32\\include"
win32comIncludePath = PY24_HOME + "\\Lib\\site-packages\\win32com\include"
win32shellIncludePath = PY_WIN32_EXT_SRC_HOME + "\\com\\win32comext\\shell\\src"

win32LibPath = PY24_HOME + "\\Lib\\site-packages\\win32\\libs"
win32ComLibPath = PY24_HOME + "\\Lib\\site-packages\\win32com\\libs"
pythonLibPath = PY24_HOME + "\\libs"



# These should not be necessary!! For some reason, the Environment Variables
# INCLUDE= and LIB= are not working.
crtIncludePath = VS_NET_HOME + "\\VC7\\Include"
crtLibPath = VS_NET_HOME + "\\VC7\\Lib"

outputFile = os.path.join(os.getcwd(), "build", "lib." + sys.platform + "-2.4", "zravencom.pyd")
finalOutputFile = os.path.join(os.getcwd(), "..", "..", "python", "zoundry", "appframework", "util", "zravencom.pyd")

setup(name="zravencom", version="1.0", ext_modules=[
    Extension(
        "zravencom",
        ["ZRavenCom.cpp", "PyICustomDoc.cpp", "PyIDocHostUIHandler.cpp", "ZRavenMisc.cpp"],
        [pythonIncludePath, win32IncludePath, win32comIncludePath, crtIncludePath, win32shellIncludePath],
        None,
        None,
        [win32LibPath, win32ComLibPath, crtLibPath, pythonLibPath],
        ["WinInet", "User32", "Kernel32", "GDI32"]
        )
    ])

print ("\n\nBuild successful - copying native library to %s" % finalOutputFile)
shutil.copyfile(outputFile, finalOutputFile)
print ("Done")
