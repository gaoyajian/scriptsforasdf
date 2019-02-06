### here first to check the existence of the focal mechanism event file in the NDK directory,
###  if existence, mostly useful for the waveforms inversion,if not,download the event quakeml from
###  iris without focal mechanism. Then download the data from IRIS and GFZ, and before run, should 
###  update the username and password for the restricted data.
###  http://geofon.gfz-potsdam.de/waveform/archive/auth/auth-example.php
###  wget --post-file /data2/yjgao/token.asc https://geofon.gfz-potsdam.de/fdsnws/dataselect/1/auth -O cred.txt
###  Yajian Gao, 2017,12,26,GFZ

from obspy import read_events
from obspy.clients.fdsn import Client
from obspy import UTCDateTime
import os
import sys
import datetime
import obspy
from pathlib import Path
import os.path
from obspy.clients.fdsn.mass_downloader import CircularDomain, \
    Restrictions, MassDownloader
from obspy.clients.seedlink.easyseedlink import create_client
#def handle_data(trace):
    #print('Received the following trace:')
    #print(trace)
    #print()
#client = create_client('geofon.gfz-potsdam.de', on_data=handle_data)
client = Client("IRIS")
if len(sys.argv) != 8:
	sys.exit("Usage: python %s year month day hour:minute:seconds eventid evla evlo"% sys.argv[0])
year,month,day,origin,eventid,evla,evlo = sys.argv[1:]
hour,minute,second=origin.split(':')
#############################################download quakeml from IRIS without FOCAL MECHANISM

EVENTFILENAME='C'+str(year)+str(month)+str(day)+str(hour)+str(minute)+'A.ndk'
PATH="../NDK/"+str(EVENTFILENAME)
print(PATH)
ts=os.path.exists(PATH)
if ts== True:
	print(ts)
	cat = obspy.read_events("NDK/"+str(EVENTFILENAME))
	print(cat)
	cat.write(eventid+".ml", format="quakeml")  
else:   
        print(ts)
        cat = client.get_events(eventid=eventid)
        cat.write(eventid+'.ml',format="quakeml") 

############################################# download seismograms
origin_time = obspy.UTCDateTime(int(year), int(month), int(day), int(hour), int(minute), int(second))
# Circular domain around the epicenter. This will download all data between
# 70 and 90 degrees distance from the epicenter. This module also offers
# rectangular and global domains. More complex domains can be defined by
# inheriting from the Domain class.
domain = CircularDomain(latitude=evla, longitude=evlo,
                        minradius=0.0, maxradius=10.0)

restrictions = Restrictions(
    # Get data from 5 minutes before the event to one hour after the
    # event. This defines the temporal bounds of the waveform data.
    starttime=origin_time - 1 * 60,
    endtime=origin_time + 600,
    # You might not want to deal with gaps in the data. If this setting is
    # True, any trace with a gap/overlap will be discarded.
    reject_channels_with_gaps=True,
    # And you might only want waveforms that have data for at least 95 % of
    # the requested time span. Any trace that is shorter than 95 % of the
    # desired total duration will be discarded.
    minimum_length=0.95,
    # No two stations should be closer than 10 km to each other. This is
    # useful to for example filter out stations that are part of different
    # networks but at the same physical station. Settings this option to
    # zero or None will disable that filtering.
    minimum_interstation_distance_in_m=10E3,
    # Only HH or BH channels. If a station has HH channels, those will be
    # downloaded, otherwise the BH. Nothing will be downloaded if it has
    # neither. You can add more/less patterns if you like.
    channel_priorities=["HH[ZNE]", "BH[ZNE]"],
    # Location codes are arbitrary and there is no rule as to which
    # location is best. Same logic as for the previous setting.
    #location_priorities=["", "00", "10"]
	)

# No specified providers will result in all known ones being queried.
#client_gfz = Client("GFZ", user="-dnzc9DIzdWl-vMoejGxuWJJ",password="cEz8RjjmQBI0oMVR")
#-dnzc9DIzdWl-vMoejGxuWJJ
#-dnzc9DIzdWl-vMoejGxuWJJ:PVy8f6Xt-vXyV5vu
client_gfz = Client("GFZ", user="ToBMNtKepB0Rusv7UVlR57q2",password="8VPDbbzIxYSzfUhj")
#client_eth = Client("ETH", user="from_me", password="to_you")
mdl = MassDownloader(providers=[client_gfz,"IRIS"])
# The data will be downloaded to the ``./waveforms/`` and ``./stations/``
# folders with automatically chosen file names.
mdl.download(domain, restrictions, mseed_storage=eventid+"/waveforms",
             stationxml_storage=eventid+"/stations")

###############################################transform the mseed into asdf using the pyasdf
import glob
import os
import pyasdf

if ts== True:
	ds = pyasdf.ASDFDataSet("WITHFOCAL/"+eventid+".h5", compression="gzip-3")
	ds.add_quakeml(eventid+".ml")
	event = ds.events[0]
	files = glob.glob(eventid+"/waveforms/*.mseed")
	for _i, filename in enumerate(files):
	    	   print("Adding file %i of %i ..." % (_i + 1, len(files)))
	    	   ds.add_waveforms(filename, tag="raw_recording", event_id=event)
	print(ds)


	files = glob.glob(eventid+"/stations/*.xml")
	for _i, filename in enumerate(files):
		print("Adding file %i of %i ..." % (_i + 1, len(files)))
		ds.add_stationxml(filename)
	print(ds)
else:
        ds = pyasdf.ASDFDataSet("WITHOUTFOCAL/"+eventid+".h5", compression="gzip-3")
        ds.add_quakeml(eventid+".ml")
        event = ds.events[0]
        files = glob.glob(eventid+"/waveforms/*.mseed")
        for _i, filename in enumerate(files):
              print("Adding file %i of %i ..." % (_i + 1, len(files)))
              ds.add_waveforms(filename, tag="raw_recording", event_id=event)
        print(ds)
        files = glob.glob(eventid+"/stations/*.xml")
        for _i, filename in enumerate(files):
              print("Adding file %i of %i ..." % (_i + 1, len(files)))
              ds.add_stationxml(filename)
        print(ds)



