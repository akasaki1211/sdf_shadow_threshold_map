@echo off

if "%~1"=="" exit

:: show version
echo Using version:
%~dp0ShadowThresholdMap.exe -v

:: run
%~dp0ShadowThresholdMap.exe -i %~1

::(example) add options.
::%~dp0ShadowThresholdMap.exe -i %~1 -b 16 -r -n "face_shadow_map" -c "rgba" -f "gaussian" -k 3

echo ===========================
echo Fin.
echo ===========================

pause