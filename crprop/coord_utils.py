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

np.set_printoptions(threshold=sys.maxsize)

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
    >>> theta = np.radians(45) # 45 degrees in radians
    >>> rotation_matrix(axis, theta)
    array([[ 0.70710678, -0.70710678,  0.        ],
           [ 0.70710678,  0.70710678,  0.        ],
           [ 0.        ,  0.        ,  1.        ]])
    """
    # Ensure axis is a normalized vector
    axis = np.asarray(axis)
    axis = axis/np.sqrt(np.dot(axis, axis))
    theta = np.asarray(theta)

    # Coefficients used to define rotation matrix
    a = np.cos(theta/2.0)
    b, c, d = -axis*np.sin(theta/2.0)
    aa, bb, cc, dd = a*a, b*b, c*c, d*d
    bc, ad, ac, ab, bd, cd = b*c, a*d, a*c, a*b, b*d, c*d

    # Form rotation matrix
    rot_matrix = np.array([[aa+bb-cc-dd, 2*(bc+ad), 2*(bd-ac)],
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
    >>> theta = np.radians(45) # 45 degrees in radians
    >>> v = [1,0,0] # vector to rotate
    >>> rotate_about_axis(v, axis, theta)
    array([ 0.70710678,  0.70710678,  0.        ])
    >>> v = [1,1,1] # vector to rotate
    >>> rotate_about_axis(v, axis, theta)
    array([ -1.11022302e-16,   1.41421356e+00,   1.00000000e+00])
    """
    # If axis is zero vector, return unrotated v
    # (can't normalize in ``rotation_matrix``)
    if (np.array_equal(axis, np.zeros(len(axis)))):
        return v

    # Rotate v using ``rotation_matrix`` call
    rot_v = np.dot(rotation_matrix(axis, theta), v)

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

