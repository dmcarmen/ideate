from functools import partial
import textwrap
from tkinter import filedialog, ttk
import tkinter as tk
import webbrowser

from utils import *


class View(ttk.Frame):
    """View class.

    Args:
        ttk.Frame
    """

    chosen_mol_dic = {}

    def __init__(self, parent, controller) -> None:
        """Generates all View class widgets. 

        Args:
            parent (ttk.Frame): parent frame.
            controller (Controller): Controller object.
        """
        super().__init__(parent)
        self.controller = controller

        ''' -------------------- '''
        ''' Complete application '''
        ''' -------------------- '''

        app_tab_control = ttk.Notebook(self)
        ini_tab = ttk.Frame(app_tab_control)
        pars_tab = ttk.Frame(app_tab_control)
        mol_tab = ttk.Frame(app_tab_control)
        img_tab = ttk.Frame(app_tab_control)

        self.distuds_list = ['m', 'cm', 'km', 'AU', 'PC']
        self.tuds_list = ['s', 'h']
        self.tempuds_list = ['K']
        # TODO: could be changed to m, cm... ^exponent
        self.densuds_list = ['#/m^3', '#/cm^3']
        self.angleuds_list = ['rad', 'º']
        self.unit_dic = {'Kelvin': 0, 'Jansky/pixel': 1,
                         'SI': 2, 'Lsun/pixel': 3, 'tau': 4}
        self.inv_unit_dic = {str(val): key for key,
                             val in self.unit_dic.items()}
        self.unit_list = self.unit_dic.keys()

        variables = ['px', 'py', 'pz', 'density',
                     'velocity', 'turbulence', 'temperature']

        ''' --------------------- '''
        ''' Initial configuration '''
        ''' --------------------- '''

        # Shape file selection
        shapefile_bt = ttk.Button(
            ini_tab, text="Open your shape model file", command=self.open_shapefile_bt_clicked)
        shapefile_bt.grid(row=0, column=0, padx=(
            20, 5), pady=(20, 10), sticky="nsew")

        self.shapefile_lbl = ttk.Label(ini_tab, text="No file selected.")
        self.shapefile_lbl.grid(row=0, column=1, padx=(
            10, 20), pady=(20, 10), sticky="nsew")

        # Analytic functions entries
        ini_data_frame = ttk.Frame(ini_tab)
        ini_data_frame.grid(row=1, column=0, padx=(20, 5), pady=(0, 10))

        funcs_frame = ttk.LabelFrame(
            ini_data_frame, text="Analytic functions:")

        funcs_tab_control = ttk.Notebook(funcs_frame)
        funcs_tab_control.pack(expand=1, fill='both')
        vel_tab = ttk.Frame(funcs_tab_control)
        temp_tab = ttk.Frame(funcs_tab_control)
        turb_tab = ttk.Frame(funcs_tab_control)
        dens_tab = ttk.Frame(funcs_tab_control)
        funcs_tab_control.add(dens_tab, text='Density')
        funcs_tab_control.add(vel_tab, text='Velocity')
        funcs_tab_control.add(turb_tab, text='Turbulence')
        funcs_tab_control.add(temp_tab, text='Temperature')

        f_str = "f(r)="

        # Velocity
        vel_tab_control = ttk.Notebook(vel_tab)
        modulus_tab = ttk.Frame(vel_tab_control)
        direction_tab = ttk.Frame(vel_tab_control)
        vel_tab_control.add(modulus_tab, text='Modulus')
        vel_tab_control.add(direction_tab, text='Direction')
        vel_tab_control.pack(expand=1, fill='both')

        self.direction_val = tk.StringVar()
        self.radial_bt = ttk.Radiobutton(
            direction_tab, text='Radial', value="radial", variable=self.direction_val)
        self.radial_bt.pack(expand=1, fill='both')
        other_bt = ttk.Radiobutton(
            direction_tab, text='Others', value="others", variable=self.direction_val, state=tk.DISABLED)
        other_bt.pack(expand=1, fill='both')

        self.direction_val.set('radial')
        createToolTip(other_bt, text='Not yet implemented!')

        ttk.Label(modulus_tab, text=f_str).grid(
            row=0, column=0, padx=(10, 0), pady=(10, 0))

        self.vel_entry = ttk.Entry(modulus_tab, width=14, exportselection=0)
        self.vel_entry.grid(row=0, column=1, padx=(10, 10), pady=(10, 0))
        self.vel_entry.insert(-1, '1')

        # Temperature
        ttk.Label(temp_tab, text=f_str).grid(
            row=0, column=0, padx=(10, 0), pady=(10, 0))

        self.temp_entry = ttk.Entry(temp_tab, width=14, exportselection=0)
        self.temp_entry.grid(row=0, column=1, padx=(10, 10), pady=(10, 0))
        self.temp_entry.insert(-1, '1')

        # Density
        ttk.Label(dens_tab, text=f_str).grid(
            row=0, column=0, sticky='w', padx=(10, 0), pady=(10, 0))

        self.dens_entry = ttk.Entry(
            dens_tab, width=14, exportselection=0)
        self.dens_entry.grid(row=0, column=1, padx=(10, 10), pady=(10, 0))
        self.dens_entry.insert(-1, '1')

        # Turbulence
        ttk.Label(turb_tab, text=f_str).grid(
            row=0, column=0, padx=(10, 0), pady=(10, 0))

        self.turb_entry = ttk.Entry(turb_tab, width=14, exportselection=0)
        self.turb_entry.grid(row=0, column=1, padx=(10, 10), pady=(10, 0))
        self.turb_entry.insert(-1, '0.2')

        # File variables selection
        variables_frame = ttk.LabelFrame(
            ini_data_frame, text="Variables read from the file:")

        ''' No for loop
        dens_bt = tk.Checkbutton(variables_frame, variable=BooleanVar(value=True),
                        text='Density', command=lambda: choose('Density'), state=tk.DISABLED)
        vel_bt = tk.Checkbutton(variables_frame, variable=BooleanVar(value=False),
                        text='Velocity', command=lambda: choose('Velocity'))
        temp_bt = tk.Checkbutton(variables_frame, variable=BooleanVar(value=False),
                        text='Temperature', command=lambda: choose('Temperature'))
        dens_bt.grid(row=0, column=0)
        vel_bt.grid(row=1, column=0)
        temp_bt.grid(row=2, column=0)
        '''
        self.var_dic = {}
        var_bt_dic = {}
        for index, var in enumerate(variables):
            txt = var.capitalize()  # + ' (' + uds_dict[var] + ')'
            if index < 4:
                self.var_dic[var] = tk.BooleanVar(value=True)
                var_bt_dic[var] = ttk.Checkbutton(variables_frame, variable=self.var_dic[var],
                                                  text=txt, command=partial(self.choose_var, var), state=tk.DISABLED)
            else:
                self.var_dic[var] = tk.BooleanVar(value=False)
                var_bt_dic[var] = ttk.Checkbutton(variables_frame, variable=self.var_dic[var],
                                                  text=txt, command=partial(self.choose_var, var))
            self.choose_var(var)
            if index < 2:
                var_bt_dic[var].grid(row=index %
                                     2, column=0, padx=(20, 10), sticky='w')
            else:
                var_bt_dic[var].grid(
                    row=index % 2, column=index//2, padx=(20, 0), sticky='w')

        points_txt = 'Points coordinates must be used and be provided in the file.'
        for p in variables[:3]:
            createToolTip(var_bt_dic[p], text=points_txt)

        createToolTip(var_bt_dic['velocity'],
                      text='Velocity includes columns Vx, Vy and Vz.')

        self.dens_entry["state"] = "disabled"
        var_bt_dic['density']['state'] = 'normal'

        # Units selection

        units_frame = ttk.LabelFrame(ini_data_frame, text="Units:")

        units_frame.columnconfigure(0, pad=10)
        units_frame.columnconfigure(1, pad=20)
        units_frame.columnconfigure(2, pad=10)
        units_frame.rowconfigure(0, pad=5)
        units_frame.rowconfigure(1, pad=5)

        ttk.Label(units_frame, text="Density").grid(
            row=0, column=0, sticky='w', padx=(10, 5))

        self.densuds_val = tk.StringVar(units_frame)
        densuds_menu = ttk.OptionMenu(
            units_frame, self.densuds_val, '#/m^3', *self.densuds_list)
        densuds_menu.config(width=7)
        densuds_menu.grid(row=0, column=1, sticky='w')
        densuds_menu["menu"].config(bg="WHITE")

        ttk.Label(units_frame, text="Velocity").grid(
            row=0, column=2, sticky='w')

        self.distuds_vel_val = tk.StringVar(units_frame)
        distuds_vel_menu = ttk.OptionMenu(
            units_frame, self.distuds_vel_val, 'km', *self.distuds_list)
        distuds_vel_menu.config(width=3)
        distuds_vel_menu.grid(row=0, column=3, padx=(5, 10), sticky='w')

        self.tuds_vel_val = tk.StringVar(units_frame)
        tuds_vel_menu = ttk.OptionMenu(
            units_frame, self.tuds_vel_val, 's', *self.tuds_list)
        tuds_vel_menu.config(width=1)
        tuds_vel_menu.grid(row=0, column=4, sticky='w')

        ttk.Label(units_frame, text="Temperature").grid(
            row=1, column=0, sticky='w', padx=(10, 5))

        self.tempuds_val = tk.StringVar(units_frame)
        tempuds_menu = ttk.OptionMenu(
            units_frame, self.tempuds_val, 'K', *self.tempuds_list)
        tempuds_menu.config(width=1)
        tempuds_menu.grid(row=1, column=1, sticky='w')

        ttk.Label(units_frame, text="Turbulence").grid(
            row=1, column=2, sticky='w')

        self.distuds_turb_val = tk.StringVar(units_frame)
        distuds_turb_menu = ttk.OptionMenu(
            units_frame, self.distuds_turb_val, 'km', *self.distuds_list)
        distuds_turb_menu.config(width=3)
        distuds_turb_menu.grid(row=1, column=3, padx=(5, 10))

        self.tuds_turb_val = tk.StringVar(units_frame)
        tuds_turb_menu = ttk.OptionMenu(
            units_frame, self.tuds_turb_val, 's', *self.tuds_list)
        tuds_turb_menu.config(width=1)
        tuds_turb_menu.grid(row=1, column=4)

        ttk.Label(units_frame, text="Px, Py, Pz, r").grid(
            row=2, column=0, sticky='w', padx=(10, 5))

        self.xyzruds_val = tk.StringVar(units_frame)
        distuds_menu = ttk.OptionMenu(
            units_frame, self.xyzruds_val, 'AU', *self.distuds_list)
        distuds_menu.config(width=3)
        distuds_menu.grid(row=2, column=1, sticky='w')

        '''
        # "Phi, Theta"
        ttk.Label(units_frame, text='\u03C6, \u03B8').grid(
            row=2, column=2, sticky='w')

        self.angleuds_val = tk.StringVar(units_frame)
        angleuds_menu = ttk.OptionMenu(
            units_frame, self.angleuds_val, 'º', *self.angleuds_list)
        angleuds_menu.config(width=3)
        angleuds_menu.grid(row=2, column=3, padx=(5, 10))
        '''

        variables_frame.pack(expand=1, fill='both', ipady=5)
        units_frame.pack(expand=1, fill='both', ipady=5, ipadx=10)
        funcs_frame.pack(expand=1, fill='both', ipady=5)

        # Start pylime, save, load functions

        ini_bts_tab = ttk.Frame(ini_tab)
        ini_bts_tab.grid(row=1, column=1, padx=(10, 20), pady=(20, 20))
        self.start_save_load_bts(ini_bts_tab)

        ''' ------------------ '''
        ''' General parameters '''
        ''' ------------------ '''

        pars_bts_tab = ttk.Frame(pars_tab)
        pars_bts_tab.grid(row=1, column=1, rowspan=2,
                          padx=(10, 20), pady=(20, 20))
        self.start_save_load_bts(pars_bts_tab)

        # Output location
        output_frame = ttk.Frame(pars_tab)
        output_frame.grid(row=0, padx=(20, 0), pady=(20, 10), sticky="nsew")

        ttk.Button(output_frame, text="Output location",
                   command=self.save_fitsfile_bt_clicked).grid(row=0, column=0)

        self.fitsfile_lbl = ttk.Label(output_frame, text="No file selected.")
        self.fitsfile_lbl.grid(row=0, column=1, padx=(20, 0))

        # Other general parameters
        volume_frame = ttk.LabelFrame(pars_tab, text="Volume parameters:")
        volume_frame.grid(row=1, sticky="nsew", padx=(20, 5))

        ttk.Label(volume_frame, text="Radius").grid(
            row=0, column=0, padx=(20, 0), sticky='w')

        self.radius_entry = ttk.Entry(
            volume_frame, width=12, exportselection=0)
        self.radius_entry.grid(row=1, column=0, padx=(20, 0))
        self.radius_entry.insert(-1, '800')

        self.radiusuds_val = tk.StringVar(volume_frame)
        radiusuds_menu = ttk.OptionMenu(
            volume_frame, self.radiusuds_val, 'AU', *self.distuds_list)
        radiusuds_menu.config(width=3)
        radiusuds_menu.grid(row=1, column=1, padx=(10, 0))

        minscale_lbl = ttk.Label(volume_frame, text="Minimum scale")
        minscale_lbl.grid(row=0, column=2, padx=(20, 0), sticky='w')
        createToolTip(
            minscale_lbl, text='Recommended value \u2248 (scene size or radius)*2/resolution (values chosen in ShapeX)')

        self.minscale_entry = ttk.Entry(
            volume_frame, width=12, exportselection=0)
        self.minscale_entry.grid(row=1, column=2, padx=(20, 0), sticky='w')
        self.minscale_entry.insert(-1, '12.5')  # 800*2/128

        self.minscaleuds_val = tk.StringVar(volume_frame)
        minscaleuds_menu = ttk.OptionMenu(
            volume_frame, self.minscaleuds_val, 'AU', *self.distuds_list)
        minscaleuds_menu.config(width=3)
        minscaleuds_menu.grid(row=1, column=3, padx=(10, 20), sticky='w')

        ttk.Label(volume_frame, text="Point Intensity").grid(
            row=2, column=0, padx=(20, 0), sticky='w')

        self.pintensity_entry = ttk.Entry(
            volume_frame, width=12, exportselection=0)
        self.pintensity_entry.grid(
            row=3, column=0, padx=(20, 0), pady=(0, 5), sticky='w')
        self.pintensity_entry.insert(-1, '4000')

        ttk.Label(volume_frame, text="Sink points").grid(
            row=2, column=2, padx=(20, 0), sticky='w')

        self.sinkpoints_entry = ttk.Entry(
            volume_frame, width=12, exportselection=0)
        self.sinkpoints_entry.grid(
            row=3, column=2, padx=(20, 0), pady=(0, 5), sticky='w')
        self.sinkpoints_entry.insert(-1, '400')

        # Optional general parameters
        opt_gral_frame = ttk.LabelFrame(pars_tab, text="Optional parameters:")
        opt_gral_frame.grid(row=2, sticky="nsew", padx=(20, 5))

        self.lte_val = tk.BooleanVar(value=True)
        ttk.Checkbutton(opt_gral_frame, text="LTE calculation only", variable=self.lte_val).grid(
            row=0, column=0, padx=(20, 0), pady=(0, 5), sticky='w')

        ''' ---------------- '''
        ''' Image parameters '''
        ''' ---------------- '''

        img_bts_tab = ttk.Frame(img_tab)
        img_bts_tab.grid(row=0, column=1, padx=(10, 20), pady=(20, 20))
        self.start_save_load_bts(img_bts_tab)

        img_frame = ttk.Frame(img_tab)
        img_frame.grid(row=0, column=0)

        # Image: spatial parameters
        img_spatial_frame = ttk.LabelFrame(
            img_frame, text="Spatial parameters:")
        img_spatial_frame.grid(row=0, padx=(
            20, 0), pady=(20, 10), sticky="nsew")

        ttk.Label(img_spatial_frame, text="Image resolution").grid(
            row=0, column=0, padx=(10, 0), sticky='w')

        self.imgres_entry = ttk.Entry(
            img_spatial_frame, width=13, exportselection=0)
        self.imgres_entry.grid(row=1, column=0, padx=(
            10, 0), pady=(0, 5), sticky='w')
        self.imgres_entry.insert(-1, '0.3')

        # TODO: parameter is not saved as there is only one option
        imgres_val = tk.StringVar(img_spatial_frame)
        imgres_menu = ttk.OptionMenu(
            img_spatial_frame, imgres_val, 'arcsec', *['arcsec'])
        imgres_menu.config(width=6)
        imgres_menu.grid(row=1, column=1, padx=(
            5, 10), pady=(0, 5), sticky='w')

        ttk.Label(img_spatial_frame, text="Pixels/imgres").grid(row=0,
                                                                column=2, padx=(20, 10), sticky='w')

        self.pxls_entry = ttk.Entry(
            img_spatial_frame, width=13, exportselection=0)
        self.pxls_entry.grid(row=1, column=2, padx=(
            20, 10), pady=(0, 5), sticky='w')
        self.pxls_entry.insert(-1, '100')

        ttk.Label(img_spatial_frame, text="Source distance").grid(
            row=2, column=0, padx=(10, 0), sticky='w')

        self.distance_entry = ttk.Entry(
            img_spatial_frame, width=13, exportselection=0)
        self.distance_entry.grid(row=3, column=0, padx=(
            10, 0), pady=(0, 5), sticky='w')
        self.distance_entry.insert(-1, '140.0')

        self.distuds_distance_val = tk.StringVar(img_spatial_frame)
        distuds_distance_menu = ttk.OptionMenu(
            img_spatial_frame, self.distuds_distance_val, 'PC', *self.distuds_list)
        distuds_distance_menu.config(width=3)
        distuds_distance_menu.grid(
            row=3, column=1, padx=(5, 10), pady=(0, 5), sticky='w')

        ttk.Label(img_spatial_frame, text="Units of the image").grid(
            row=2, column=2, padx=(20, 10), sticky='w')

        self.unit_val = tk.StringVar(img_spatial_frame)
        unit_menu = ttk.OptionMenu(
            img_spatial_frame, self.unit_val, 'Kelvin', *self.unit_list)
        # unit_menu.config(width=3)
        unit_menu.grid(row=3, column=2, padx=(20, 10), pady=(0, 5), sticky='w')

        # Image: velocity parameters
        img_velocity_frame = ttk.LabelFrame(
            img_frame, text="Channels and spacing parameters:")
        img_velocity_frame.grid(row=1, padx=(20, 0), sticky="nsew")

        ttk.Label(img_velocity_frame, text="Number of channels").grid(
            row=0, column=0, padx=(10, 0), sticky='w')

        self.nchan_entry = ttk.Entry(
            img_velocity_frame, width=13, exportselection=0)
        self.nchan_entry.grid(row=1, column=0, padx=(
            10, 0), pady=(0, 5), sticky='w')
        self.nchan_entry.insert(-1, '36')

        ttk.Label(img_velocity_frame, text="Velocity resolution").grid(
            row=0, column=1, padx=(20, 0), sticky='w')

        self.velres_entry = ttk.Entry(
            img_velocity_frame, width=13, exportselection=0)
        self.velres_entry.grid(row=1, column=1, padx=(
            20, 0), pady=(0, 5), sticky='w')
        self.velres_entry.insert(-1, '2')

        self.distuds_velres_val = tk.StringVar(img_velocity_frame)
        distuds_velres_menu = ttk.OptionMenu(
            img_velocity_frame, self.distuds_velres_val, 'km', *self.distuds_list)
        distuds_velres_menu.config(width=3)
        distuds_velres_menu.grid(row=1, column=2, padx=(0, 10), pady=(0, 5))

        self.tuds_velres_val = tk.StringVar(img_velocity_frame)
        tuds_velres_menu = ttk.OptionMenu(
            img_velocity_frame, self.tuds_velres_val, 's', *self.tuds_list)
        tuds_velres_menu.config(width=3)
        tuds_velres_menu.grid(row=1, column=3, padx=(0, 10), pady=(0, 5))

        # Optional img parameters
        opt_img_frame = ttk.LabelFrame(img_frame, text="Optional parameters:")
        opt_img_frame.grid(row=2, sticky="nsew", padx=(20, 0))

        ttk.Label(opt_img_frame, text="Vsys").grid(
            row=0, column=0, padx=(10, 0), sticky='w')

        self.vsys_entry = ttk.Entry(
            opt_img_frame, width=13, exportselection=0)
        self.vsys_entry.grid(row=1, column=0, padx=(10, 5), pady=(0, 5))
        self.vsys_entry.insert(-1, '0')

        self.distuds_vsys_val = tk.StringVar(opt_img_frame)
        distuds_vsys_menu = ttk.OptionMenu(
            opt_img_frame, self.distuds_vsys_val, 'km', *self.distuds_list)
        distuds_vsys_menu.config(width=3)
        distuds_vsys_menu.grid(row=1, column=1, padx=(0, 10), pady=(0, 5))

        self.tuds_vsys_val = tk.StringVar(opt_img_frame)
        tuds_vsys_menu = ttk.OptionMenu(
            opt_img_frame, self.tuds_vsys_val, 's', *self.tuds_list)
        tuds_vsys_menu.config(width=3)
        tuds_vsys_menu.grid(row=1, column=2, padx=(0, 10), pady=(0, 5))

        ''' -------------------- '''
        ''' Molecule information '''
        ''' -------------------- '''

        mol_bts_tab = ttk.Frame(mol_tab)
        mol_bts_tab.grid(row=0, column=2, padx=(10, 20), pady=(20, 20))
        self.start_save_load_bts(mol_bts_tab)

        # LAMDA files
        mol_tree_frame = ttk.Frame(mol_tab)
        mol_data_frame = ttk.Frame(mol_tab)
        mol_tree_frame.grid(row=0, column=0)
        mol_data_frame.grid(row=0, column=1, sticky='nw')

        self.mol_tree = ttk.Treeview(
            mol_tree_frame, columns=('mol'), show='headings', selectmode='browse')
        self.mol_tree.heading('mol', text='Molecule')

        mol_dic = self.controller.get_mol_dic()
        self.mol_list = list(mol_dic.keys())
        for mol in self.mol_list:
            self.mol_tree.insert('', tk.END, mol, values=mol)

        self.mol_tree.bind('<<TreeviewSelect>>', self.mol_tree_selected)
        #self.mol_tree.bind('<Double-1>', mol_tree_selected)
        #self.mol_tree.bind('<Button-1>', mol_tree_selected)
        self.mol_tree.grid(row=1, column=0, padx=(
            20, 5), pady=(0, 10), sticky='nse')

        self.mol_search_entry = EntryWithPlaceholder(mol_tree_frame, "Search")
        self.mol_search_entry.bind('<KeyRelease>', self.search_mol)
        self.mol_search_entry.grid(row=0, column=0, padx=(
            20, 5), pady=(20, 0), sticky='nsew')

        # link a scrollbar to the mol list
        mol_scrollbar = ttk.Scrollbar(mol_tree_frame,
                                      orient='vertical',
                                      command=self.mol_tree.yview
                                      )
        self.mol_tree['yscrollcommand'] = mol_scrollbar.set
        mol_scrollbar.grid(row=1, column=1, sticky='nse')

        # Other molecule information

        # Molecule name
        self.mol_name = ttk.Label(mol_data_frame, text="")
        self.mol_name.grid(row=0, column=2, padx=(
            20, 5), pady=(20, 10), sticky='sw')

        # Data labels + transition + relative abundance
        mol_data_tab = ttk.Frame(mol_data_frame)
        mol_data_tab.grid(row=1, column=2, sticky='nw')

        ttk.Label(mol_data_tab, text="Transition number:").grid(
            row=0, column=0, padx=(20, 5), pady=(0, 0), sticky='nw')

        validate_cmd_spinbox = (self.register(
            self.validate_trans_spinbox), '%P')

        self.trans_val = tk.IntVar()
        self.trans_val.set(1)

        self.trans_spinbox = ttk.Spinbox(
            mol_data_tab, from_=1, to=1, textvariable=self.trans_val, wrap=True, width=2,
            command=self.trans_changed, validate='all', validatecommand=validate_cmd_spinbox)
        self.trans_spinbox.config(width=4)
        self.trans_spinbox.grid(row=1, column=0, padx=(
            20, 5), pady=(0, 0), sticky='nw')
        self.trans_spinbox["state"] = "disabled"
        self.trans_spinbox.bind('<Return>', self.trans_changed_event)
        self.spinbox_len = 1

        ttk.Label(
            mol_data_tab, text="Relative abundance (r):").grid(row=2, column=0, padx=(
                20, 5), pady=(0, 0), sticky='nw')

        self.rel_abundance_entry = ttk.Entry(mol_data_tab, exportselection=0)
        self.rel_abundance_entry.grid(
            row=3, column=0, padx=(20, 5), sticky='nw')
        self.rel_abundance_entry.insert(-1, '1e-9')

        lamda_text = tk.Text(mol_data_tab, height=5, width=30, wrap=tk.WORD)
        line1 = "Careful! Lower and upper doesn't refer to the quantum levels. To understand the LAMDA file format click here: "
        lamda_text.insert(tk.END, line1)
        lamda_text.grid(row=4, column=0, padx=(
            20, 5), pady=(30, 0), sticky='s')
        hyperlink = HyperlinkManager(lamda_text)

        lamda_text.insert(tk.END, "LAMDA data format", hyperlink.add(partial(
            webbrowser.open, "https://home.strw.leidenuniv.nl/~moldata/molformat.html")))

        def callback(url):
            webbrowser.open_new_tab(url)

        self.mol_info = ttk.Treeview(mol_tab, height=1, selectmode='browse')
        self.mol_info.column("#0", width=0, stretch=False)
        self.mol_info.heading("#0", text="", anchor=tk.CENTER)

        headings = ['Transition', 'Upper', 'Lower',
                    'EinsteinA', 'Freq(GHz)', 'E_u(K)']
        self.mol_info['columns'] = headings
        for item in headings:
            self.mol_info.column(item, anchor=tk.CENTER,
                                 width=150, stretch=False)
            self.mol_info.heading(item, text=item, anchor=tk.CENTER)

        self.mol_info.grid(row=2, columnspan=3, pady=(10, 10), padx=(10, 0))

        app_tab_control.add(ini_tab, text='Initial configuration')
        app_tab_control.add(pars_tab, text='General parameters')
        app_tab_control.add(mol_tab, text='Molecule')
        app_tab_control.add(img_tab, text='Image')

        app_tab_control.pack(expand=1, fill='both')

    ''' ------------------ '''
    ''' Callback functions '''
    ''' ------------------ '''

    def open_shapefile_bt_clicked(self):
        if self.controller:
            path = self.controller.open_shapefile()
            if path is not None and len(path) != 0:
                self.shapefile_lbl.config(text=path.split("/")[-1])

    def start_bt_clicked(self):
        if self.controller:
            self.controller.start()

    def save_bt_clicked(self):
        if self.controller:
            self.controller.save()

    def load_bt_clicked(self):
        if self.controller:
            self.controller.load()

    def save_fitsfile_bt_clicked(self):
        if self.controller:
            path = self.controller.save_fitsfile()
            if path:
                self.fitsfile_lbl.config(text=path.split("/")[-1])

    def askopenfilename(self, initialdir, title, filetypes):
        path = filedialog.askopenfilename(
            initialdir=initialdir, title=title, filetypes=filetypes)
        return path

    def asksaveasfilename(self, initialdir, initialfile, defaultextension, filetypes):
        path = filedialog.asksaveasfilename(
            initialdir=initialdir, initialfile=initialfile, defaultextension=defaultextension, filetypes=filetypes)
        return path

    def choose_var(self, var):
        """Callback when var is chosen.

        Args:
            var (str): var chosen from the button list.
        """
        if self.controller:
            checkbt_val = self.var_dic[var].get()
            self.controller.change_datos_vars(checkbt_val, var)

        # Enable/disable analytic functions entry
        self.enable_funcs(checkbt_val, var)

    def enable_funcs(self, checkbt_val, var):
        """Actions when vars are ticked/unticked.

        Args:
            checkbt_val (_type_): _description_
            var (_type_): _description_
        """
        if(var == 'velocity'):
            self.vel_entry["state"] = "disabled" if checkbt_val is True else "normal"
            self.radial_bt["state"] = "disabled" if checkbt_val is True else "normal"
        elif var == 'temperature':
            self.temp_entry["state"] = "disabled" if checkbt_val is True else "normal"
        elif var == 'turbulence':
            self.turb_entry["state"] = "disabled" if checkbt_val is True else "normal"
        elif var == 'density':
            self.dens_entry["state"] = "disabled" if checkbt_val is True else "normal"

    def mol_tree_selected(self, event):
        selected_idx = self.mol_tree.selection()
        if len(selected_idx) > 0:
            mol = self.mol_tree.item(selected_idx[0])['values'][0]
            self.new_mol_set(mol)

    ''' ---------------- '''
    ''' Auxiliar widgets '''
    ''' ---------------- '''

    def popup(self, text):
        text = "\n ".join(textwrap.wrap(
            text, width=30, break_long_words=False))
        popup(text)

    def start_save_load_bts(self, frame):
        """Set of three buttons: Start, Save and Load.

        Args:
            frame (tk.Frame): frame where the buttons are located.
        """
        ttk.Button(frame, text="Start!", command=self.start_bt_clicked).grid(
            row=0, pady=(0, 5), ipady=10, sticky="nswe")
        ttk.Button(frame, text="Save parameters", command=self.save_bt_clicked).grid(
            row=1, pady=(5, 5), sticky="nswe")
        ttk.Button(frame, text="Load parameters", command=self.load_bt_clicked).grid(
            row=2, pady=(5, 0), sticky="nswe")

    ''' ------------------- '''
    ''' Setters and getters '''
    ''' ------------------- '''

    def entry_set_text(self, entry, text):
        """Sets entry text.

        Args:
            entry (tk.Entry).
            text (str): text to be written.
        """
        entry.delete(0, tk.END)
        entry.insert(0, text)
        return

    def update_datos_vars(self, datos_vars):
        """Updates View with vars values froom datos_vars (boolean to see which vars are read from shape).

        Args:
            datos_vars (dict): dictionary {var sring: bool}, True if the var will be read from Shape file and it's ticked, else False.
        """
        for var in datos_vars:
            checkbt_val = datos_vars[var]
            self.var_dic[var].set(checkbt_val)
            self.enable_funcs(checkbt_val, var)

    def update_uds(self, uds):
        """Updates units in GUI.

        Args:
            uds (dict): dictionary with {str units name: str value}.
        """
        if 'density' in uds:
            self.densuds_val.set(uds['density'])
        if 'temperature' in uds:
            self.tempuds_val.set(uds['temperature'])

        if 'velocity' in uds:
            vt = uds['velocity'].split('/')
            self.distuds_vel_val.set(vt[0])
            self.tuds_vel_val.set(vt[1])
        if 'turbulence' in uds:
            vt = uds['turbulence'].split('/')
            self.distuds_turb_val.set(vt[0])
            self.tuds_turb_val.set(vt[1])

        if 'xyzr' in uds:
            self.xyzruds_val.set(uds['xyzr'])

        # if 'angle' in uds:
        #   self.angleuds_val.set(uds['angle'])

        if 'radius' in uds:
            self.radiusuds_val.set(uds['radius'])
        if 'minscale' in uds:
            self.minscaleuds_val.set(uds['minscale'])

        if 'vsys' in uds:
            vt = uds['vsys'].split('/')
            self.distuds_vsys_val.set(vt[0])
            self.tuds_vsys_val.set(vt[1])

        if 'distance' in uds:
            self.distuds_distance_val.set(uds['distance'])

        if 'velres' in uds:
            vt = uds['velres'].split('/')
            self.distuds_velres_val.set(vt[0])
            self.tuds_velres_val.set(vt[1])

    def get_uds(self):
        """Gets all units values.

        Returns:
            dict: dictionary with all units {str uds name: str value}.
        """
        uds = {}
        uds['density'] = self.densuds_val.get()
        uds['temperature'] = self.tempuds_val.get()
        uds['velocity'] = self.distuds_vel_val.get() + '/' + \
            self.tuds_vel_val.get()
        uds['turbulence'] = self.distuds_turb_val.get() + '/' + \
            self.tuds_turb_val.get()
        uds['xyzr'] = self.xyzruds_val.get()
        #uds['angle'] = self.angleuds_val.get()

        uds['radius'] = self.radiusuds_val.get()
        uds['minscale'] = self.minscaleuds_val.get()
        uds['vsys'] = self.distuds_vsys_val.get() + '/' + \
            self.tuds_vsys_val.get()

        uds['distance'] = self.distuds_distance_val.get()
        uds['velres'] = self.distuds_velres_val.get() + '/' + \
            self.tuds_velres_val.get()
        return uds

    def update_funcs(self, funcs):
        """Updates functions in GUI.

        Args:
            funcs (dict): dictionary with {str function name: str function value}.
        """
        if 'dens_func' in funcs:
            self.entry_set_text(self.dens_entry, funcs['dens_func'])
        if 'temp_func' in funcs:
            self.entry_set_text(self.temp_entry, funcs['temp_func'])
        if 'vel_func' in funcs:
            self.entry_set_text(self.vel_entry, funcs['vel_func'])
        if 'vel_dir' in funcs:
            self.direction_val.set(funcs['vel_dir'])
        if 'turb_func' in funcs:
            self.entry_set_text(self.turb_entry, funcs['turb_func'])

    def get_funcs(self):
        """Gets all functions entry values.

        Returns:
            dict: dictionary with {str function name: str function value}.
        """
        funcs = {}
        funcs['dens_func'] = self.dens_entry.get()
        funcs['temp_func'] = self.temp_entry.get()
        funcs['vel_func'] = self.vel_entry.get()
        funcs['vel_dir'] = self.direction_val.get()
        funcs['turb_func'] = self.turb_entry.get()

        return funcs

    def update_datos_pars(self, pars):
        """Updates general parameters in GUI.

        Args:
            pars (dict): dictionary with {str parameter name: str parameter value}.
        """
        if 'radius' in pars:
            self.entry_set_text(self.radius_entry, pars['radius'])
        if 'minscale' in pars:
            self.entry_set_text(self.minscale_entry, pars['minscale'])
        if 'pintensity' in pars:
            self.entry_set_text(self.pintensity_entry, pars['pintensity'])
        if 'sinkpoints' in pars:
            self.entry_set_text(self.sinkpoints_entry, pars['sinkpoints'])
        if 'lte' in pars:
            self.lte_val.set(pars['lte'])
        if 'shape_file' in pars:
            self.shapefile_lbl.config(text=pars['shape_file'].split("/")[-1])
        if 'fits_file' in pars:
            self.fitsfile_lbl.config(text=pars['fits_file'].split("/")[-1])

    def get_datos_pars(self):
        """Gets all general parameters entry values.

        Returns:
            dict: dictionary with {str parameter name: str parameter value}.
        """
        pars = {}
        pars['radius'] = self.radius_entry.get()
        pars['minscale'] = self.minscale_entry.get()
        pars['pintensity'] = self.pintensity_entry.get()
        pars['sinkpoints'] = self.sinkpoints_entry.get()
        pars['lte'] = self.lte_val.get()
        # fits_file

        return pars

    def update_datos_img(self, img):
        """Updates general parameters in GUI.

        Args:
            img (dict): dictionary with {str image parameter name: str img parameter value}.
        """
        if 'pxls' in img:
            self.entry_set_text(self.pxls_entry, img['pxls'])
        if 'imgres' in img:
            self.entry_set_text(self.imgres_entry, img['imgres'])
        if 'distance' in img:
            self.entry_set_text(self.distance_entry, img['distance'])
        if 'unit' in img:
            self.unit_val.set(self.inv_unit_dic[img['unit']])
        if 'nchan' in img:
            self.entry_set_text(self.nchan_entry, img['nchan'])
        if 'velres' in img:
            self.entry_set_text(self.velres_entry, img['velres'])
        if 'vsys' in img:
            self.entry_set_text(self.vsys_entry, img['vsys'])

    def get_datos_img(self):
        """Gets image parameters from entries.

        Returns:
            dict: dictionary with {str image parameter name: str img parameter value}.
        """
        img = {}
        img['pxls'] = self.pxls_entry.get()
        # TODO: coger las unidades (ahora mismo solo 1)
        img['imgres'] = self.imgres_entry.get()
        img['distance'] = self.distance_entry.get()
        img['unit'] = self.unit_dic[self.unit_val.get()]
        img['nchan'] = self.nchan_entry.get()
        img['velres'] = self.velres_entry.get()
        img['vsys'] = self.vsys_entry.get()

        return img

    # Molecule information functions
    def update_mol(self, datos_mol):
        """Updates molecule information in GUI.

        Args:
            datos_mol (dict): dictionary that can include {'mol_name': molecule name, 'trans': transition number, 
                'rel_abundance_func': relative abundance function}
        """
        if 'mol_name' in datos_mol:  # TODO: choose molecule in the tree instead...
            mol_name = datos_mol['mol_name']
            if mol_name not in self.mol_tree.get_children(''):
                self.restore_tree(self.mol_tree, self.mol_list)
                self.entry_set_text(self.mol_search_entry, '')
            self.mol_tree.selection_set(mol_name)
            # self.new_mol_set(mol_name)

            if 'trans' in datos_mol:
                self.trans_val.set(datos_mol['trans'])
        if 'rel_abundance_func' in datos_mol:
            self.entry_set_text(self.rel_abundance_entry,
                                datos_mol['rel_abundance_func'])

    def get_mol(self):
        """Gets molecule information (transition and relative abundance function)

        Returns:
            dict: dictionary with {'trans': transition number, 'rel_abundance_func': relative abundance function}
        """
        mol = {}
        if self.trans_spinbox.get() is not None:
            mol['trans'] = self.trans_spinbox.get()
        mol['rel_abundance_func'] = self.rel_abundance_entry.get()

        return mol

    def new_mol_set(self, mol):
        """Function called when a new molecule is selected.

        Args:
            mol (str): molecule name
        """
        self.chosen_mol_dic = self.controller.update_mol(mol)
        if self.chosen_mol_dic is not None:
            old_mol = self.chosen_mol_dic['old_mol']
            if len(old_mol) == 0 or old_mol != mol:  # if it is not the same molecule as before
                # We change nummber of possible transitions accordingly
                self.spinbox_len = len(
                    self.chosen_mol_dic['radtransitions'])
                self.trans_spinbox.config(to=self.spinbox_len)
                self.trans_spinbox["state"] = "enabled"
                old_trans = self.trans_val.get()
                if old_trans < self.spinbox_len:
                    # to keep transition if loading a bak file
                    self.trans_val.set(old_trans)
                else:
                    self.trans_val.set(1)
                self.trans_changed()

                # Prints molecule name in the GUI.
                mol_name = self.chosen_mol_dic['enlevels'].meta['molecule']
                wrapped_mol_name = "\n ".join(textwrap.wrap(
                    mol_name, width=45, break_long_words=False))
                self.mol_name.config(text=wrapped_mol_name)

    def restore_tree(self, tree, data):
        """Updates tree with data (cleaning previous one).

        Args:
            tree (tk.Tree).
            data (list): data to populate tree.
        """
        tree.delete(*tree.get_children())
        for item in data:
            tree.insert('', tk.END, item, values=item)

    def search_mol(self, event):
        """Callback when molecule is searched.

        Args:
            event (_type_): _description_
        """
        val = event.widget.get()
        if val == '':
            data = self.mol_list
        else:
            data = []
            for item in self.mol_list:
                if val.lower() in item.lower():
                    data.append(item)

        self.restore_tree(self.mol_tree, data)

        mol_name = self.controller.get_mol_name()

        if mol_name in data:
            for child in self.mol_tree.get_children():
                if self.mol_tree.item(child)["values"][0] == mol_name:
                    idx = child
                    break
            self.mol_tree.selection_set(idx)

    def trans_changed_event(self, event):
        if self.trans_spinbox.get() != '':
            self.trans_changed()

    def trans_changed(self):
        """When transition is changed it will print out the new transition information.
        """
        trans_number = int(self.trans_spinbox.get())
        trans_table = self.chosen_mol_dic['radtransitions']
        if len(trans_table) > 0 and trans_number <= self.spinbox_len:
            #headings = trans_table.colnames
            for item in self.mol_info.get_children():
                self.mol_info.delete(item)
            self.mol_info.insert(parent='', index='end', iid=0, text='', values=list(
                trans_table[trans_table['Transition'] == trans_number][0]))

    ''' ---------- '''
    ''' Validators '''
    ''' ---------- '''

    def validate_trans_spinbox(self, val):
        if val.isnumeric() is True or val == '':
            return True
        else:
            return False
