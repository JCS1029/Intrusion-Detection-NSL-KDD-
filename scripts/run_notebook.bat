@echo off
cd /d "%~dp0.."
echo Starting Jupyter Notebook (project .venv)...
".venv\Scripts\jupyter.exe" notebook notebooks\ids_nsl_kdd_analysis.ipynb
