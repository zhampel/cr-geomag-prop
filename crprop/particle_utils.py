from __future__ import absolute_import

try:
    import os
    import sys
    import numpy as np
    import astropy.coordinates as coords
    from astropy import units as u

except ImportError as e:
    print(e)
    raise ImportError

np.set_printoptions(threshold=np.nan)

# Particle Properties
# Proton
massMeV = 938.272013
masseV = 938272013.0
masskg = 1.67262161014e-27
chargeC = 1.602176462e-19

# Set scale of positions and velocities
outer_radius = 10.501
inner_radius = 10.5
norm_vel = 1

# HAWC Observatory geocentric coordinates (in Earth radii)
hawcX = -0.1205300654
hawcY = -0.939836962102
hawcZ = 0.323942291206

# Cos ( Lowest Zenith )
cosThetaMin = -1.

def sph2cart(r, az, el):
    """
    Return the Cartesian values of elements defined in spherical coordinates

    Parameters
    ----------
    r  : float
         Radius value
    az : float
         azimuth value in radians
    el : float
         theta value in radians


    Returns
    -------
    x  : float
         x value
    y  : float
         y value
    z  : float
         z value

    Example
    -------
    >>> from particle_utils import sph2cart
    >>> import numpy as np
    >>> r, az, el = 1, np.radians(45), np.radians(45)
    >>> sph2cart(r, az, el)
    (0.5, 0.49999999999999989, 0.70710678118654757)
    >>> r, az, el = 1, np.radians(45), 0
    >>> sph2cart(r, az, el)
    (0.0, 0.0, 1.0)
    """
    rsin_theta = r * np.sin(el)
    x = rsin_theta * np.cos(az)
    y = rsin_theta * np.sin(az)
    z = r * np.cos(el)
    return np.array([x, y, z]).T

def geodetic_to_geocentric(lat, lon, height=1):
    """
    Convert Geodetic direction to Geocentric positional coordinates.

    Parameters
    ----------
    lat : float
          geodetic latitude(s) in degrees
    lon : float
          geodetic longitude(s) in degrees
    height : float, optional
             height above the Earth in Earth radii

    Returns
    -------
    x : float
        geocentric x value(s) in Earth radii
    y : float
        geocentric y value(s) in Earth radii
    z : float
        geocentric z value(s) in Earth radii

    """

    r = 6.37781e6 # radius of the Earth
    e_pos = coords.EarthLocation.from_geodetic(lat=lat*u.deg, lon=lon*u.deg,
                                               height=height*r*u.meter)
    x = e_pos.x.value/r
    y = e_pos.y.value/r
    z = e_pos.z.value/r

    return x, y, z

def initial_buffers(num_particles, Emin, Emax, lat, lon, height, alpha=None):
    np_position = np.ndarray((num_particles, 4), dtype=np.float32)
    np_velocity = np.ndarray((num_particles, 4), dtype=np.float32)
    np_zmel = np.ndarray((num_particles, 4), dtype=np.float32)

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

    vr = -norm_vel*np.ones(num_particles)
    vphi = 2.*np.pi*np.random.random(num_particles)
    vtheta = np.arccos(np.random.uniform(cosThetaMin, 1, num_particles))

    # Transform to Cartesian Coords
    np_velocity[:,0:3] = sph2cart(vr, vphi, vtheta)
    np_velocity[:,3] = 0.

    return (np_position, np_velocity, np_zmel)
