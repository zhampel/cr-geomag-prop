from __future__ import absolute_import

try:
    import os
    import sys
    import numpy as np
    import argparse
    import yaml
    from definitions import *
    from particle_utils import *
    from extras import printText, printHelp
    from opengl_utils import *
    #load_texture, axis, threeAxis, mouse, motion

    from PIL import Image

    import pyopencl as cl # OpenCL - GPU computing interface
    from pyopencl.tools import get_gl_sharing_context_properties
    from OpenGL.GL import * # OpenGL - GPU rendering interface
    from OpenGL.GLU import * # OpenGL tools (mipmaps, NURBS, perspective projection, shapes)
    from OpenGL.GLUT import * # OpenGL tool to make a visualization window
    from OpenGL.arrays import vbo

except ImportError as e:
    print(e)
    raise ImportError

# PyOpenCL memory flags
mf = cl.mem_flags

np.set_printoptions(threshold=sys.maxsize)

# Boolean to draw a textured Earth
drawTexturedEarth = True
texture_file = os.path.join(TEXTURE_DIR, 'earthmap1k.jpg')

# Path to output frame pngs
frame_prefix = os.path.join(FRAME_OUTPUT_DIR, 'particle')

# Whether to save frames to pngs
save_frames = False
frame = 0

# Continuously rotate perspective
rotate_perspective = False

# Dictionary for choosing EOM integrators
eom_dict = {'euler'    : 1,
            'rk4'      : 2,
            'boris'    : 3,
            'adaboris' : 4}


# Dictionary for grabbing available devices
deviceDict = {'gpu' : cl.device_type.GPU,
              'cpu' : cl.device_type.CPU}

# Define pyopencl context and queue based on available hardware
def init_device(cpu_device=False):
    # Find a device... default is for GPU
    device_type_name = 'gpu'
    if cpu_device:
        device_type_name = 'cpu'

    # Grab OpenCL device calls
    device_type = deviceDict[device_type_name]

    print('\n============== Grabbing Compute Resources =============\n')
    platform = cl.get_platforms()[0]
    print('\t\tPlatform: %s'%platform)
    device = platform.get_devices(device_type=device_type)
    print('\t\tDevice: %s'%device[0])
    print('\n=======================================================\n')
    context = cl.Context(devices=device,
                         properties=[(cl.context_properties.PLATFORM, platform)] + get_gl_sharing_context_properties())
    return device, context

def glut_window():

    global initRun

    printHelp()

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


def on_key(*args):
    global drawTexturedEarth
    global drawInfoMessage
    global rotate_perspective
    global width, height, isBigDisplay
    global save_frames, time_step, time_pause_var, run_options

    # Pause and restart
    if args[0] == b' ' or args[0] == b'p':
        time_step = time_pause_var-time_step
        run_options[0] = time_step

    # Speed up by 10 percent
    if args[0] == b'+':
        time_step += 0.1*time_step
        time_pause_var = time_step
        run_options[0] = time_step

    # Slow down by 10 percent
    if args[0] == b'-':
        time_step -= 0.1*time_step
        time_pause_var = time_step
        run_options[0] = time_step

    # Rotate vieweing perspective
    if args[0] == b'r':
        rotate_perspective = not rotate_perspective

    # Save frames to file
    if args[0] == b's':
        save_frames = not save_frames
        if not os.path.exists(FRAME_OUTPUT_DIR):
            os.makedirs(FRAME_OUTPUT_DIR)

    # Toggle textured Earth and simple sphere
    if args[0] == b't':
        drawTexturedEarth = not drawTexturedEarth
    
    # Toggle printing info message on screen
    if args[0] == b'i':
        drawInfoMessage = not drawInfoMessage
    
    # Quickly toggle large and small display sizes
    if args[0] == b'b':
        if isBigDisplay:
            width /= display_scale_factor
            height /= display_scale_factor
        else:
            width *= display_scale_factor
            height *= display_scale_factor
        isBigDisplay = not isBigDisplay

    # Exit program
    if args[0] == b'\033' or args[0] == b'q':
        sys.exit()


def on_display():

    # Rotate camera
    if rotate_perspective:
        dx = 0.3
        rotate['z'] += dx

    """Render the particles"""
    # Update or particle positions by calling the OpenCL kernel
    cl.enqueue_acquire_gl_objects(queue, [cl_gl_position, cl_gl_color])

    kernelargs = (cl_gl_position, cl_gl_color, cl_velocity, cl_zmel,
                  cl_start_position, cl_start_velocity,
                  run_options)
                  #np.float32(log_Emax), np.float32(Erange), np.float32(time_step))

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

    if (drawTexturedEarth):
        # Draw Earth
        global texture
        glDepthMask(GL_FALSE)

        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        glColor4f(1.0,1.0,1.0,1.0)
        #glColor4f(1.0,1.0,1.0,0.75)
        quad = gluNewQuadric()

        glPushMatrix()

        # Only front of sphere appears
        glEnable(GL_CULL_FACE)
        glCullFace(GL_BACK)

        # Bind texture to quadric
        glEnable(GL_TEXTURE_2D)
        glBindTexture(GL_TEXTURE_2D, texture)
        gluQuadricTexture(quad, True)

        # Rotate Earth to align with HAWC longitude
        e_rot = 180./np.pi*np.arctan(HAWCY/HAWCX)
        glRotated(e_rot, 0.0, 0.0, 1.0)

        # Define sphere as quadric surface
        gluSphere(quad, 1.0, 100, 100)

        glDisable(GL_BLEND)
        glDisable(GL_CULL_FACE)
        glDepthMask(GL_TRUE)

        glPopMatrix()


    else:
        # Draw a blue sphere
        # Draw xyz axes
        threeAxis(1.5)
        # Draw Transparent Earth
        glEnable(GL_BLEND)
        glColor4f(0.0, 0.0, 1.0, 0.15)
        glutSolidSphere(1.0, 32, 32)
        glDisable(GL_BLEND)

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

    # Info message on screen
    textx = 0.05
    texty = 0.99
    texty_delta = 0.0115
    if drawInfoMessage:
        for lineno in range(21):
            texty -= texty_delta
            glut_print(printText(lineno=lineno), textx, texty)

    glutSwapBuffers()

    # Inspired by the 'render.py` script from 
    # https://groups.google.com/forum/#!topic/pygame-mirror-on-google-groups/qdFuQh8RY4g
    # NOTE: the GL_RGB / GL_RGBA difference
    if save_frames:
        global frame
        png_file_write(frame_prefix, frame, glReadPixels( 0,0, w, h, GL_RGBA, GL_UNSIGNED_BYTE))
        frame += 1


#######################################################################################

# write a png file from GL framebuffer data

def png_file_write(name, number, data):
    im = Image.frombuffer("RGBA", (720,576), data, "raw", "RGBA", 0, 0)
    fnumber = "%05d" % number
    im.save(name + fnumber + ".png")

######################################################################################

#-----
# MAIN
#-----
if __name__=="__main__":

    global args
    p = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter,
                                description=("Launch a simulation of particles "
                                             "propagating in the geomagnetic field."))
    p.add_argument("-p", "--particle", dest="particle_type", default="proton",
                   help=("Particle species type. Options: proton, helium, "
                         "carbon, oxygen, neon, magnesium, silicon, iron."))
    p.add_argument("-n", "--num_particles", dest="num_particles", default=1000,
                   type=check_positive_int,
                   help="Number of particles to simulate.")
    p.add_argument("-e", "--energy_lims", dest="energy_lims", nargs=2,
                   default=[1e7, 1e8], type=check_positive_float,
                   help="Minimum and maximum energy of particles (eV). ")
    p.add_argument("-a", "--alpha", dest="alpha", type=check_positive_float,
                   help=("Optional energy spectral index. "
                         "If given, weight the energy distribution of events by E^-alpha."))
    p.add_argument("--lat_lon_alt", dest="lat_lon_alt",
                   nargs=3, type=float, default=[18.99, -97.308, 3],
                   help=("Geodetic latitude of starting particle position in degrees, "
                         "Geodetic longitude of starting particle position in degrees, "
                         "Height of starting particle position in Earth radii where 1 is ground level."))
    p.add_argument("-s", "--eom_step", dest="eom_step", default="boris",
                   help=("Stepper function to integrate equations of motion. "
                         "Options: boris, adaboris, euler, rk4."))
    p.add_argument("-d", "--cpu", dest="device", help='Flag to run on CPU', action='store_true')

    # Use of a config file for all options 
    config_parse = p.add_mutually_exclusive_group()
    config_parse.add_argument("-c", "--config", dest="config_file", default='crprop/config.yml', help="Path to yaml configuration file")

    args = p.parse_args()
    args_dict = vars(args)

    # If no specified input, use default config file
    if not any((args.particle_type, 
                args.num_particles,
                args.energy_lims, 
                args.alpha, 
                args.lat_lon_alt, 
                args.eom_step,
                args.device)):
        config_file = args.config_file
        with open(config_file, 'r') as ymlfile:
            cfg = yaml.load(ymlfile)

        for arg in cfg["args"]:
            if arg not in args_dict:
                raise ValueError(("'{}' specified in the config file "
                                  "is an invalid argument!".format(arg)))
            else:
                args_dict[arg] = cfg["args"][arg]

    # Get particle parameters
    global particle_type, num_particles, Emin, Emax, log_Emax, Erange, run_options
    cpu_device_flag = args.device
    particle_type = args.particle_type
    num_particles = args.num_particles
    Emin = args.energy_lims[0]
    Emax = args.energy_lims[1]
    log_Emax = np.log10(Emax)
    Erange = np.log10(Emax)-np.log10(Emin)
    eom_integrator = eom_dict[args.eom_step.lower()]

    lat = args.lat_lon_alt[0]
    lon = args.lat_lon_alt[1]
    alt = args.lat_lon_alt[2]

    run_options = np.array([time_step, log_Emax, Erange, eom_integrator], dtype=np.float32)

    # Start a new OpenGL window
    window = glut_window()

    # Preload texture once
    texture = load_texture(texture_file)

    # Initialize the necessary particle information
    (np_position, np_velocity, np_zmel) = initial_buffers(particle_type, num_particles, Emin, Emax, alpha=args.alpha,
                                                          lat=lat, lon=lon, height=alt)

    # Arrays for OpenGL bindings
    gl_position = vbo.VBO(data=np_position, usage=GL_DYNAMIC_DRAW, target=GL_ARRAY_BUFFER)
    gl_position.bind()
    np_color = np.ndarray((num_particles, 4), dtype=np.float32)
    gl_color = vbo.VBO(data=np_color, usage=GL_DYNAMIC_DRAW, target=GL_ARRAY_BUFFER)
    gl_color.bind()

    # Define pyopencl context and queue based on available hardware
    #platform = cl.get_platforms()[0]
    #dev = platform.get_devices(device_type=cl.device_type.GPU)
    #context = cl.Context(properties=[(cl.context_properties.PLATFORM, platform)] + get_gl_sharing_context_properties())
    dev, context = init_device(cpu_device=cpu_device_flag)
    queue = cl.CommandQueue(context)

    cl_velocity = cl.Buffer(context, mf.COPY_HOST_PTR, hostbuf=np_velocity)
    cl_zmel = cl.Buffer(context, mf.COPY_HOST_PTR, hostbuf=np_zmel)
    cl_start_position = cl.Buffer(context, mf.READ_ONLY | mf.COPY_HOST_PTR, hostbuf=np_position)
    cl_start_velocity = cl.Buffer(context, mf.READ_ONLY | mf.COPY_HOST_PTR, hostbuf=np_velocity)

    # Buffer object depends on version of PyOpenCL
    if hasattr(gl_position, 'buffers'):
        cl_gl_position = cl.GLBuffer(context, mf.READ_WRITE, int(gl_position.buffers[0]))
        cl_gl_color = cl.GLBuffer(context, mf.READ_WRITE, int(gl_color.buffers[0]))
    elif hasattr(gl_position, 'buffer'):
        cl_gl_position = cl.GLBuffer(context, mf.READ_WRITE, int(gl_position.buffer))
        cl_gl_color = cl.GLBuffer(context, mf.READ_WRITE, int(gl_color.buffer))
    else:
        print("Can not find a proper buffer object in pyopencl install. Exiting...")
        sys.exit()

    # Get OpenCL code and compile the program
    cl_src_code = os.path.join(CL_SRC_PATH, 'run_prop.cl')
    f = open(cl_src_code, 'r')
    fstr = "".join(f.readlines())
    program = cl.Program(context, fstr)

    opts_string = "-I %s"%CL_SRC_PATH
    try:
        program.build(options=opts_string, cache_dir=None)
    except:
        print('Build log:')
        print(program.get_build_info(dev[0], cl.program_build_info.LOG))
        raise

    # Run the simulation
    glutMainLoop()
