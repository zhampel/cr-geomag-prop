from __future__ import absolute_import

try:
    import os
    import argparse
    import pyopencl as cl # OpenCL - GPU computing interface
    from pyopencl.tools import get_gl_sharing_context_properties
    from OpenGL.GL import * # OpenGL - GPU rendering interface
    from OpenGL.GLU import * # OpenGL tools (mipmaps, NURBS, perspective projection, shapes)
    from OpenGL.GLUT import * # OpenGL tool to make a visualization window
    from OpenGL.arrays import vbo 
    import numpy # Number tools
    import sys # System tools (path, modules, maxint)
    from PIL import Image

except ImportError as e:
    print(e)
    raise ImportError

# PyOpenCL memory flags
mf = cl.mem_flags

numpy.set_printoptions(threshold=numpy.nan)

# OpenGL window dimensions and perspective
width = 720
height = 576
zoom = 60.

# Path to run.py script
run_dir = os.path.dirname(os.path.realpath(__file__))

# Path to output frame pngs
frame_output_dir = os.path.join(run_dir, 'frames')
frame_prefix = os.path.join(frame_output_dir, 'particle')

# OpenCL source code directory
cl_src_path = os.path.join(run_dir, 'cl_src')

# Whether to save frames to pngs
save_frames = False

# Continuously rotate perspective
rotate_perspective = False

# size of final render
w = width
h = height

frame = 0

# Particle Properties
massMeV = 938.272013
masseV = 938272013.0
masskg = 1.67262161014e-27
chargeC = 1.602176462e-19

# Set scale of positions and velocities
outer_radius = 10.501
inner_radius = 10.5
norm_vel = 1
#norm_vel = 200
# HAWC Geocentric Coordinates (In Earth Radii)
hawcX = -0.1205300654
hawcY = -0.939836962102
hawcZ = 0.323942291206

# Cos ( Lowest Zenith )
cosThetaMin = -1. #75 #0.707106781186548

# Set the time step and pause functionality
time_step = 0.0005
time_pause_var = time_step
# Set initial step to 0 to start paused
time_step = 0

# Mouse functionality
mouse_down = False
mouse_old = {'x': 0., 'y': 0.}
rotate = {'x': -55., 'y': 0., 'z': 45.}
translate = {'x': 0., 'y': 0., 'z': 0.}
initial_translate = {'x': 0., 'y': 0., 'z': -outer_radius}

def check_positive_int(value):
    ivalue = int(value)
    if ivalue <= 0:
         raise argparse.ArgumentTypeError("%s is an invalid positive int value" % value)
    return ivalue

def check_positive_float(value):
    ivalue = float(value)
    if ivalue <= 0:
         raise argparse.ArgumentTypeError("%s is an invalid positive float value" % value)
    return ivalue

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

def glut_window():
    global initRun
    glutInit(sys.argv)
    glutInitDisplayMode(GLUT_RGBA | GLUT_DOUBLE | GLUT_DEPTH)
    glutInitWindowSize(width, height)
    glutInitWindowPosition(0, 0)
    window = glutCreateWindow("Particle Simulation")

    glClearColor(0.0,0.0,0.0,0.0) # Black Background
    #glClearColor(1.0,1.0,1.0,0.0) # White Background
    glutDisplayFunc(on_display)  # Called by GLUT every frame
    glutKeyboardFunc(on_key)
    glutMouseFunc(mouse)
    glutMotionFunc(motion)
    glutTimerFunc(10, on_timer, 10)  # Call draw every 30 ms

    return(window)

def initial_buffers(num_particles):
    np_position = numpy.ndarray((num_particles, 4), dtype=numpy.float32)
    np_color = numpy.ndarray((num_particles, 4), dtype=numpy.float32)
    np_velocity = numpy.ndarray((num_particles, 4), dtype=numpy.float32)
    np_zmel = numpy.ndarray((num_particles, 4), dtype=numpy.float32)

    ## Test values
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

    #x,y,z = sph2cart(r, phi, theta)
    #np_position[:,0] = x
    #np_position[:,1] = y
    #np_position[:,2] = z
    #np_position[:,3] = 1.

    #np_velocity[:,0] = norm_vel*(0.5-numpy.random.random_sample((num_particles, )))
    #np_velocity[:,1] = norm_vel*(0.5-numpy.random.random_sample((num_particles, )))
    #np_velocity[:,2] = norm_vel*(0.5-numpy.random.random_sample((num_particles, )))

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
    #vx,vy,vz = -hawcX,-hawcY,-hawcZ
    #norm = numpy.sqrt(vx**2 + vy**2 + vz**2)
    #vx *= norm_vel/norm 
    #vy *= norm_vel/norm 
    #vz *= norm_vel/norm 

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

    # Arrays for OpenGL bindings
    gl_position = vbo.VBO(data=np_position, usage=GL_DYNAMIC_DRAW, target=GL_ARRAY_BUFFER)
    gl_position.bind()
    gl_color = vbo.VBO(data=np_color, usage=GL_DYNAMIC_DRAW, target=GL_ARRAY_BUFFER)
    gl_color.bind()

    return (np_position, np_velocity, np_zmel, gl_position, gl_color)

def on_timer(t):
    glutTimerFunc(t, on_timer, t)
    glutPostRedisplay()

def on_key(*args):
    global save_frames, time_step, rotate_perspective

    # Pause and restart
    if args[0] == ' ' or args[0] == 'p':
        time_step = time_pause_var-time_step

    # Rotate vieweing perspective
    if args[0] == 'r':
        rotate_perspective = not rotate_perspective

    # Save frames to file
    if args[0] == 's':
        save_frames = not save_frames
        if not os.path.exists(frame_output_dir):
            os.makedirs(frame_output_dir)

    # Exit program
    if args[0] == '\033' or args[0] == 'q':
        sys.exit()

def mouse(button, state, x, z):
    global action
    if (button==GLUT_LEFT_BUTTON):
        action = "ROTATE"
    elif (button==GLUT_RIGHT_BUTTON):
        action = "ZOOM"
    elif (button==GLUT_MIDDLE_BUTTON):
        action = "TRANS"

    mouse_old['x'] = x
    mouse_old['z'] = z

def on_mouse_rotate(x, z):
    rotate['x'] += (z - mouse_old['z']) * .2
    rotate['z'] += (x - mouse_old['x']) * .2

def on_mouse_trans(x, z):
    translate['x'] += x - mouse_old['x']
    translate['z'] += z - mouse_old['z']

def on_mouse_zoom(x, z):
    global zoom
    zoom -= z - mouse_old['z']
    if (zoom > 150.):
        zoom = 150.
    elif zoom < 1:
        zoom = 1.1

def motion(x, z):
    if action=="ROTATE":
        on_mouse_rotate(x, z)
    elif action=="ZOOM":
        on_mouse_zoom(x, z)
    elif action=="TRANS":
        on_mouse_trans(x, z)
    else:
        print("Unknown action\n")
    mouse_old['x'] = x
    mouse_old['z'] = z
    glutPostRedisplay()

def axis(length):
    """ Draws an axis (basicly a line with a cone on top) """
    glPushMatrix()
    glBegin(GL_LINES)
    glVertex3d(0,0,0)
    glVertex3d(0,0,length)
    glEnd()
    glTranslated(0,0,length)
    glutWireCone(0.04,0.2, 12, 9)
    glPopMatrix()
    
def threeAxis(length):
    """ Draws an X, Y and Z-axis """ 
    glPushMatrix()
    # Z-axis
    glColor3f(1.0,0.0,0.0)
    axis(length)
    # X-axis
    glRotated(90,0,1.0,0)
    glColor3f(0.0,1.0,0.0)
    axis(length)
    # Y-axis
    glRotated(-90,1.0,0,0)
    glColor3f(0.0,0.0,1.0)
    axis(length)
    glPopMatrix()


def on_display():

    # Rotate camera
    if rotate_perspective:
        dx = 0.3
        rotate['z'] += dx

    """Render the particles"""        
    global frame
    # Update or particle positions by calling the OpenCL kernel
    cl.enqueue_acquire_gl_objects(queue, [cl_gl_position, cl_gl_color])
    kernelargs = (cl_gl_position, cl_gl_color, cl_velocity, cl_zmel, cl_start_position, cl_start_velocity, numpy.float32(log_Emax), numpy.float32(Erange), numpy.float32(time_step))
    program.particle_prop(queue, (num_particles,), None, *(kernelargs))
    cl.enqueue_release_gl_objects(queue, [cl_gl_position, cl_gl_color])
    queue.finish()
    glFlush()

    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()

    glViewport(0, 0, width, height)
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluPerspective(zoom, width / float(height), .1, 10000.)

    # Handle mouse transformations
    glTranslatef(initial_translate['x'], initial_translate['y'], initial_translate['z'])
    glRotatef(rotate['x'], 1, 0, 0)
    glRotatef(rotate['z'], 0, 0, 1)
    glTranslatef(translate['x'], translate['y'], translate['z'])
    
    # Render the particles
    glEnable(GL_POINT_SMOOTH)
    glPointSize(2)
    glEnable(GL_BLEND)
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)

    # Set up the VBOs
    gl_color.bind()
    glColorPointer(4, GL_FLOAT, 0, gl_color)
    gl_position.bind()
    glVertexPointer(4, GL_FLOAT, 0, gl_position)
    glEnableClientState(GL_VERTEX_ARRAY)
    glEnableClientState(GL_COLOR_ARRAY)

    # Draw the VBOs
    glDrawArrays(GL_POINTS, 0, num_particles)

    glDisableClientState(GL_COLOR_ARRAY)
    glDisableClientState(GL_VERTEX_ARRAY)

    glDisable(GL_BLEND)
    
    # Draw Axes
    threeAxis(1.5)
    #glClear(GL_COLOR_BUFFER_BIT)

    # Draw Transparent Earth
    glEnable(GL_BLEND)
    #glBlendFunc (GL_SRC_ALPHA, GL_ONE) 
    #glBlendFunc(GL_ONE, GL_ONE_MINUS_DST_ALPHA)
    #glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_DST_ALPHA)
    glColor4f(0.0,0.0,1.0, 0.15)
    glutSolidSphere(1.0,32,32)
    glDisable(GL_BLEND)

    glutSwapBuffers()
        
    # NOTE: the GL_RGB / GL_RGBA difference
    if save_frames:
        png_file_write(frame_prefix, frame, glReadPixels( 0,0, w, h, GL_RGBA, GL_UNSIGNED_BYTE))
        #png_file_write("frames/particles", frame, glReadPixels( 0,0, w, h, GL_RGBA, GL_UNSIGNED_BYTE))
        frame += 1



#######################################################################################

# write a png file from GL framebuffer data

def png_file_write(name, number, data):
    im = Image.frombuffer("RGBA", (720,576), data, "raw", "RGBA", 0, 0)
    fnumber = "%05d" % number
    im.save(name + fnumber + ".png")

######################################################################################



def printHelp():
    print """\n\n
          ------------------------------------------------------------------------------\n
          Left Mouse Button:        - rotate viewing position\n
          Middle Mouse Button:      - translate the scene\n
          Right Mouse Button:       - zoom in and out of scene\n
          
          Keys
            p:                      - start or pause the program\n
            q,Esc:                  - exit the program\n
            s:                      - save frames to file (default is no save)\n
          ------------------------------------------------------------------------------\n
          \n"""

#-----
# MAIN
#-----
if __name__=="__main__":

    global args
    parser = argparse.ArgumentParser(description="Convolutional NN Training Script")
    parser.add_argument("-n", "--num_particles", dest="num_particles", default=1000, type=check_positive_int, help="Number of particles to simulate")
    parser.add_argument("-e", "--Emin", dest="Emin", default=1e7, type=check_positive_float, help="Minimum energy of particles (eV)")
    parser.add_argument("-E", "--Emax", dest="Emax", default=1e8, type=check_positive_float, help="Maximum energy of particles (eV)")
    args = parser.parse_args()

    # Get particle parameters
    global num_particles, Emin, Emax, log_Emax, Erange
    num_particles = args.num_particles
    Emin = args.Emin
    Emax = args.Emax
    log_Emax = numpy.log10(Emax)
    Erange = numpy.log10(Emax)-numpy.log10(Emin)

    # Start a new OpenGL window
    window = glut_window()
   
    # Initialize the necessary particle information
    (np_position, np_velocity, np_zmel, gl_position, gl_color) = initial_buffers(num_particles)
   
    # Define pyopencl context and queue based on available hardware
    platform = cl.get_platforms()[0]
    dev = platform.get_devices(device_type=cl.device_type.GPU)
    context = cl.Context(properties=[(cl.context_properties.PLATFORM, platform)] + get_gl_sharing_context_properties())  
    queue = cl.CommandQueue(context)
    
    cl_velocity = cl.Buffer(context, mf.COPY_HOST_PTR, hostbuf=np_velocity)
    cl_zmel = cl.Buffer(context, mf.COPY_HOST_PTR, hostbuf=np_zmel)
    cl_start_position = cl.Buffer(context, mf.READ_ONLY | mf.COPY_HOST_PTR, hostbuf=np_position)
    cl_start_velocity = cl.Buffer(context, mf.READ_ONLY | mf.COPY_HOST_PTR, hostbuf=np_velocity)
   
    # Buffer object depends on version of PyOpenCL
    if hasattr(gl_position,'buffers'):
        cl_gl_position = cl.GLBuffer(context, mf.READ_WRITE, int(gl_position.buffers[0]))
        cl_gl_color = cl.GLBuffer(context, mf.READ_WRITE, int(gl_color.buffers[0]))
    elif hasattr(gl_position,'buffer'):
        cl_gl_position = cl.GLBuffer(context, mf.READ_WRITE, int(gl_position.buffer))
        cl_gl_color = cl.GLBuffer(context, mf.READ_WRITE, int(gl_color.buffer))
    else:
        print "Can not find a proper buffer object in pyopencl install. Exiting..."
        sys.exit()
   
    # Get OpenCL code and compile the program
    #cl_src_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'cl_src')
    f = open("%s/run_prop.cl"%cl_src_path,'r')
    fstr = "".join(f.readlines())
    program = cl.Program(context, fstr)

    try:
        program.build(options=['-I %s'%cl_src_path], cache_dir=None)
    except:
        print('Build log:')
        print(program.get_build_info(dev[0], cl.program_build_info.LOG))
        raise

    # Run the simulation
    glutMainLoop()
