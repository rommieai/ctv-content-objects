@echo off
rem Lo lanza la tarea programada "CTV tanda PubMatic" (lunes y jueves): descarga el CSV de PubMatic,
rem corre la tanda completa, recarga BigQuery y hace commit y push. Todo queda en logs\programada.log;
rem si algo falla, abre ese log en el Bloc de notas para que se vea.
cd /d "%~dp0.."
if not exist logs mkdir logs
echo. >> logs\programada.log
echo ===== %date% %time% ===== >> logs\programada.log
python scripts\descargar_pubmatic.py --tanda --bigquery --commit --push >> logs\programada.log 2>&1
if errorlevel 1 (
    echo FALLO, ver arriba >> logs\programada.log
    start "" notepad logs\programada.log
    exit /b 1
)
