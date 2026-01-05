@echo off
SETLOCAL ENABLEDELAYEDEXPANSION

:: GitHub repo info
SET GITHUB_USER=quantum-yeti
SET GITHUB_REPO=ScratchBoard
SET EXE_NAME=ScratchBoard.exe
SET TEMP_EXE=%TEMP%\%EXE_NAME%

:: Find running EXE location
echo Checking if %EXE_NAME% is running...
for /f "tokens=2 delims=," %%a in ('tasklist /fo csv /nh /fi "imagename eq %EXE_NAME%"') do (
    set EXE_PATH=%%~a
)

IF NOT DEFINED EXE_PATH (
    echo %EXE_NAME% is not currently running. You will need to specify where it is installed.
    pause
    exit /b 1
)

:: Remove quotes from CSV output
set EXE_PATH=%EXE_PATH:"=%

echo Found running EXE at: %EXE_PATH%

:: Stop the application
echo Stopping %EXE_NAME%...
taskkill /f /im "%EXE_NAME%" 2>nul

:: Fetch latest release URL
echo Fetching the latest release from GitHub...
for /f "delims=" %%i in ('curl -s https://api.github.com/repos/%GITHUB_USER%/%GITHUB_REPO%/releases/latest ^| findstr /i "browser_download_url"') do (
    set DOWNLOAD_URL=%%i
)

:: Only get URL ending with .exe
for /f "tokens=2 delims=:" %%a in ("!DOWNLOAD_URL!") do set EXE_URL=%%a
set EXE_URL=!EXE_URL:~2,-1!

echo Downloading latest release from: !EXE_URL!
curl -L -o "%TEMP_EXE%" "!EXE_URL!"

IF NOT EXIST "%TEMP_EXE%" (
    echo Failed to download the new EXE. Exiting.
    exit /b 1
)

:: Replace the old EXE
echo Replacing old EXE...
copy /y "%TEMP_EXE%" "%EXE_PATH%"

:: Start the updated EXE
echo Starting updated application...
start "" "%EXE_PATH%"

echo Done!
pause
