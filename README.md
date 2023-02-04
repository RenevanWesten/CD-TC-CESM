# CD-TC-CESM

Mechanisms of Tropical Cyclone Response under Climate Change in the Community Earth System Model, Climate Dynamics (https://doi.org/10.1007/s00382-023-06680-3)

René M. van Westen, Henk A. Dijkstra and Nadia Bloemendaal

These directories contain Python scripts for plotting/analysing model output.

Python scripts can be found in the directory 'Program'.
Model output can be found in the directory 'Data'.

The model output are stored as NETCDF files, most output is converted to seasonally and/or yearly averages for data storage.
Only for the genesis potential indices (GPI and DGPI) and the zonally-averaged atmospheric temperature, the entire present-day and future ensemble mean is already determined. The present-day sea surface temperature biases with respect to ERA5 are also determined and interpolated onto the ERA5 grid.
