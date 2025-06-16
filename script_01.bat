@echo off
setlocal enabledelayedexpansion

REM Check if list.txt exists
if not exist list.txt (
    echo Error: The file list.txt does not exist.
    exit /b 1
)

REM Read each line from list.txt
for /f "usebackq tokens=*" %%A in ("list.txt") do (
    set "filter_value=%%A"

    REM Skip empty lines
    if not "!filter_value!"=="" (
        echo Running the Python script with filter_value: !filter_value!

        REM Run the Python script with the current filter_value
        python app.py --filter_value "!filter_value!"
        
        REM Check the exit status
        if errorlevel 1 (
            echo Error while running Python script with filter_value: !filter_value!
        )
    )
)

endlocal
