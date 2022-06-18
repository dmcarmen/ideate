import configparser
from pathlib import Path
from astroquery.lamda import Lamda
import subprocess as sub
import warnings

from utils import *


class Model:
    # TODO: de donde cogerlos
    lime_path = "/pcdisk/kepler/cdiez/work/lime/"
    model_path = "/pcdisk/kepler/cdiez/work/csic/gui/"
    mol_path = model_path + "mols/"
    Path(mol_path).mkdir(parents=True, exist_ok=True)

    ini_dir = "~/work/csic/"

    datos_vars = {}
    datos_pars = {}
    datos_mol = {}
    datos_img = {}
    datos_uds = {}
    datos_funcs = {}

    def __init__(self) -> None:
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            self.mol_dic = Lamda.molecule_dict
        self.mol_load_flag = False

    def update_mol(self, mol):
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
            moldat_path = self.mol_path + self.datos_mol['mol_name'] + ".dat"
            Lamda.download_molfile(
                mol=self.datos_mol['mol_name'], outfilename=moldat_path)
            # TODO: path choosable

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

        return config

    def load(self, path):
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
            # Cuidado al leerlo es str todo...

    def save_bak(self, path):
        config = self.create_config(check_flag=False)
        if config:
            with open(path, 'w') as configfile:
                config.write(configfile)

    def start(self):
        if 'shape_file' in self.datos_pars:
            check_format(self.datos_pars["shape_file"], self.datos_vars)
            config = self.create_config(check_flag=True)
            if config:
                with open('lime_config.ini', 'w') as configfile:
                    config.write(configfile)

            if 'fits_file' in self.datos_pars:
                config_backup = self.datos_pars['fits_file'].rsplit('.')[
                    0] + '.bak'
            else:
                config_backup = self.model_path + 'model.bak'

            with open(config_backup, 'w') as cbfile:
                config.write(cbfile)

            command = 'cd ' + self.lime_path + ' ; ./configure ; make pylime &>/dev/null; . ./pylimerc.sh ; cd ' + \
                self.model_path + ' ; pylime -t lime_model.py'
            p = sub.Popen(command, shell=True)
            #output, errors = p.communicate()
        else:
            raise Exception("You must choose a file to run the program!")
