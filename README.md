# LGApp
A web app that lets you pick and run tests via Labgrid's pytest plugin and generate HTML/PDF reports for test results.

## Features
- Pick a pytest file and run it with Labgrid
- View pytest HTML reports in the browser
- Download PDF versions

## Requirements
- Python 3.10+
- macOS/Linux (Not tested on Windows)

## Install
Open Terminal and run:
```bash
git clone https://github.com/danteppc/lgapp.git
cd lgapp
python3 -m venv .venv
source .venv/bin/activate
pip install -e .
```

## Run
Once installed, simply run:
```bash
lgapp
```
Then open http://localhost:8080

## Use
- Run tab: choose a `.py` test (defaults to `~/lgtest`, but you can browse anywhere)
- Tests run automatically; you'll be redirected to its report
- Reports tab: see all runs, view, download PDF, or delete

## Data & config locations
LGApp uses platform-appropriate user folders:
- Reports and DB are stored user data dir
- Labgrid environment config file: a default `lgconfig.yaml` is created in the user config dir on first run

## Screenshots

| Run Tests | Config Labgrid | Manage Reports |
| --- | --- | --- |
| ![Run page](imgs/1.png) | ![Config page](imgs/2.png) | ![Reports page](imgs/3.png) |
