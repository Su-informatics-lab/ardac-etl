# ardac-etl
ARDaC ETL workflows for DCC data release version 2.0.0.

# Installation
The python workflow is implemented and tested with python 3.13.2.  Make sure this version is installed and accessible by
your environment.

## Configuration of python virtual environment
1. Set the current directory to `ardac-etl` 
2. Create a new virtual environment:
```
python3 -m venv ./penv
```
3. Activate the new virtual environment:
```
source ./penv/bin/activate
```
4. Upgrade the `pip` installation:
```
python3 -m pip install --upgrade pip
```
5. Install needed python package dependencies:
```
python3 -m pip install -r requirements.txt
```
