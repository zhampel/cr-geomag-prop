from __future__ import absolute_import

try:
    import os
    import sys
    import numpy
    import astropy.coordinates as coords
    from astropy import units as u

except ImportError as e:
    print(e)
    raise ImportError

numpy.set_printoptions(threshold=numpy.nan)

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
cosThetaMin = -1. #75 #0.707106781186548


def rotation_matrix(axis, theta):
    """
    Return the rotation matrix associated with counterclockwise rotation about
    the given axis by theta radians.
    http://stackoverflow.com/questions/6802577/python-rotation-of-3d-vector

    Parameters
    ----------
    axis       : array_like
                 Axis about which to rotate
    theta      : float
                 Rotation angle in radians

    Returns
    -------
    rot_matrix : 2d_array_like
                 Rotation matrix

    Example
    -------
    >>> from particle_utils import rotation_matrix
    >>> import numpy
    >>> axis = [0,0,1] # z-axis
    >>> theta = numpy.radians(45) # 45 degrees in radians
    >>> rotation_matrix(axis, theta)
    array([[ 0.70710678, -0.70710678,  0.        ],
           [ 0.70710678,  0.70710678,  0.        ],
           [ 0.        ,  0.        ,  1.        ]])
    """
    # Ensure axis is a normalized vector
    axis = numpy.asarray(axis)
    axis = axis/numpy.sqrt(numpy.dot(axis, axis))
    theta = numpy.asarray(theta)

    # Coefficients used to define rotation matrix
    a = numpy.cos(theta/2.0)
    b, c, d = -axis*numpy.sin(theta/2.0)
    aa, bb, cc, dd = a*a, b*b, c*c, d*d
    bc, ad, ac, ab, bd, cd = b*c, a*d, a*c, a*b, b*d, c*d

    # Form rotation matrix
    rot_matrix = numpy.array([[aa+bb-cc-dd, 2*(bc+ad), 2*(bd-ac)],
                              [2*(bc-ad), aa+cc-bb-dd, 2*(cd+ab)],
                              [2*(bd+ac), 2*(cd-ab), aa+dd-bb-cc]])

    return rot_matrix


def rotate_about_axis(v, axis, theta):
    """
    Return the rotated vector v after rotation about axis by theta radians

    Parameters
    ----------
    v          : array_like
                 Axis about which to rotate
    axis       : array_like
                 Axis about which to rotate
    theta      : float
                 Rotation angle in radians

    Returns
    -------
    rot_matrix : 2d_array_like
                 Rotation matrix

    Example
    -------
    >>> from particle_utils import rotate_about_axis
    >>> import numpy
    >>> axis = [0,0,1] # z-axis
    >>> theta = numpy.radians(45) # 45 degrees in radians
    >>> v = [1,0,0] # vector to rotate
    >>> rotate_about_axis(v, axis, theta)
    array([ 0.70710678,  0.70710678,  0.        ])
    >>> v = [1,1,1] # vector to rotate
    >>> rotate_about_axis(v, axis, theta)
    array([ -1.11022302e-16,   1.41421356e+00,   1.00000000e+00])
    """
    # If axis is zero vector, return unrotated v
    # (can't normalize in ``rotation_matrix``)
    if (numpy.array_equal(axis,numpy.zeros(len(axis)))):
        return v

    # Rotate v using ``rotation_matrix`` call
    rot_v = numpy.dot(rotation_matrix(axis,theta),v)

    return rot_v


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
    >>> import numpy
    >>> r, az, el = 1, numpy.radians(45), numpy.radians(45)
    >>> sph2cart(r, az, el)
    (0.5, 0.49999999999999989, 0.70710678118654757)
    >>> r, az, el = 1, numpy.radians(45), 0
    >>> sph2cart(r, az, el)
    (0.0, 0.0, 1.0)
    """
    rsin_theta = r * numpy.sin(el)
    x = rsin_theta * numpy.cos(az)
    y = rsin_theta * numpy.sin(az)
    z = r * numpy.cos(el)
    return x, y, z

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
    np_position = numpy.ndarray((num_particles, 4), dtype=numpy.float32)
    np_velocity = numpy.ndarray((num_particles, 4), dtype=numpy.float32)
    np_zmel = numpy.ndarray((num_particles, 4), dtype=numpy.float32)

    ## Test values
    if alpha:
        E = 10**numpy.arange(numpy.log10(Emin), numpy.log10(Emax), 0.01)
        weights = E**-alpha
        Energy_array = numpy.random.choice(E, size=num_particles, p=weights/weights.sum())
    else:
        Energy_array = numpy.logspace(numpy.log10(Emin),numpy.log10(Emax),num_particles)
    Gamma_array = Energy_array/masseV+1.
    np_zmel[:,0] = chargeC
    np_zmel[:,1] = masskg
    np_zmel[:,2] = Energy_array
    np_zmel[:,3] = Gamma_array

    #r = (outer_radius-inner_radius)*numpy.random.random(num_particles)+inner_radius
    ##phi = 0*numpy.pi/180*numpy.ones(num_particles)
    #phi = 2*numpy.pi*numpy.random.random(num_particles)
    ##theta = numpy.arccos(numpy.random.random(num_particles))
    #theta = numpy.arccos(2*numpy.random.random(num_particles)-1)
    ##theta = 45*numpy.pi/180*numpy.ones(num_particles)

    # Assign starting particle positions.
    np_position[:,0:3] = geodetic_to_geocentric(lat, lon, height)
    np_position[:,3] = 1.

    vr = -norm_vel*numpy.ones(num_particles)
    vphi = 2.*numpy.pi*numpy.random.random(num_particles)
    #vphi = numpy.pi*numpy.random.random(num_particles)
    vtheta = numpy.arccos(numpy.random.uniform(cosThetaMin,1,num_particles))

    # Transform to Cartesian Coords
    vx,vy,vz = sph2cart(vr, vphi, vtheta)

    np_velocity[:,0] = vx#+numpy.random.normal(0,numpy.sqrt(norm), len(np_velocity[:,0]))
    np_velocity[:,1] = vy#+numpy.random.normal(0,numpy.sqrt(norm), len(np_velocity[:,0]))
    np_velocity[:,2] = vz#+numpy.random.normal(0,numpy.sqrt(norm), len(np_velocity[:,0]))
    np_velocity[:,3] = 0.

    z_axis = numpy.zeros(3)
    z_axis[2] = 1
    rot_axis = numpy.zeros((num_particles,3))
    for i in range(num_particles):
        vel_i = np_velocity[i,0:3].copy()
        pos_i = np_position[i,0:3].copy()
        #rot_axis = numpy.cross(z_axis,pos_i)
        #rot_angle = numpy.arccos(numpy.dot(z_axis,pos_i)/numpy.sqrt(numpy.dot(pos_i,pos_i)))
        #vel_i = rotate_about_axis(vel_i,rot_axis,rot_angle)
        np_velocity[i,0:3] = vel_i

    return (np_position, np_velocity, np_zmel)
