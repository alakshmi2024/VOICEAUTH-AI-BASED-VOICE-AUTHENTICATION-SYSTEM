@echo off
echo Activating Virtual Environment...
call venv\Scripts\activate

echo Starting VoiceAuth Application...
python app.py

pause