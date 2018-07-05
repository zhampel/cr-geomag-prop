# Charged Particle B-Field Propagation Visualization

This project (cr-igrf-prop) demonstrates a tool to visualize
charge particle propagation through the Earth's magnetic field.
The following [link](https://www.youtube.com/watch?v=M-hRWb5rqL8&feature=youtu.be)
shows a demonstration of this project's visualization of proton particles 
interacting with the geomagnetic field.

To check-out the repo:
`git clone https://github.com/zhampel/cr-igrf-prop.git`



## B-Field Models
There are two available models for estimating the geomagnetic field.
The first is the dipole approximation, where the axis of the field
is tilted by 11.5 deg from the Earth's axis of rotation.
The second is the International Geomagnetic Reference Field 
([IGRF](https://www.ngdc.noaa.gov/IAGA/vmod/igrf.html)).


# Usage
To get started, one simply needs to run
`python crprop/run.py`.

## Visualization
There are several available options when running the simulation.
To start/pause the propagation, use the `p` key or the spacebar.
To stop the rotation of the perspective, use the `r` key.
To save the frames to png files, use the `s` key.
Finally, to quit the simulation, use the `q` or `Esc` key.

A BASH script named `crprop/make_mp4.sh` is provided to generate 
an mp4 movie if saved frames are present in the `frames` directory.
One must have ffmpeg installed on the system to make the movie.


## Installation of Installation
The installation of the required packages can be a little bit tricky
depending on the platform.
For Linux machines, `pip install -r requirements.txt` should be enough
to get started.
However, on Macs the process can be a bit more involved.
More to be added soon...
