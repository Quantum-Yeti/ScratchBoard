@echo off
SETLOCAL ENABLEDELAYEDEXPANSION

:: Set your GitHub repository details
SET GITHUB_USER=quantum-yeti
SET GITHUB_REPO=https://github.com/Quantum-Yeti/ScratchBoard
SET EXE_NAME=ScratchBoard.exe

:: Get the latest release info from GitHub API
echo Fetching the latest release info from GitHub...
for /f "delims=" %%i in ('curl -s https://api.github.com/repos/%GITHUB_USER%/%GITHUB_REPO%/releases/latest ^| findstr "browser_download_url"') do (
    set DOWNLOAD_URL=%%i
)

:: Extract the URL for the exe file (assuming your .exe is in the release assets)
for /f "tokens=2 delims=:" %%a in ("!DOWNLOAD_URL!") do (
    set EXE_URL=%%a
)

:: Remove any extra spaces or quotes
set EXE_URL=%EXE_URL:~1,-1%

:: Download the latest .exe file
echo Downloading the latest release...
curl -L -o "%EXE_NAME%" "%EXE_URL%"

:: Check if the download was successful
IF NOT EXIST "%EXE_NAME%" (
    echo Failed to download the .exe file. Exiting.
    exit /b 1
)

:: Stop the application (if running)
echo Stopping the existing application...
taskkill /f /im "%EXE_NAME%"

:: Replace the old .exe with the new one
echo Replacing the old .exe with the latest version...
move /y "%EXE_NAME%" "%~dp0%EXE_NAME%"

:: Start the new .exe
echo Starting the new version of the application...
start "" "%~dp0%EXE_NAME%"

echo Done!
