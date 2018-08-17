from __future__ import absolute_import

try:
    import os
    import sys
    import json
    import numpy as np
    from coord_utils import *

except ImportError as e:
    print(e)
    raise ImportError

np.set_printoptions(threshold=np.nan)

# Path to run.py script
run_dir = os.path.dirname(os.path.realpath(__file__))

# Path to particle attributes json file
json_pfile = os.path.join(run_dir, 'data/particle_properties.json') 

# Cos ( Lowest Zenith )
cosThetaMin = -1.


def load_json_file(jfile):
    """
    Load json file given filename
    """
    with open(jfile) as handle:
        j = json.load(handle)

    return j

def get_particle_props(particle_name):
    """
    Get specific particle species properties
    from default json file. 
    """
    # Get full particle attribute dictionary
    full_pdict = load_json_file(json_pfile)

    # Get specific species attributes
    particle_props_dict = full_pdict[particle_name]

    return particle_props_dict
    

def initial_buffers(particle_type, num_particles, Emin, Emax, lat, lon, height, alpha=None):
    np_position = np.ndarray((num_particles, 4), dtype=np.float32)
    np_velocity = np.ndarray((num_particles, 4), dtype=np.float32)
    np_zmel = np.ndarray((num_particles, 4), dtype=np.float32)

    # Get species attributes
    particle_dict = get_particle_props(particle_type)
    chargeC = particle_dict['charge']
    masskg  = particle_dict['masskg']
    masseV  = particle_dict['masseV']
    print('{} properties: \n\t masseV {} \n\t masskg {} \n\t charge in C {}\n\n'.format(particle_type, masseV, masskg, chargeC))

    ## Test values
    if alpha:
        E = 10**np.arange(np.log10(Emin), np.log10(Emax), 0.01)
        weights = E**-alpha
        Energy_array = np.random.choice(E, size=num_particles, p=weights/weights.sum())
    else:
        Energy_array = np.logspace(np.log10(Emin), np.log10(Emax), num_particles)
    Gamma_array = Energy_array/masseV+1.
    np_zmel[:,0] = chargeC
    np_zmel[:,1] = masskg
    np_zmel[:,2] = Energy_array
    np_zmel[:,3] = Gamma_array

    # Assign starting particle positions.
    np_position[:,0:3] = geodetic_to_geocentric(lat, lon, height)
    np_position[:,3] = 1.

    vr = -np.ones(num_particles)
    vphi = 2.*np.pi*np.random.random(num_particles)
    vtheta = np.arccos(np.random.uniform(cosThetaMin, 1, num_particles))

    # Transform to Cartesian Coords
    np_velocity[:,0:3] = sph2cart(vr, vphi, vtheta)
    np_velocity[:,3] = 0.

    return (np_position, np_velocity, np_zmel)
