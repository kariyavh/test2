@echo off
setlocal

set SCRIPT_DIR=%~dp0
cd /d %SCRIPT_DIR%

python -m pip install --upgrade pip
pip install -r requirements.txt pyinstaller

pyinstaller --noconfirm --clean ^
  --add-data "office_toolkit;office_toolkit" ^
  --name "OfficeEfficiencyToolkit" ^
  run_app.py

if exist OfficeEfficiencyToolkit-windows.zip del OfficeEfficiencyToolkit-windows.zip
powershell Compress-Archive -Path "dist/OfficeEfficiencyToolkit" -DestinationPath "OfficeEfficiencyToolkit-windows.zip" -Force

echo.
echo Build complete. The packaged application is located in dist\ or the ZIP archive in the project folder.
endlocal
