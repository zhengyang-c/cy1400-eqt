- fix the distance calculation h m m 
- modify gridsearch s.t
- for each grid cell, do a rotation of the N and E components of the waveform, find the position that minimises the T (transverse) component energy, for one station

- misfit from travel time, misfit due to energy uncertainty, need to weight between the

- use travel time to do gridsearch, use that to normalise travel time error

- then, do a grid search using the rotation, use that to normalise the contribution from the energy errors

- the total error 

- first step: get misfit of arrival times
- use the region of less than < 0.5 s misfit 

- filtering is going to matter re: the waveforms

- arrival time picks seem more robust, only use some grid points to test the energy
 

rotation only cares about the horizontal locations 
need travel times to constrain depth 



TODO:
- "fix" the travel time grid search
- then incorporate the rotation method as a way to pin down the location 

seems that hypoDD output is reliable

want to generate my own travel time model instead of loading from ak135 or other global models, preferably using 


organise these s.t. they are organised as tests 


first use travel time to find probable locations
even if there are symmetric parts due to having a linear array, if i add a term due to rotating the waveforms to R and T components, there should be a bias towards one of the minimums 

i.e. want to have some asymmetric error 

determine the station gap, could only use rotation method for large station gaps 
station gap: maximum azimuthal gap 

so you don't have to use the rotation method for everything 

travel time table: travel.pl script 


rotation method: only cares about the horizontal direction / azimuth 

plot 2d map view at best depth
define some error function from the rotation

and then find some way to combine both of the error functions 

minimally at least have a better travel time grid search

rotation method has to do with the 3d velocity model so maybe it's a bit less obvious 

for filtering vis a vis frequency, need to test multiple frequency ranges e.g. 1-5, 1-10, etc etc etc

to compare energy 

might not need to remove instrument response 



https://docs.obspy.org/master/packages/autogen/obspy.geodetics.base.degrees2kilometers.html#obspy.geodetics.base.degrees2kilometers
h m m m m
https://docs.obspy.org/master/packages/autogen/obspy.geodetics.base.gps2dist_azimuth.html#obspy.geodetics.base.gps2dist_azimuth




