# ardac-etl
ARDaC ETL workflows for DCC data release version 2.0.0.

# Installation
The python workflow is implemented and tested with python 3.13.2.  Furthermore, the NextFlow workflow scripts
utilize Anaconda Python virtual environments.  Anaconda is chosen over the Python built-in virtual environment
manager because NextFlow has a strong preference for using Anaconda virtual environments.

If Anaconda is not already installed on your system, the small-scale Anaconda environment manager called
_miniconda_ can be installed easily using the following [installation instructions](https://www.anaconda.com/docs/getting-started/miniconda/install#macos-linux-installation)

The Anaconda base installation should be availble in your shell's search path after installation.  Open a new
terminal window so that you are using the updated environment.

To show your current search path:
```
echo $PATH
```

The path should contain the installtion location of Anaconda.  If not, you should seek help installing Anaconda
from from your system administrator.

The next task is to create the virtual environment using Anaconda.

## Create the virtual environment
- If `base` environment is not activated, do `conda activate base`. If you are in another virtual environment, then deactivate it first.
- `cd /path/to/ardac-etl/python`
- `conda env create -p ../venv -f conda.yml` creates a virtual environment at `/path/to/project/ardac-etl/venv` with packages and python installed accoridng to `conda.yml` 

The created Python virtual environment at `/path/to/project/ardac-etl/venv` should be used for development of the
ardac-etl project and used with the NextFlow workflow.  If you are using VSCode as your IDE, you should set the
following configuration fields in the VSCode settings accordingly:
```
Python: Venv Path = ./venv
Python: Conda Path = /path/to/your/conda/bin/conda
```

You may also need to set `Python: Locator = js` if the IDE cycles indefinitely on `Reactivating Terminals`.

## Installing NextFlow
Follow the instructions [here](https://www.nextflow.io/docs/latest/install.html) to install NextFlow

## Executing the ARDaC mapper workflow
The NextFlow workflow to generate the ARDaC nodes from the observational and clinical data sets is performed by the `run_observational_workflow.bash` and `run_clinical_workflow.bash` scripts in the `nextflow` subdirectory.  These scripts can be run directly in that same subdirectory.  A hidden log file `.nextflow.log` will be generated describing the run and any problems that may have occurred.

