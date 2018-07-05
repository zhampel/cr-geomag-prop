#!/bin/bash 

ffmpeg -framerate 70 -i frames/particles0%04d.png -c:v libx264 -r 60 -pix_fmt yuv420p movie.mp4
