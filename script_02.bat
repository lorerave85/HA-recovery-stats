@echo off

REM Run the Python script using Python 3.11
python3.11 merge.py

REM Check the exit status
if errorlevel 1 (
    echo Error while running merge.py
)
