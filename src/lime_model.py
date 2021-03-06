#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Notes:
#	- The above pragma line is only required if you plan to run this module as a stand-alone script to run any test harnesses which may occur after "if __name__ == '__main__'".
#
#	- You should run lime with this script in the form
#		pylime model.py
#	  You will need the location of pylime in your PATH environment variable; also you need to have the location of the limepar_classes.py module in your PYTHONPATH environment variable.

# For definitions of the classes ModelParameters and ImageParameters:
from limepar_classes import *

import numpy
import pandas as pd
from scipy.spatial import KDTree

import errno
import os
import configparser
import re as reg

from sympy import *
import math
from py_expression_eval import Parser

# Units conversion dictionary (same as macros, but with some units added)
uds_dict = {
    "AMU": 1.66053904e-27,
    "CLIGHT": 2.99792458e8,
    "HPLANCK": 6.626070040e-34,
    "KBOLTZ": 1.38064852e-23,
    "GRAV": 6.67428e-11,
    "AU": 1.495978707e11,
    "LOCAL_CMB_TEMP": 2.72548,
    "PC": 3.08567758e16,
    "PI": 3.14159265358979323846,
    "SPI": 1.77245385091,
    "CP_H2": 1,
    "CP_p_H2": 2,
    "CP_o_H2": 3,
    "CP_e": 4,
    "CP_H": 5,
    "CP_He": 6,
    "CP_Hplus": 7,
    "m": 1,     "cm": 0.01,     "km": 10**3,
    "s": 1,     "h": 60*60,
    "K": 1,
    "#/m^3": 1, "#/cm^3": 1e6,
    "rad": 1,   "º": math.pi/180
}

# Auxiliar functions


def max_dist_ordered_pts(pts_list):
    """
    max_dist_ordered_pts gives the maximum distance from a list of ordered points.

    :param pts_list: list of ordered points.
    :return: maximum distance between points in the list.
    """
    max_dist = 0
    for i in range(len(pts_list)-1):
        dist = abs(pts_list[i+1] - pts_list[i])
        if dist > max_dist:
            max_dist = dist
    return max_dist


def get_radius(x, y, z):
    """
    get_radius of the point (x,y,z) from center (0,0,0).

    :param x: x-coordinate.
    :param y: y-coordinate.
    :param z: z-coordinate.
    :return: radius to the center
    """
    # greater than zero to avoid a singularity at the origin.
    rMin = 0.1*uds_dict["AU"]
    r0 = math.sqrt(x*x+y*y+z*z)
    if r0 > rMin:
        r = r0
    else:
        r = rMin  # Just to prevent overflows at r==0!
    return r


''' TODO: Spherical conversion, not implemented.
# make sure which units + which convention for  theta, phi, and x,y,z
# *pi/180 to radians, at themoment spherical: (radial, azimuthal [0,2pi), polar [0,pi])
def sph2cart(r, theta, phi):
    x = r * sin(phi) * cos(theta)
    y = r * sin(phi) * sin(theta)
    z = r * cos(phi)
    return [x, y, z]  # line of vision, up right

def cart2sph(x, y, z):  # line of vision, derecha, arriba
    r = sqrt(x*x + y*y + z*z)
    phi = acos(z/r)
    theta = atan2(y, x)
    return [r, theta, phi]  # (radial, azimuthal [0,2pi), polar [0,pi])
'''


# Reading config ini file
config = configparser.ConfigParser()
try:
    with open('lime_config.ini') as f:
        config.read_file(f)
except IOError:
    raise Exception('Config file not found. It should be named lime_config.ini and placed in the same folder as the model.')

shape_file = config['PARS']['shape_file']

# Reading shape tabulated data file
df = pd.read_csv(shape_file, sep='\t')
for c in df.columns:
    if reg.match("Unnamed*", c):
        del df[c]
df = df.dropna(subset=['Px', 'Py', 'Pz'])
df = df.reset_index()

# Units conversion for data from the file
xyzr_uds = config['UDS']['xyzr']
df['Px'] *= uds_dict[xyzr_uds]
df['Py'] *= uds_dict[xyzr_uds]
df['Pz'] *= uds_dict[xyzr_uds]

if 'density' in config['VARS'] and config.getboolean('VARS', 'density') is True:
    df['Density'] *= uds_dict[config['UDS']['density']]

if 'velocity' in config['VARS'] and config.getboolean('VARS', 'velocity') is True:
    vel_uds = (config['UDS']['velocity']).split('/')
    df['Vx'] *= uds_dict[vel_uds[0]] / uds_dict[vel_uds[1]]
    df['Vy'] *= uds_dict[vel_uds[0]] / uds_dict[vel_uds[1]]
    df['Vz'] *= uds_dict[vel_uds[0]] / uds_dict[vel_uds[1]]

if 'temperature' in config['VARS'] and config.getboolean('VARS', 'temperature') is True:
    df['Temperature'] *= uds_dict[config['UDS']['temperature']]

if 'turbulence' in config['VARS'] and config.getboolean('VARS', 'turbulence') is True:
    vel_uds = (config['UDS']['turbulence']).split('/')
    df['Turbulence'] *= uds_dict[vel_uds[0]] / uds_dict[vel_uds[1]]

# Calculate max distance between points in shape grid
lpz = list(set(df['Pz']))
lpz.sort()
lpx = list(set(df['Px']))
lpx.sort()
lpy = list(set(df['Py']))
lpy.sort()

max_dist = math.sqrt(max_dist_ordered_pts(lpx)**2+max_dist_ordered_pts(lpy)
                     ** 2+max_dist_ordered_pts(lpz)**2) + 0.1*uds_dict['AU']

# Ini parser to evaluate analytic functions
parser = Parser()

# Ini kdtree to find nearest points
npdf = df[['Px', 'Py', 'Pz']].to_numpy()
kdtree = KDTree(npdf)

''' Option 2: using LinearNDInterpolator instead of KDtree. Problem: which fill value for velocity?
from scipy.interpolate import LinearNDInterpolator

x = df['Px']
y = df['Py']
z = df['Pz']
dens_interpol = LinearNDInterpolator((x,y,z), df['Density'], fill_value=1e3)
vx_interpol = LinearNDInterpolator((x,y,z), df['Vx'], fill_value=0) #TODO only if read
vy_interpol = LinearNDInterpolator((x,y,z), df['Vy'], fill_value=0) #TODO only if read 
vz_interpol = LinearNDInterpolator((x,y,z), df['Vz'], fill_value=0) #TODO only if read
'''

# .......................................................................


def input(macros):
    par = ModelParameters()

    # We give all the possible parameters here, but have commented out many which can be left at their defaults.
    # Parameters which must be set (they have no sensible defaults).
    # Parameters are read from the config file, but they can also be set here by hand.
    if 'radius' in config['PARS']:
        par.radius = float(config['PARS']['radius']) * \
            uds_dict[config['UDS']['radius']]
    else:
        raise Exception('radius was not specified')

    if 'minscale' in config['PARS']:
        par.minScale = float(config['PARS']['minscale']) * \
            uds_dict[config['UDS']['minscale']]
    else:
        raise Exception('minscale was not specified')

    if 'pIntensity' in config['PARS']:
        par.pIntensity = int(config['PARS']['pIntensity'])
    else:
        raise Exception('pIntensity was not specified')

    if 'sinkPoints' in config['PARS']:
        par.sinkPoints = int(config['PARS']['sinkPoints'])
    else:
        raise Exception('sinkPoints was not specified')

    # Parameters which may be omitted (i.e. left at their default values) under some circumstances.
    #
#  par.dust              = "/data/jena_thin_e6.tab"
#  par.outputfile        = "populations.pop"
#  par.binoutputfile     = "restart.pop"
#    par.gridfile          = "grid.vtk"
#    par.pregrid           = shape_file
#  par.restart           = "restart.pop"
#  par.gridInFile        = "grid_5.ds"

    #    Setting elements of the following two arrays is optional. NOTE
    #    that, if you do set any of their values, you should set as many as
    #    the number of elements returned by your function density(). The
    #    ith element of the array in question will then be assumed to refer
    #    to the ith element in the density function return. The current
    #    maximum number of elements allowed is 7, which is the number of
    #    types of collision partner recognized in the LAMBDA database.
    #
    #    Note that there is no (longer) a hard connection between the
    #    number of density elements and the number of collision-partner
    #    species named in the moldata files. This means in practice that,
    #    if you set the values for par->collPartIds, you can, if you like,
    #    set some for which there are no transition rates supplied in the
    #    moldatfiles. This might happen for example if there is a molecule
    #    which contributes significantly to the total molecular density but
    #    for which there are no measured collision rates for the radiating
    #    species you are interested in.
    #
    #    You may also omit to mention in par->collPartIds a collision
    #    partner which is specified in the moldatfiles. In this case LIME
    #    will assume the density of the respective molecules is zero.
    #
    #    If you don't set any values for any or all of these arrays,
    #    i.e. if you omit any mention of them here (we preserve this
    #    possibility for purposes of backward compatibility), LIME will
    #    attempt to replicate the algorithms employed in version 1.5, which
    #    involve guessing which collision partner corresponds to which
    #    density element. Since this was not exactly a rigorous procedure,
    #    we recommend use of the arrays.
    #
    #    par->nMolWeights: this specifies how you want the number density
    #    of each radiating species to be calculated. At each grid point a
    #    sum (weighted by par->nMolWeights) of the density values is made,
    #    then this is multiplied by the abundance to return the number
    #    density.
    #
    #    Note that there are convenient macros defined in ../src/lime.h for
    #    7 types of collision partner.
    #
    #    Below is an example of how you might use these parameters:
    #
#  par.collPartIds        = [macros["CP_H2"]] # must be a list, even when there is only 1 item.
#  par.nMolWeights        = [1.0] # must be a list, even when there is only 1 item.

#  par.collPartNames     = ["phlogiston"] # must be a list, even when there is only 1 item.
#  par.collPartMolWeights = [2.0159] # must be a list, even when there is only 1 item.

#  par.gridDensMaxValues = [1.0] # must be a list, even when there is only 1 item.
#  par.gridDensMaxLoc    = [[0.0,0.0,0.0]] # must be a list, each element of which is also a list with 3 entries (1 for each spatial coordinate).

#  par.tcmb              = 2.72548
    if 'lte' in config['PARS']:
        # par.lte_only = False by default
        par.lte_only = bool(config['PARS']['lte'])
#  par.init_lte          = False
#  par.samplingAlgorithm = 0
#  par.sampling          = 2 # Now only accessed if par.samplingAlgorithm==0 (the default).
#  par.blend             = False
#  par.polarization      = False
#  par.nThreads          = 1
#  par.nSolveIters       = 14
#  par.traceRayAlgorithm = 1
#  par.resetRNG          = False
#  par.doSolveRTE        = False
#    par.gridOutFiles      = ['0.txt','1.txt','2.txt','3.txt',"4.ds"]
    if 'moldatfile' in config['MOL']:
        mol_path = config['MOL']['moldatfile']
        # must be a list, even when there is only 1 item.
        par.moldatfile = [str(mol_path)]
    else:
        raise Exception('moldatfile was not specified')

#  par.girdatfile        = ["myGIRs.dat"] # must be a list, even when there is only 1 item.

    # Definitions for image #0. Add further similar blocks for additional images.
    #
    # by default this list par.img has 0 entries. Each 'append' will add an entry. The [-1] entry is the most recently added.
    par.img.append(ImageParameters())

    if 'trans' in config['MOL']:
        # zero-indexed J quantum number
        par.img[-1].trans = int(config['MOL']['trans']) - 1
    else:
        raise Exception('trans was not specified')

#  par.img[-1].molI              = -1
#  par.img[-1].bandwidth         = -1.0

    if 'nchan' in config['IMG']:
        par.img[-1].nchan = int(config['IMG']['nchan'])
    else:
        raise Exception('nchan was not specified')

    if 'velres' in config['IMG']:
        velres_uds = (config['UDS']['velres']).split('/')
        par.img[-1].velres = float(config['IMG']['velres']) * \
            uds_dict[velres_uds[0]] / uds_dict[velres_uds[1]]
    else:
        raise Exception('velres was not specified')

    if 'imgres' in config['IMG']:
        par.img[-1].imgres = float(config['IMG']['imgres'])
    else:
        raise Exception('imgres was not specified')

    if 'pxls' in config['IMG']:
        par.img[-1].pxls = int(config['IMG']['pxls'])
    else:
        raise Exception('pxls was not specified')

    if 'unit' in config['IMG']:
        # 0:Kelvin 1:Jansky/pixel 2:SI 3:Lsun/pixel 4:tau
        par.img[-1].unit = int(config['IMG']['unit'])
    else:
        raise Exception('unit was not specified')

#  par.img[-1].freq              = -1.0

    if 'vsys' in config['IMG']:
        vsys_uds = (config['UDS']['vsys']).split('/')
        par.img[-1].source_vel = float(config['IMG']['vsys']) * \
            uds_dict[vsys_uds[0]] / \
            uds_dict[vsys_uds[1]]  # source velocity in m/s
#  par.img[-1].theta             = 0.0
#  par.img[-1].phi               = 0.0
#  par.img[-1].incl              = 0.0
#  par.img[-1].posang            = 0.0
#  par.img[-1].azimuth           = 0.0

    if 'distance' in config['IMG']:
        par.img[-1].distance = float(config['IMG']['distance']) * \
            uds_dict[config['UDS']['distance']]
    else:
        raise Exception('distance was not specified')

#  par.img[-1].doInterpolateVels = False

    if 'fits_file' in config['PARS']:
        fits_filepath = config['PARS']['fits_file']
        # TODO: if name is too large it gets cut -> lime problem?
        fits_folder = os.path.dirname(fits_filepath)
    else:
        fits_folder = os.path.dirname(shape_file) + "/gildas/"
        fits_filepath = fits_folder + "model.fits"

    try:
        os.makedirs(fits_folder)
    except OSError as error:
        if error.errno != errno.EEXIST:
            raise

    par.img[-1].filename = str(fits_filepath)  # Output filename

#  par.img[-1].units = "0,1"

    return par

# .......................................................................
# .......................................................................
# User-defined functions:

# .......................................................................


def density(macros, x, y, z):
    """
  The value returned should be a list, each element of which is a density (in molecules per cubic metre) of a molecular species (or electrons). The molecule should be one of the 7 types currently recognized in the LAMDA database - see

          http://home.strw.leidenuniv.nl/~moldata/

  Note that these species are expected to be the bulk constituent(s) of the physical system of interest rather than species which contribute significantly to spectral-line radiation. In LIME such species are often called 'collision partners'.

  The identity of each collision partner is provided via the list parameter par.collPartIds. If you do provide this, obviously it must have the same number and ordering of elements as the density list you provide here; if you don't include it, LIME will try to guess the identities of the species you provide density values for.
    """

    # Finding nearest point in tabulated data
    dist, i = kdtree.query((x, y, z))

    # If it is too far, it is considered to be outside of the modelled structure
    if dist >= max_dist:
        return [1e3]

    if config.getboolean('VARS', 'density') is True:  # density read from tabulated data
        dens = float(df['Density'][i])
        if dens <= 1e3:
            dens = 1e3
    else:  # density calculated from analytic function
        dens_func = config['FUNCS']['dens_func']
        r = get_radius(x, y, z) / uds_dict[config['UDS']['xyzr']]

        # careful not to divide by x,y,z (they can be 0)
        dens = parser.parse(dens_func).evaluate(
            {'r': r}) * uds_dict[config['UDS']['density']]

    return [dens]

# .......................................................................


def temperature(macros, x, y, z):
    """
  This function should return a tuple of 2 temperatures (in kelvin). The 2nd is optional, i.e. you can return None for it, and LIME will do the rest.
    """

    if config.getboolean('VARS', 'temperature') is True:  # temp read from tabulated data
        dist, i = kdtree.query((x, y, z))
        temp = float(df['Temperature'][i])
    else:  # temp calculated from analytic function
        temp_func = config['FUNCS']['temp_func']
        r = get_radius(x, y, z) / uds_dict[config['UDS']['xyzr']]

        temp = parser.parse(temp_func).evaluate(
            {'r': r}) * uds_dict[config['UDS']['temperature']]

    return [temp, 0.0]

# .......................................................................


def abundance(macros, x, y, z):
    """
  This function should return a list of abundances (as fractions of the effective bulk density), 1 for each of the radiating species. Note that the number and identity of these species is set via the list of file names you provide in the par.moldatfile parameter, so make sure at least that the number of elements returned by abundance() is the same as the number in par.moldatfile!

  Note that the 'effective bulk density' mentioned just above is calculated as a weighted sum of the values returned by the density() function, the weights being provided in the par.nMolWeights parameter.
    """

    # relative abundance calculated from analytic function
    if 'rel_abundance_func' in config['MOL']:
        rel_abundance_func = config['MOL']['rel_abundance_func']
        r = get_radius(x, y, z) / uds_dict[config['UDS']['xyzr']]

        val = parser.parse(rel_abundance_func).evaluate({'r': r})
    else:
        raise Exception('rel_abundance_func was not specified')

    listOfAbundances = [val]  # must be a list, even when there is only 1 item.
    return listOfAbundances

# .......................................................................


def doppler(macros, x, y, z):
    """
  This function returns the Doppler B parameter, defined in terms of a Doppler-broadened Gaussian linewidth as follows:

                       ( -[v-v0]^2 )
          flux(v) = exp(-----------).
                       (    B^2    )

  Note that the present value refers only to the Doppler broadening due to bulk turbulence; LIME later adds in the temperature-dependent part (which also depends on molecular mass).
    """

    # turbulence read from tabulated data
    if config.getboolean('VARS', 'turbulence') is True:
        dist, i = kdtree.query((x, y, z))

        turb = float(df['Turbulence'][i])
        return turb
    else:  # turbulence calculated from analytic function
        turb_func = config['FUNCS']['turb_func']
        r = get_radius(x, y, z) / uds_dict[config['UDS']['xyzr']]

        vel_uds = (config['UDS']['turbulence']).split('/')
        val = parser.parse(turb_func).evaluate(
            {'r': r}) * uds_dict[vel_uds[0]] / uds_dict[vel_uds[1]]

        return val


# .......................................................................


def velocity(macros, x, y, z):
    """
  Gives the bulk gas velocity vector in m/s.
    """

    vel = [0, 0, 0]  # ini variable

    # velocity read from tabulated data
    if config.getboolean('VARS', 'velocity') is True:
        dist, i = kdtree.query((x, y, z))
        vel[0] = float(df['Vx'][i])
        vel[1] = float(df['Vy'][i])
        vel[2] = float(df['Vz'][i])
    # velocity calculated from RADIAL analytic function
    elif config['FUNCS']['vel_direction'] == 'radial':
        vel_func = config['FUNCS']['vel_func']
        r = get_radius(x, y, z) / uds_dict[config['UDS']['xyzr']]

        vel_uds = (config['UDS']['velocity']).split('/')
        val = parser.parse(vel_func).evaluate(
            {'r': r}) * uds_dict[vel_uds[0]] / uds_dict[vel_uds[1]]

        vel[0] = x*val/r
        vel[1] = y*val/r
        vel[2] = z*val/r
    else:  # TODO: not implemented (other vector fields)
        pass
    return vel
