# Charged Particle in Geomagnetic Field Visualization

This project (cr-geomag-prop) demonstrates a tool to visualize charge particle 
propagation through the Earth's magnetic field using PyOpenCL and PyOpenGL.
The following [link](https://www.youtube.com/watch?v=M-hRWb5rqL8&feature=youtu.be)
shows a demonstration of this project's visualization of proton particles 
interacting with the geomagnetic field.

To check-out the repo:
```
git clone https://github.com/zhampel/cr-geomag-prop.git
```



## B-Field Models
There are two available models for estimating the geomagnetic field.
The first is the dipole approximation, where the axis of the field
is tilted by 11.5 deg from the Earth's axis of rotation.
The second is the International Geomagnetic Reference Field 
([IGRF](https://www.ngdc.noaa.gov/IAGA/vmod/igrf.html)).


# Usage
Upon installation of required dependencies, one simply needs to run
```
python crprop/run.py -n 1000 -e 1e7 -E 1e8
```
to start the simulation, where the number of particles to simulate is given by `-n`,
and the minimum and maximum particle energy in electronvolts (eV) are given by `-e` 
and `-E`, respectively.
The values shown in the line above are the defaults, thus users can do a first run 
via `python crprop/run.py`.

## Visualization
Once the window opens, one can also use various mouse operations to change the scene.
Holding the left mouse button allows the user to move the viewing position, while 
holding down the right mouse button and moving up and down on the screen provides
a zooming operation.
The center mouse button provides translation of the origin about the screen.

The colors of the particles are representative of their energy, and are correlated
per the respective wavelengths.
Thus, red corresponds to the lowest energies, while violet represents the highest values. 
The wavelength-to-energy scaling is log-linear, thus color is proportional to the logarithm
of the energy.

There are several available user options when running the simulation:

- Start/pause the propagation using the `p` key or the spacebar
- Stop the rotation of the perspective using the `r` key
- Save the frames to png files using the `s` key
- Quit the simulation using the `q` or `Esc` key

A BASH script named `crprop/make_mp4.sh` is provided to generate 
an mp4 movie if saved frames are present in the `frames` directory.
One must have ffmpeg installed on the system to make the movie.


## Installation of Required Software
The installation of the required packages can be a little bit tricky
depending on the platform.
For Linux machines, `pip install -r requirements.txt` or `make install`
should be enough to get started.
However, on Macs the process can be a bit more involved.
More to be added soon...
