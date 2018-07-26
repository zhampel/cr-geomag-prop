from __future__ import absolute_import

try:
    import os
    import sys
    import numpy

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
    """
    axis = numpy.asarray(axis)
    theta = numpy.asarray(theta)
    axis = axis/numpy.sqrt(numpy.dot(axis, axis))
    a = numpy.cos(theta/2.0)
    b, c, d = -axis*numpy.sin(theta/2.0)
    aa, bb, cc, dd = a*a, b*b, c*c, d*d
    bc, ad, ac, ab, bd, cd = b*c, a*d, a*c, a*b, b*d, c*d
    return numpy.array([[aa+bb-cc-dd, 2*(bc+ad), 2*(bd-ac)],
                     [2*(bc-ad), aa+cc-bb-dd, 2*(cd+ab)],
                     [2*(bd+ac), 2*(cd-ab), aa+dd-bb-cc]])

def rotate_about_axis(v, axis, theta):
    if (numpy.array_equal(axis,numpy.zeros(len(axis)))):
        return v
    return numpy.dot(rotation_matrix(axis,theta),v)

def sph2cart(r, az, el):
    rsin_theta = r * numpy.sin(el)
    x = rsin_theta * numpy.cos(az)
    y = rsin_theta * numpy.sin(az)
    z = r * numpy.cos(el)
    return x, y, z

def initial_buffers(num_particles, Emin, Emax, alpha=None):
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

    # HAWC Values
    np_position[:,0] = hawcX*3
    np_position[:,1] = hawcY*3
    np_position[:,2] = hawcZ*3
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
