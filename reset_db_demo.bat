@echo off
cd /d "%~dp0"
py reset_db_demo.py
if errorlevel 1 exit /b %errorlevel%
