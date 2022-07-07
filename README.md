# IDEATE

**IDEATE** (physIcal 3D modElling to rAdiative Transfer intErface) is an interface that allows the output provided by [ShapeX](https://wsteffen75.wixsite.com/website) be used as an input model for the radiative transfer code [LIME](https://lime.readthedocs.io/en/latest/).

**IDEATE** is publicly available, but if you use it for your work, please use the following acknowledgement:

"IDEATE has been developed at the Centro de Astrobiologia (CAB,
CSIC-INTA, Spain) and is part of the I+D+i project PID2019-105203GB-C22
funded by the Spanish MCIN/AEI/10.13039/501100011033."


## Table of contents
- [How to use it](#how-to-use-it)
  * [Input and output](#input-and-output)
    + [Input file](#input-file)
    + [Output file](#output-file)
  * [Available analytic functions](#available-analytic-functions)
- [Installation](#installation)
  * [ShapeX](#shapex)
  * [LIME](#lime)
  * [IDEATE](#ideate)
- [Source code organization and basic logic](#source-code-organization-and-basic-logic)
- [Aknowledgements](#aknowledgements)

## How to use it

To run the program you need to install **ShapeX**, **LIME** and **IDEATE**. Follow the instructions in [Installation](#installation). Once installed to run the GUI you need to execute the `ideate.py` file, for example running from the main folder `python src/ideate.py`.

### Input and output

#### Input file

ShapeX output `.txt` tabulated data file follows this format:

| Object, Species | Px      | Py      | Pz      | Density | Vx      | Vy      | Vz      | Temperature | Turbulence |
|-----------------|---------|---------|---------|---------|---------|---------|---------|-------------|---|
| \<str>, \<str>    | \<float> | \<float> | \<float> | \<float> | \<float> | \<float> | \<float> | \<float>     | \<float> |


**Turbulence** is not an option in ShapeX, but it can be added (for example using `pandas`) manually to the file. Columns **Px**, **Py** and **Pz** are compulsory. The rest are optional and can be chosen from *Initial Configuration* > *Variables read from the file*. File's path must be specified with *Initial configuration* > *Open your shape model file*.
  
#### Output file

Its path and name can be chosen in *General parameters* > *Output location* and it will be a `.fits` file created by LIME.

### Available analytic functions

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

## Source code organization and basic logic

inside `src/` we can find the following files:

- `lime_model.py`: model LIME needs for its execution. By default, it will be copied to `~/.ideate/` at the beginning of IDEATE's execution and it will be called when clicking *Start!*. When cllicking than button, IDEATE will also save `lime_config.ini` file, containing all parameters specified by the user and required by pylime and `lime_model.py` model to work. If modifying the model is required, it can be changed manually and after that running `pylime lime_model.py` (and it must be in the same folder as `lime_config.ini`)
- `View.py`: all functions related to what tou can **see** on the interface. If there is an user action in the interface or it needs certain data, it will send a petition to the *Controller*.
- `Model.py`: this class will contain the functions to save and read the parameters and the power to execute LIME. It works managing, writing and reading, configuration files (see [configparser](https://docs.python.org/3/library/configparser.html) to learn how they work). These files save data needed for LIME's execution, and when clicking *Start!*, `lime_config.ini` will automatically be created in  `~/.ideate/` and another `.bak` file (with the same data, and the name and path of the output `.fits` file chosen) for possible later access. Besides, a `.bak` can be saved when clicking *Save parameters*, and you can recover those parameters on the interface clicking *Load parameters*.
- `Controller.py`: it connects *View* and *Model*, sending data between them.
- `utils.py`: auxiliar functions for *View* and *Model*.

Funtions and classes are documented on the source code.

## Acknowledgements

"IDEATE has been developed at the Centro de Astrobiologia (CAB,
CSIC-INTA, Spain). C. Diez Menendez acknowledges a JAE-Intro fellowship
from the Consejo Superior de Investigaciones Científicas (CSIC) -- Reference
JAEINT_21_02510 --- under the supervision of C. Sánchez Contreras (CAB,
CSIC-INTA). This work is part of the I+D+i project PID2019-105203GB-C22
funded by the Spanish MCIN/AEI/10.13039/501100011033."

