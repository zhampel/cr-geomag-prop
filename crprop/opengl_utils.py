from __future__ import absolute_import

try:
    import sys
    import pygame
    from pygame.locals import *
    
    from OpenGL.GL import * # OpenGL - GPU rendering interface
    from OpenGL.GLU import * # OpenGL tools (mipmaps, NURBS, perspective projection, shapes)
    from OpenGL.GLUT import * # OpenGL tool to make a visualization window
    from OpenGL.arrays import vbo

except ImportError as e:
    print(e)
    raise ImportError


# OpenGL window dimensions and initial perspective
width = 720
height = 576
zoom = 60.
display_scale_factor = 2 # must be integer
isBigDisplay = False

# Boolean for printing info message
drawInfoMessage = True

# Mouse functionality
outer_radius = 10.501
mouse_down = False
mouse_old = {'x': 0., 'y': 0.}
rotate = {'x': -55., 'y': 0., 'z': 45.}
translate = {'x': 0., 'y': 0., 'z': 0.}
initial_translate = {'x': 0., 'y': 0., 'z': -outer_radius}

# Set the time step and pause functionality
time_step = 0.0005
time_pause_var = time_step

# Set initial step to 0 to start paused
time_step = 0


# Timer update function
def on_timer(t):
    glutTimerFunc(t, on_timer, t)
    glutPostRedisplay()


# Print to window screen
def glut_print(text, x, y):

    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluOrtho2D(0.0, 1.0, 0.0, 1.0)
    glMatrixMode(GL_MODELVIEW)

    glColor3f(1, 1, 1)
    glRasterPos2f(x, y)
    for ch in text:
        glutBitmapCharacter(OpenGL.GLUT.GLUT_BITMAP_HELVETICA_10, ctypes.c_int(ord(ch)))
        #glutBitmapCharacter(OpenGL.GLUT.GLUT_BITMAP_TIMES_ROMAN_24, ctypes.c_int(ord(ch)))
        #glutBitmapCharacter(OpenGL.GLUT.GLUT_BITMAP_9_BY_15, ctypes.c_int(ord(ch)))



# Load a texture file to paint on sphere
def load_texture(texture_url):
    tex_id = glGenTextures(1)
    tex = pygame.image.load(texture_url)

    # Get image RGBA with flipped (True) ordering
    tex_surface = pygame.image.tostring(tex, 'RGBA', True)
    tex_width, tex_height = tex.get_size()

    glBindTexture(GL_TEXTURE_2D, tex_id)
    glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
    glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
    glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, tex_width, tex_height, 0, GL_RGBA, GL_UNSIGNED_BYTE, tex_surface)
    glBindTexture(GL_TEXTURE_2D, 0)
    return tex_id


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

