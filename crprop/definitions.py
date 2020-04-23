import os

# Local directory of crprop 
CRPROP_DIR = os.path.dirname(os.path.realpath(__file__))

# Local directory containing entire repo
REPO_DIR = os.path.split(CRPROP_DIR)[0]

# Local directory containing textures
TEXTURE_DIR = os.path.join(CRPROP_DIR, 'textures')

# Local directory for saving output frames
FRAME_OUTPUT_DIR = os.path.join(CRPROP_DIR, 'frames')

# Local directory containing OpenCL source code
CL_SRC_PATH = os.path.join(CRPROP_DIR, 'cl_src')

# HAWC Observatory geocentric coordinates (in Earth radii)
HAWCX = -0.1205300654
HAWCY = -0.939836962102
HAWCZ = 0.323942291206
