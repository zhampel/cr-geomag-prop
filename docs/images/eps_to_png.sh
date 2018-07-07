#!/bin/bash 

for f in `ls *.eps`; do
     convert -density 500 $f -flatten ${f%.*}.png;
done
