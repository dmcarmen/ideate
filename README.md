# IDEATE

**IDEATE** (physIcal 3D modElling to rAdiative Transfer intErface) is an interface that allows the output provided by [ShapeX](https://wsteffen75.wixsite.com/website) be used as an input model for the radiative transfer code [LIME](https://lime.readthedocs.io/en/latest/).


## How to use it

To run the program you need to install **ShapeX**, **LIME** and **IDEATE**. Follow the instructions in [Installation](#installation). Once installed to run the GUI you need to execute the `ideate.py` file, for example running from the main folder `python src/ideate.py`.

For the analytics functions on the interface you can use all the expressions appearing on [py-expression-eval library](https://pypi.org/project/py-expression-eval/) (strings appearing on **Available operators, constants and functions**).

## Installation

### ShapeX

Latest ShapeX version can be downloaded from its [web](https://wsteffen75.wixsite.com/website/downloads).

### LIME

You can follow the full installation steps in [LIME's GitHub](https://github.com/lime-rt/lime). This program uses **pylime**. This module uses Python 2, so there should be also a Python2 version in the computer. For the rest of the process this module will be prepared along with **IDEATE** installation. 

### IDEATE

Before installing make sure you are using Python 3. You can check your Python version by running `python -V`. This version was tested on Python 3.7.9.

If the command pylime already exists and the Python packages are already installed this step is **not necessary**.

Else, by running `./install.sh [-l <lime_path>] [-m <mol_path>] [-p]` you can install **IDEATE** and prepare **pylime**. The script can take zero to three arguments:
- `-l <lime_path>`: optional, complete path to where **LIME** is installed (written without trailing '/'). By default, it will try to find where pylime command is.
- `-m <mol_path>`: optional, complete path to where to save the molecules information (written without trailing '/'). If not specified, it will be saved in `~/.ideate/mols`.
- `-p`: optional, if provided, required Python packages will be installed. Required Python packages appear on `ideate_requirements.txt`.
