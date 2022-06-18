import os


class Controller:
    def __init__(self, model, view=None) -> None:
        self.model = model
        self.view = view

    def set_view(self, view):
        self.view = view

    def open_shapefile(self):
        pars = self.model.datos_pars
        if 'shape_file' in pars:
            ini_dir_shape = os.path.dirname(pars['shape_file'])
        else:
            ini_dir_shape = self.model.ini_dir

        path = self.view.askopenfilename(ini_dir_shape, "Select file", ((
            "Text files", "*.txt"), ("CSV", "*.csv"), ("All Files", "*.*")))
        if path is not None and len(path) != 0:
            self.model.datos_pars['shape_file'] = path
            return path

    def change_datos_vars(self, checkbt_val, var):
        self.model.datos_vars[var] = checkbt_val

    def update_data(self):
        self.model.datos_uds.update(self.view.get_uds())
        self.model.datos_funcs.update(self.view.get_funcs())
        self.model.datos_mol.update(self.view.get_mol())
        self.model.datos_pars.update(self.view.get_datos_pars())
        self.model.datos_img.update(self.view.get_datos_img())

    def update_mol(self, mol):
        return self.model.update_mol(mol)

    def get_mol_name(self):
        if 'mol_name' in self.model.datos_mol:
            return self.model.datos_mol['mol_name']
        else:
            return None

    def get_mol_dic(self):
        return self.model.mol_dic

    def save(self):
        self.update_data()

        if 'fits_file' in self.model.datos_pars:
            ff = self.model.datos_pars['fits_file']
            ini_dir_bak = os.path.dirname(ff)
            ini_file_bak = os.path.splitext(os.path.basename(ff))[0]+'.bak'
        else:
            ini_dir_bak = self.model.ini_dir
            ini_file_bak = 'model.bak'

        path = self.view.asksaveasfilename(
            initialdir=ini_dir_bak, initialfile=ini_file_bak, defaultextension=".bak", filetypes=[("Backup files", "*.bak"), ("All Files", "*.*")])

        if path is not None and len(path) != 0:
            self.model.save_bak(path)

    def load(self):
        path = self.view.askopenfilename(self.model.ini_dir, "Select file", ((
            "Backup files", "*.bak"), ("Text files", "*.txt"), ("All Files", "*.*")))
        self.model.load(path)

        self.view.update_datos_vars(self.model.datos_vars)
        self.view.update_uds(self.model.datos_uds)
        self.view.update_funcs(self.model.datos_funcs)
        self.view.update_mol(self.model.datos_mol)
        self.view.update_datos_pars(self.model.datos_pars)
        self.view.update_datos_img(self.model.datos_img)

    def start(self):
        self.update_data()
        try:
            self.model.start()
        except Exception as err:
            err_text = str(err)
            self.view.popup(err_text)

    def save_fitsfile(self):
        if 'fits_file' in self.model.datos_pars:
            ff = self.model.datos_pars['fits_file']
            ini_dir_fits = os.path.dirname(ff)
            ini_file_fits = os.path.basename(ff)
        else:
            ini_dir_fits = self.model.ini_dir
            ini_file_fits = 'model.fits'

        path = self.view.asksaveasfilename(
            initialdir=ini_dir_fits, initialfile=ini_file_fits, defaultextension=".fits", filetypes=[("FITS Files", "*.fits*"), ("All Files", "*.*")])
        if path is not None and len(path) != 0:
            self.model.datos_pars['fits_file'] = path
            return path
