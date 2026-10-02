# EcoCal Dashboard

Styled in the Euronext house style (same palette/font as euronext-holidays; `style.py`).

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

## For colleagues: one-click start (Windows)

Needs **Python 3.11+** and, at run time, internet access to the FXStreet calendar API
(`calendar-api.fxstreet.com`). No admin rights, no PowerShell.

1. Unzip the release folder anywhere.
2. Double-click **`run.bat`** (first start ~1 minute; it builds a private `.venv`).
3. Browser opens at http://localhost:8501. Keep the black window open; close it to stop.

The offline zip contains a `wheels` folder, so no PyPI access is needed. The app listens on
`localhost` only. Setup failed halfway? Delete `.venv` and rerun.

### Maintainer: build a release

```powershell
.\.venv\Scripts\python.exe tools/make_release.py --python 3.13 --python 3.11   # offline zip -> dist/
.\.venv\Scripts\python.exe tools/make_release.py --no-wheels                    # small online zip
```

Wheels are tied to the recipient's Python version (`python --version`) and Windows x64.
`ecocal` is installed with `--no-deps` by `run.bat` (see Setup above for why).
