def getWindSituation(x):
    return {'1':'Other',
            '2':'Unknown',
            '3':'Calm',
            '4':'Light Breeze',
            '5':'Moderate Breeze',
            '6':'Strong Breeze',
            '7':'Gale',
            '8':'Moderate Gale',
            '9':'Strong Gale',
            '10':'Storm Winds',
            '11':'Hurricane Force Winds',
            '12':'Gusty Winds'}.get(x,'Error:Lookup')

def getIsPrecip(x):
    return {'1':'Precipitation',
            '2':'No Precipitation',
            '3':'ERROR'}.get(x,'Not Reported')

def getPrecipSituation(x):
    return {'1':'Other',
            '2':'Unknown',
            '3':'No Precipitation',
            '4':'Unidentified Slight',
            '5':'Unidentified Moderate',
            '6':'Unidentified Heavy',
            '7':'Snow Slight',
            '8':'Snow Moderate',
            '9':'Snow Heavy',
            '10':'Rain Slight',
            '11':'Rain Moderate',
            '12':'Rain Heavy',
            '13':'Frozen Precipitation Slight',
            '14':'Frozen Precipitation Moderate',
            '15':'Frozen Precipitation Heavy'}.get(x,'Error:Lookup')

def getVisibilitySituation(x):
    return {'1':'Other',
            '2':'Unknown',
            '3':'Clear',
            '4':'Fog Not Patchy',
            '5':'Patchy Fog',
            '6':'Blowing Snow',
            '7':'Smoke',
            '8':'Sea Spray',
            '9':'Vehicle Spray',
            '10':'Blowing Dust or Sand',
            '11':'Sun Glare',
            '12':'Swarms of Insects'}.get(x,x)

def getPavementType(x):
    return {'1':'Other',
            '2':'Unknown',
            '3':'Asphalt',
            '4':'Open Graded Asphalt',
            '5':'Concrete',
            '6':'Steel Bridge',
            '7':'Concrete Bridge',
            '8':'Asphalt Overlay Bridge',
            '9':'Timber Bridge'}.get(x,'Error:Lookup')

def getPavementSensorType(x):
    return {'1':'Other',
            '2':'Contact Passive',
            '3':'Contact Active',
            '4':'Infrared',
            '5':'Radar',
            '6':'Vibrating',
            '7':'Microwave'}.get(x,'Error:Lookup')

def getPavementSensorError(x):
    return {'1':'Other',
            '2':'none',
            '3':'noResponse',
            '4':'cutCable',
            '5':'shortCircuit',
            '6':'dirtyLens'}.get(x,'Error:Lookup')
            
def getSurfaceStatus(x):
    return {'1':'Other',
            '2':'ERROR',
            '3':'Dry',
            '4':'Trace Moisture',
            '5':'Wet',
            '6':'Chemical Wet',
            '7':'Ice Warning',
            '8':'Ice Watch',
            '9':'Snow Warning',
            '10':'Snow Watch',
            '11':'Absorption',
            '12':'Dew',
            '13':'Frost',
            '14':'Absorption at Dewpoint'}.get(x,'Error:Lookup')

def getBlackIceSignal(x):
     return {'1':'Other',
             '2':'No Ice',
             '3':'Black Ice',
             '4':'Detector Error'}.get(x,'Error:Lookup')

def getSubSurfaceType(x):
    return {'1':'Other',
            '2':'Unknown',
            '3':'Concrete',
            '4':'Asphalt',
            '5':'Open Graded Asphalt',
            '6':'Gravel',
            '7':'Clay',
            '8':'Loam',
            '9':'Sand',
            '10':'Permafrost',
            '11':'Various Aggregates',
            '12':'Air'}.get(x,'Error:Lookup')
