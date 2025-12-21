HOME_CONTENT = r"""

REM Open Chrome
if exist "%ProgramFiles%\Google\Chrome\Application\chrome.exe" (
    start "" "%ProgramFiles%\Google\Chrome\Application\chrome.exe" "chrome://newtab"
    exit /b
)

"""