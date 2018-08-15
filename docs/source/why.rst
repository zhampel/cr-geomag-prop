.. _features:

:github_url: https://github.com/zhampel/cr-geomag-prop

***********
Why CRProp?
***********

CRProp was built out of a need for an extensible, easy to use and run
simulation package that would simulate millions of particle trajectories 
on the GPU for applications needing large statistics, as well as having the
capability to simultaneously visualize those same particles.


-------------
Main Features
-------------

The features unique to PyUnfold include:

- Built on top of the Python scientific computing stack + OpenCL kernel calls
- Support for custom, user defined magnetic fields
- Visualization of particle trajectories via PyOpenGL functionality


---------
Successes
---------

CRProp has been successfully used in several contexts, including:

- Energy-dependent cosmic-ray Moon shadow measurement made by the `HAWC observatory <https://www.hawc-observatory.org/>`_ [1]_.
- Anti-proton / proton measurement with the Moon Shadow using the `HAWC Observatory <https://hawc-observatory.org/>`_ [2]_.


.. [1] Alfaro, R. and others. 2017. "All-particle cosmic ray energy spectrum measured by the HAWC experiment from 10 to 500 TeV." *Phys. Rev. D* 96 (12):122001. `<https://doi.org/10.1103/PhysRevD.96.122001>`_.
.. [2] Alfaro, R. and others. 2018. "Constraining the anti-proton/proton ratio in TeV cosmic rays with observations of the Moon shadow by HAWC." *Phys. Rev. D* 97 (10):102005. `<https://doi.org/10.1103/PhysRevD.97.102005>`_.
