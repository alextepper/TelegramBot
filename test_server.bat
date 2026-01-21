@echo off
echo Starting Flask server...
start cmd /k "cd /d %~dp0 && python app.py"
timeout /t 3 /nobreak
echo.
echo Testing the endpoint...
python test_endpoint.py
pause

