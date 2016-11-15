#@echo on

:: 变量设置
set project=OutOfServiceAlarmAction
set currentdir=%~dp0
set srcdir=%currentdir%src
set targetdir=%currentdir%target


:: 删除src pyc
for /R %srcdir% %%s in (*.pyc) do ( 
    del %%s
) 


:: 编译
python -m compileall .


:: 拷贝到target
rd /s /q %targetdir%
md %targetdir%\%project%
xcopy /s /e /i /y %srcdir% %targetdir%\%project%


:: 删除target py
for /R %targetdir%\%project% %%s in (*.py) do ( 
    del %%s
)


:: 压缩打包
python zipCompile.py "%targetdir%\%project%.zip" "%targetdir%\%project%"


pause
