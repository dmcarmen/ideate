# IDEATE

**IDEATE** (phyIcal 3D modElling to rAdiative Transfer intErface) is an interface that allows the output provided by [ShapeX](https://wsteffen75.wixsite.com/website) be used as an input model for the radiative transfer code [LIME](https://lime.readthedocs.io/en/latest/).


## How to use it

To run the program you need to install **ShapeX**, **LIME** and **IDEATE** itself . Follow the instructions in [Installation](#installation). Once installed to run the GUI you need to execute the `ideate.py` file, for example running from the main folder `python src/ideate.py`.

## Installation

### ShapeX

Latest ShapeX version can be downloaded from its [web](https://wsteffen75.wixsite.com/website/downloads).

### LIME

You can follow the full installation steps in [LIME's GitHub](https://github.com/lime-rt/lime). This program uses **pylime**, but this module will be prepared along with **IDEATE** installation.

### IDEATE

Python 3.7.9 (or higher) required. You can check your Python version by running `python -V`. 

By running `./install.sh` you can install **IDEATE** and prepare **pylime**.
Required Python packages appear on `ideate_requirements.txt` and will be installed when running the script.
