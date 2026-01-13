@echo off
title T212 Poročanje davkov - Zaganjalnik
echo ======================================================
echo    Trading 212 Tax Hub - Avtomatska priprava
echo ======================================================
echo.

echo [1/2] Preverjanje in posodabljanje potrebnih knjiznic...
echo ------------------------------------------------------
python -m pip install --upgrade pip --quiet
pip install streamlit pandas requests --upgrade --quiet

echo.
echo [2/2] Zaganjam aplikacijo...
echo ------------------------------------------------------
streamlit run app.py

echo.
echo Aplikacija je bila ustavljena.
pause