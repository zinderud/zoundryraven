echo off
set Path=C:\Tools\Python24;%Path%
set Path=C:\Program Files\Microsoft Visual C++ Toolkit 2003\bin;%Path%

set Include=%ProgramFiles%\Microsoft Platform SDK\Include;%Include%
set Include=%ProgramFiles%\Microsoft Visual C++ Toolkit 2003\include;%Include%

set Lib=%ProgramFiles%\Microsoft Platform SDK\Lib;%Lib%
set Lib=%ProgramFiles%\Microsoft Visual C++ Toolkit 2003\lib;%Lib%
set Lib=%ProgramFiles%\Microsoft Visual Studio .NET 2003\Vc7\lib;%xxLib%

cd \Development\eclipse-raven\workspace\Raven\src\native\aspell

C:\Tools\Python24\python setup.py build

pause
