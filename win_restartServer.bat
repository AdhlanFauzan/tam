@echo off
call ..\environment\scripts\activate.bat
set tamport=8000
IF EXIST win_startLocal.bat call win_settings.bat
start python manage.py runserver 127.0.0.1:%tamport% --nothreading
set tamport=
