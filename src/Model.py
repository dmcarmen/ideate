import configparser
from pathlib import Path
from astroquery.lamda import Lamda
import subprocess as sub
from inspect import getsourcefile
from os.path import abspath, dirname
import warnings
import shutil

from utils import *


class Model:
    """Model class. Controls IDEATE's data and can call LIME.

    Raises:
        Exception: see in create_config function for more details.
    """

    ini_dir = Path.home()

    # Model data dictionaries.
    datos_vars = {}     # variables read or not from the file
    datos_pars = {}     # general parameters for LIME
    datos_mol = {}      # molecule information
    datos_img = {}      # image parameters for LIME
    datos_uds = {}      # units from functions/variables and several parameters
    datos_funcs = {}    # analytic functions
    datos_dust = {}     # dust data

    def __init__(self) -> None:
        """Creates Model and initiates LAMDA molecules dictionary.
        """
        # Reading ini configuration file to see where ideate model and LIME are located.
        # Also sees where LAMDA molecules files will be saved.
        ini_config = configparser.ConfigParser()

        cfile_path = Path(dirname(abspath(getsourcefile(lambda: 0))))
        ini_config.read(Path(cfile_path).parents[0] / "ideate_config.ini")

        if 'CONFIG' in ini_config:
            self.lime_path = Path(ini_config['CONFIG']['lime_path'])
            if 'mol_path' in ini_config['CONFIG']:
                self.mol_path = Path(ini_config['CONFIG']['mol_path'])
            else:
                self.mol_path = self.ini_dir / '.ideate_dust/mols/'
        else:  # if there is no ini config file (pylime is on the system)
            self.lime_path = None
            self.mol_path = self.ini_dir / '.ideate_dust/mols/'

        self.model_path = self.ini_dir / '.ideate_dust/'
        
        shutil.copyfile(cfile_path / "lime_model.py", self.model_path / "lime_model.py")
        Path(self.mol_path).mkdir(parents=True, exist_ok=True)

        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            self.mol_dic = Lamda.molecule_dict
        self.mol_load_flag = False

    def update_mol(self, mol):
        """Updates molecule dictionary information and returns its info. 

        Args:
            mol (str): molecule name.

        Returns:
            dict: dictionary with molecule information {'old_mol': old_mol, 'collrates': collrates, 'radtransitions': radtransitions, 'enlevels': enlevels}. If it is the same molecule as before returns None.
        """
        old_mol = ''
        if 'mol_name' in self.datos_mol and self.mol_load_flag is False:
            self.mol_load_flag = False
            old_mol = self.datos_mol['mol_name']

        if len(old_mol) == 0 or old_mol != mol:
            self.datos_mol['mol_name'] = mol
            print()
            print('Selected molecule: ', mol)
            print('Link: ', self.mol_dic[mol])

            collrates, radtransitions, enlevels = Lamda.query(mol=mol)
            print('Complete name: ' + enlevels.meta['molecule'])
            print('Weight: ' + str(enlevels.meta['molwt']))
            print('Number of enerfy levels: ' +
                  str(enlevels.meta['nenergylevels']))
            print('Transitions:')
            radtransitions.pprint_all()
            return {'old_mol': old_mol, 'collrates': collrates, 'radtransitions': radtransitions, 'enlevels': enlevels}

    def create_config(self, check_flag):
        """Creates a configuration file with all the dictionaries information.

        Args:
            check_flag (bool): if True, it will check all needed data is present. 

        Raises:
            Exception: specified on the function.

        Returns:
            config: configparser.ConfigParser object with all the data.
        """
        config = configparser.ConfigParser()

        config['VARS'] = self.datos_vars
        config['UDS'] = self.datos_uds
        config['FUNCS'] = self.datos_funcs

        if(self.datos_vars['density'] is False):
            dens_func = self.datos_funcs['dens_func']
            if(len(dens_func) > 0):
                config['FUNCS']['dens_func'] = dens_func
            elif check_flag:
                raise Exception(
                    "If Density is not read from the file you must provide an analytic function!")

        if(self.datos_vars['temperature'] is False):
            temp_func = self.datos_funcs['temp_func']
            if(len(temp_func) > 0):
                config['FUNCS']['temp_func'] = temp_func
            elif check_flag:
                raise Exception(
                    "If Temperature is not read from the file you must provide an analytic function!")

        if(self.datos_vars['velocity'] is False):
            vel_func = self.datos_funcs['vel_func']
            if(len(vel_func) > 0):
                config['FUNCS']['vel_func'] = vel_func
                config['FUNCS']['vel_direction'] = self.datos_funcs['vel_dir']
            elif check_flag:
                raise Exception(
                    "If Velocity is not read from the file you must provide an analytic function!")

        if(self.datos_vars['turbulence'] is False):
            turb_func = self.datos_funcs['turb_func']
            if(len(turb_func) > 0):
                config['FUNCS']['turb_func'] = turb_func
            elif check_flag:
                raise Exception(
                    "If Turbulence is not read from the file you must provide an analytic function!")

        config['MOL'] = self.datos_mol

        if 'mol_name' in self.datos_mol:
            fname = self.datos_mol['mol_name'] + ".dat"
            moldat_path = str(self.mol_path / fname)
            Lamda.download_molfile(
                mol=self.datos_mol['mol_name'], outfilename=moldat_path)

            config['MOL']['moldatfile'] = moldat_path
        else:
            if check_flag:
                raise Exception("You must choose a molecule!")

        rel_abundance_func = self.datos_mol['rel_abundance_func']
        if len(rel_abundance_func) <= 0 and check_flag:
            raise Exception(
                "You must provide the molecule's relative abundance!")

        config['PARS'] = self.datos_pars
        config['IMG'] = self.datos_img
        if 'dust_file' not in self.datos_dust and self.datos_dust['dust_activated'] is True and check_flag:
            raise Exception("If you want to use dust you must provide an opacity table.")
        else:
            config['DUST'] = self.datos_dust

        return config

    def load(self, path):
        """Loads bak file. Gets all the data from it and updates dictionaries.

        Args:
            path (_type_): _description_
        """
        if path is not None and len(path) != 0:
            config = configparser.ConfigParser()
            config.read(path)
            if 'VARS' in config:
                self.datos_vars.update(dict(config['VARS']))
                self.datos_vars = {key: str2bool(
                    val) for key, val in self.datos_vars.items()}
            if 'UDS' in config:
                self.datos_uds.update(dict(config['UDS']))
            if 'MOL' in config:
                self.datos_mol.update(dict(config['MOL']))
                self.mol_load_flag = True
            if 'PARS' in config:
                self.datos_pars.update(dict(config['PARS']))
            if 'IMG' in config:
                self.datos_img.update(dict(config['IMG']))
            if 'FUNCS' in config:
                self.datos_funcs.update(dict(config['FUNCS']))
            if 'DUST' in config:
                self.datos_dust.update(dict(config['DUST']))
            # Careful when reading from configparser: everything is str, no bool!

    def save_bak(self, path):
        """Creates the backup configuration file.

        Args:
            path (str): where to save bak file.
        """
        config = self.create_config(check_flag=False)
        if config:
            with open(path, 'w') as configfile:
                config.write(configfile)

    def start(self):
        """Start function to call LIME. It checks shape file format and creates the config file before starting the execution.

        Raises:
            Exception: if a shape file wasn't chosen exception will be raised. 
        """
        if 'shape_file' in self.datos_pars:
            check_format(self.datos_pars["shape_file"], self.datos_vars)
            config = self.create_config(check_flag=True)
            if config:
                with open(self.model_path / 'lime_config.ini', 'w') as configfile:
                    config.write(configfile)

            if 'fits_file' in self.datos_pars:
                config_backup = self.datos_pars['fits_file'].rsplit('.')[
                    0] + '.bak'
            else:
                config_backup = str(self.model_path / 'model.bak')

            with open(config_backup, 'w') as cbfile:
                config.write(cbfile)

            # If pylime is already a command program is run directly
            if self.lime_path is None:
                command = 'cd ' + str(self.model_path) + ' ; pylime -t lime_model.py'
            else:
                command = 'cd ' + str(self.lime_path) + ' ; . ./pylimerc.sh ; cd ' + \
                    str(self.model_path) + ' ; pylime -t lime_model.py'
            p = sub.Popen(command, shell=True)
        else:
            raise Exception("You must choose a file to run the program!")
