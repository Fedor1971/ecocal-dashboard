# EcoCal Dashboard

Local Streamlit app for browsing/filtering the world economic calendar via the
[`ecocal`](https://github.com/lcsrodriguez/ecocal) package.

## Setup

```powershell
python -m venv .venv
.venv\Scripts\pip install -r requirements.txt
.venv\Scripts\pip install ecocal==1.2.1 --no-deps
```

`ecocal` is installed separately with `--no-deps`: its package metadata pins
`pandas==2.1.4` exactly, which has no prebuilt wheel for Python 3.13+ and
needs a C/Fortran compiler to build from source. Its actual code only uses
standard, version-stable pandas APIs (`read_csv`, `DataFrame`, `merge`), so a
modern pandas (installed via `requirements.txt` above) works fine.

## Run

```powershell
.venv\Scripts\streamlit run app.py
```
