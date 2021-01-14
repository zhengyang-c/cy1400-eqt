# stuff

- use obspy because pysmo has scipy compatibility issues so it just has to go
- use obspy to load sac file
- obspy trim function, which is nonconservative. neater would be to load whole data set and use python array indexing


- can currently plot with the time series + characteristic function
- the triggering requires thresholds, but calculation of the CF does not
- so just plot like all the different CFs to compare


atm it's 1s sta, 10s lta

----

# cfs 

recursive_sta_lta(a, nsta, nlta)    Recursive STA/LTA.

carl_sta_trig(a, nsta, nlta, ratio, quiet)  Computes the carlSTAtrig characteristic function.

classic_sta_lta(a, nsta, nlta)  Computes the standard STA/LTA from a given input array a. The length of

delayed_sta_lta(a, nsta, nlta)  Delayed STA/LTA.

z_detect(a, nsta)   Z-detector. this is the Z-test (standard deviations from the mean)

papers seesm to recommend DECIMATING THE DATA I.E. SAMPLING IT AT A LOWER RATE
which makes sense it removes the higher frequency stuff 

pk_baer(reltrc, samp_int, tdownmax, ...[, ...])     Wrapper for P-picker routine by M. Baer, Schweizer Erdbebendienst.

ar_pick(a, b, c, samp_rate, f1, f2, lta_p, ...)     Pick P and S arrivals with an AR-AIC + STA/LTA algorithm.

----



# carl sta trig:

last two arguments ratio and quiet. as each number gets smaller, the CF gets more sensitive. 1 and 1 for each to try


----

## plotting all picks 

using only 300 seconds, make picks (300 - 600s) using threshold of 3.0 and 1.5 (on trigger and off trigger)


if we throw away the off-triggers it should make life easier for me 

now it can plot 10s before and 30s after the pick with a nice red line + output ascii file 

---

# improving the cf by exponentiating

(1) square the classic sta/lta (or higher powers)

going by eye, power 3 looks ok

(2) square the recursive sta/lta (or higher powers)

**also, how does the recursive sta/lta work lol**


btw delayed looks very bad so let's just not use it
    
# changing the time windows

try:

current: 1/10
to try:
0.5 / 5
2 / 20

1 / 5
0.1 / 5


one day i'll put this all on a massive jupyter notebook

# trying pk_baer 

pk_baer(reltrc, samp_int, tdownmax, tupevent, thr1, thr2, preset_len, p_dur, return_cf=False)[source]

looks similar to the PhasePApy tbh

actually no

also it just doesn't seem to pick anything

so i can just move on i guess

# use PhasePApy picker lol

- kurtosis
PhasePApy outputs in UTC uhhh so i'll have to convert 
oh no i'll just take the UTC of when the date time starts and convert accordingly 

PhasePApy uses ```UTCDateTime``` objects from obspy 
which work similarly to datetime objects in python

i should find a way to plot the pick times 


1) can now plot all pick times in one plot, separate plot files with .txt files
2) all 3 pick algorithms seem to differ on the number of picks
3) and i have no idea why
4) which is a good thing but idk what are actually signals so o o o

# output in txt file no. of picks 

uhh
is this why they use a sql database oh my god 
so you can organise the data properly

ok i added a .txt logging thing 

i can use wc -l to count the number of picks if needed 

but it's not logging for obspy yet because it doesn't have the same uh
well
output
but it's good enough

# apply detection to full day / count number of detections for each detection method

not enough ram lol do this on the HPC kekW


# syncing onedrive wtf (friday)

just use gui over the weblol


## 10/1/2021

also i moved all the functions to a helper file because it was getting long and difficult to manage


# applying eqt (sunday) 

- either need hdf5 format
- or miniseed

and miniseed is easier (because i can just export)

no clue what the stations.json is supposed to be????
so i guess i'm using hdf5

tf is the json file i'll have to read the code wtf

need station coordinates for the json file but otherwise it's quite simple
i spoke too soon


```
file_list = [join(station, ev) for ev in listdir(station) if ev.split('/')[-1] != '.DS_Store'];
        print(file_list)
        mon = [ev.split('__')[1]+'__'+ev.split('__')[2] for ev in file_list ];


```


it can't seem to read the files in properly
it seems to expect __ like wtf

and the sample download fn is not even downloading anything

'''
 *** Finished the prediction in: 0 hours and 10 minutes and 25.69 seconds.
 *** Detected: 19 events.
 *** Wrote the results into --> " /mnt/c/Users/Zheng Yang/aceh/detections/TA01_outputs "
'''


i just renamed the dots to __ such that it's

```
NET__STA__CHA.mseed
```

probably want to check:
(1) what is the CF values for the eqtransformer detections
(2) what happens when you use all three channels with eqtransformer





# what even is recursive sta/lta (friday)

# generate and plot own spectrogram




# writing own classic sta/lta (saturday)


# coincidence across streams (saturday)

https://docs.obspy.org/packages/autogen/obspy.signal.trigger.coincidence_trigger.html#obspy.signal.trigger.coincidence_trigger

# trying the P and S pickers hm (saturday)

- plot with E and N channels side by side
- load into same stream and run the AICpicker



need HPC support to fix something 