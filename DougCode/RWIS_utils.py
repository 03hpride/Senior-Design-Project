import pandas as pd
from NTCIP_tables import *
import time
from datetime import datetime, tzinfo, timedelta, timezone
import calendar
import logging

# Function to log errors that occur in processing
def logError(msg):
    logging.error(msg=msg, extra = {'UTC':datetime.now(timezone.utc).strftime('%d-%m-%Y %H:%M UTC'),
                                    'LOCAL':datetime.now().strftime('%d-%m-%Y %H:%M LOCAL')})


# Classes used in converting times and setting timezones.
class UTC(tzinfo):
    def utcoffset(self,dt):
        return timedelta(hours=0)
    def dst(self, dt):
        return timedelta(0)
    def tzname(self,dt):
        return 'UTC'
    
class PST8PDT(tzinfo):
    def utcoffset(self,dt):
        return timedelta(hours=-8)+self.dst(dt)   
    def dst(self,dt):
        return timedelta(hours=time.localtime().tm_isdst)
    def tzname(self, dt):
        return ['PST','PDT'][time.localtime().tm_isdst]

# Functions for converting measured units to human-readable units
#
# NOTE: These conversion constants should be verified according to NTCIP Standard 1204
# https://www.ntcip.org/file/2022/04/NTCIP-1204v0426b-2021_AsPublished.pdf
#
def convert_windUnits(TenthsOfMetersPerSecond):
    MPH = TenthsOfMetersPerSecond * 0.223694 
    return round(MPH, 4)

def convert_temperature(TenthsCelsius):
    fahrenheit = (TenthsCelsius*9)/50 + 32
    return round(fahrenheit, 4)

def convert_precipitationRate(TenthsOfKGperMeterSquaredPerSecond):
    InchesPerHour = TenthsOfKGperMeterSquaredPerSecond * 0.014173236
    return round(InchesPerHour, 4)

def convert_precipitationVolume(TenthsOfKGperMeterSquared):
    Inches = TenthsOfKGperMeterSquared * 0.00393701
    return round(Inches, 4)

def convert_visibility(TenthsOfMeters):
    Miles = TenthsOfMeters/16093.47089712
    return round(Miles, 4)

def convert_surfaceIceOrWaterDepth(Millimeters):
    Inches = Millimeters*0.0393701
    return round(Inches, 4)

def convert_subSurfaceDepth(Centimeters):
    Inches = Centimeters * 0.393701
    return round(Inches, 4)

def convert_atmosphericPressure(TenthsOfMillibars):
    inchesHG = TenthsOfMillibars * 0.0029528744
    return round(inchesHG, 4)

# Functions for converting a column of values, while checking for "Not Reported" and making sure the values are valid
def stationID(column, district):
    newValues = []
    for station in column.values:
        station = district + '-' + str(station).rjust(2,'0')
        newValues.append(station)
    return pd.Series(data=newValues)

# Converts a column of dates (YYYY-MM-DD) and a column of times (HH:MM:DD) 
# to UTC Epoch, Local Epoch, and to timestring (YYYY/MM/DD-HH:MM -timezone offset)
def timeFromDateTime(recordDate, recordTime):
    localstring = []
    utc = []
    local = []
    for i in range(len(recordDate)):
        thing = datetime.strftime(datetime.strptime(recordDate.values[i]+recordTime.values[i],'%Y-%m-%d%H:%M:%S'), '%Y%m%d%H%M')
        pacificdate = datetime.strptime(str(thing), '%Y%m%d%H%M').replace(tzinfo=PST8PDT()).astimezone(UTC()).strftime('%Y%m%d%H%M')

        utc.append(calendar.timegm(datetime.strptime(str(pacificdate), '%Y%m%d%H%M').replace(tzinfo=UTC()).timetuple()))
        local.append(calendar.timegm(datetime.strptime(str(pacificdate),'%Y%m%d%H%M').replace(tzinfo=UTC()).astimezone(PST8PDT()).timetuple()))
        localstring.append(datetime.strftime(datetime.strptime(pacificdate,'%Y%m%d%H%M').replace(tzinfo=UTC()).astimezone(PST8PDT()), '%Y/%m/%d-%H:%M %z'))

    return pd.Series(localstring), pd.Series(utc), pd.Series(local)

# Converts a column of Epoch times to UTC Epoch, Local Epoch, and to timestring (YYYY/MM/DD-HH:MM -timezone offset)
def timeFromEpoch(recordEpoch):
    base = []
    for value in recordEpoch.values:
        try:
            base.append(datetime.fromtimestamp(float(value), timezone.utc).strftime('%Y%m%d%H%M'))
        except:
            base.append(value)
    
    utc = []
    local = []
    localstring = []
    for i in range(len(recordEpoch)):
        if ((base[i] != 'Not Reported') and (base[i] != '0')):
            utc.append(calendar.timegm(datetime.strptime(str(base[i]), '%Y%m%d%H%M').replace(tzinfo=UTC()).timetuple()))
            local.append(calendar.timegm(datetime.strptime(str(base[i]), '%Y%m%d%H%M').replace(tzinfo=UTC()).astimezone(PST8PDT()).timetuple()))
            localstring.append(datetime.strftime(datetime.strptime(str(base[i]),'%Y%m%d%H%M').replace(tzinfo=UTC()).astimezone(PST8PDT()), '%Y/%m/%d-%H:%M %z'))
        else:
            if (base[i] == 'Not Reported'):
                utc.append('Not Reported')
                local.append('Not Reported')
                localstring.append('Not Reported')
            else:
                utc.append('Error:NTCIP')
                local.append('Error:NTCIP')
                localstring.append('Error:NTCIP')

    return pd.Series(localstring), pd.Series(utc), pd.Series(local)

# Functions that perform conversions for an entire column
# Primarily utilizes conversion functions above and NTCIP tables
def essAtmosphericPressure(column):
    for index, value in column.items():
        if value != 'Not Reported':
            if (int(value) >= 0) and (int(value) < 65535):
                column.iat[index] = convert_atmosphericPressure(int(value))
            else:
                column.iat[index] = 'Error:NTCIP'
    return column

def windSpeed(column):
    for index, value in column.items():
        if value != 'Not Reported':
            if (int(value) >= 0 and int(value) < 361):
                column.iat[index] = convert_windUnits(int(value))
            else:
                column.iat[index] = 'Error:NTCIP'
    return column

def windDir(column):
    for index, value in column.items():
        if value != 'Not Reported':
            if (int(value) >= 0 and int(value) < 361):
                column.iat[index] = float(value)
            else:
                column.iat[index] = 'Error:NTCIP'
    return column

def essTemperature(column):
    for index, value in column.items():
        if value != 'Not Reported':
            if (int(value) >= -1000 and int(value) < 1001):
                column.iat[index] = convert_temperature(int(value))
            else:
                column.iat[index] = 'Error:NTCIP'
    return column

def essRelativeHumidity(column):
    for index, value in column.items():
        if value != 'Not Reported':
            if (int(value) >= 0 and int(value) < 101):
                column.iat[index] = float(value)
            else:
                column.iat[index] = 'Error:NTCIP'
    return column

def essPrecipYesNo(column):
    for index, value in column.items():
        column.iat[index] = getIsPrecip(value)
    return column

def essPrecipRate(column):
    for index, value in column.items():
        if value != 'Not Reported':
            if (int(value) >= 0 and int(value) < 65535):
                column.iat[index] = convert_precipitationRate(int(value))
            else:
                column.iat[index] = 'Error:NTCIP'
    return column

def essPrecipSituation(column):
    for index, value in column.items():
        column.iat[index] = getPrecipSituation(value)
    return column

def precipitationAccumulation(column):
    for index, value in column.items():
        if value != 'Not Reported':
            if (int(value) >= 0 and int(value) < 65535):
                column.iat[index] = convert_precipitationVolume(int(value))
            else:
                column.iat[index] = 'Error:NTCIP'
    return column

def essVisibility(column):
    for index, value in column.items():
        if value != 'Not Reported':
            if (int(value) >= 0 and int(value) < 1000001):
                column.iat[index] = convert_visibility(int(value))
            else:
                column.iat[index] = 'Error:NTCIP'
    return column

def essVisibilitySituation(column):
    for index, value in column.items():
        if value != 'Not Reported':
            column.iat[index] = getVisibilitySituation(value)
    return column

def essPavementSensorIndex(column):
    return column

def essPavementType(column):
    for index, value in column.items():
        column.iat[index] = getPavementType(value)
    return column

def essPavementSensorType(column):
    for index, value in column.items():
        column.iat[index] = getPavementSensorType(value)
    return column

def essSurfaceStatus(column):
    for index, value in column.items():
        column.iat[index] = getSurfaceStatus(value)
    return column

def essSurfaceIceOrWaterDepth(column):
    for index, value in column.items():
        if value != 'Not Reported':
            if (int(value) >= 0 and int(value) < 65535):
                column.iat[index] = convert_surfaceIceOrWaterDepth(int(value))
            else:
                column.iat[index] = 'Error:NTCIP'
    return column

def essSurfaceSalinity(column):
    for index, value in column.items():
        if value != 'Not Reported':
            if (int(value) >= 0 and int(value) < 65535):
                column.iat[index] = float(value)
            else:
                column.iat[index] = 'Error:NTCIP'
    return column

def essSurfaceBlackIceSignal(column):
    for index, value in column.items():
        column.iat[index] = getBlackIceSignal(value)
    return column

def essSubSurfaceSensorIndex(column):
    return column

def essSubSurfaceType(column):
    for index, value in column.items():
        column.iat[index] = getSubSurfaceType(value)
    return column

def essSubSurfaceDepth(column):
    for index, value in column.items():
        if value != 'Not Reported':
            if (int(value) >= 0 and int(value) < 1001):
                column.iat[index] = convert_subSurfaceDepth(int(value))
            else:
                column.iat[index] = 'Error:NTCIP'
    return column

# Dictionary that relates column names with functions to use in processing
functionDict = {
    'essAtmosphericPressure': essAtmosphericPressure,
    'essAvgWindDirection': windDir,
    'essAvgWindSpeed': windSpeed,
    'essSpotWindDirection': windDir,
    'essSpotWindSpeed': windSpeed,
    'essMaxWindGustSpeed': windSpeed,
    'essMaxWindGustDir': windDir,
    'essAirTemperature.1': essTemperature,
    'essWetbulbTemp': essTemperature,
    'essDewpointTemp': essTemperature,
    'essMaxTemp': essTemperature,
    'essMinTemp': essTemperature,
    'essRelativeHumidity': essRelativeHumidity,
    'essPrecipYesNo': essPrecipYesNo,
    'essPrecipRate': essPrecipRate,
    'essPrecipSituation': essPrecipSituation,
    'essPrecipitationOneHour': precipitationAccumulation,
    'essPrecipitationThreeHours': precipitationAccumulation,
    'essPrecipitationSixHours':	precipitationAccumulation,
    'essPrecipitationTwelveHours': precipitationAccumulation,
    'essPrecipitation24Hours': precipitationAccumulation,
    'essVisibility': essVisibility,
    'essVisibilitySituation': essVisibilitySituation,
    'essPavementSensorIndex.1': essPavementSensorIndex,
    'essPavementSensorIndex.2': essPavementSensorIndex,
    'essPavementSensorIndex.3': essPavementSensorIndex,
    'essPavementSensorIndex.4': essPavementSensorIndex,
    'essPavementSensorIndex.5': essPavementSensorIndex,
    'essPavementSensorIndex.6': essPavementSensorIndex,
    'essPavementSensorIndex.7': essPavementSensorIndex,
    'essPavementSensorIndex.8': essPavementSensorIndex,
    'essPavementType.1': essPavementType,
    'essPavementType.2': essPavementType,
    'essPavementType.3': essPavementType,
    'essPavementType.4': essPavementType,
    'essPavementType.5': essPavementType,
    'essPavementType.6': essPavementType,
    'essPavementType.7': essPavementType,
    'essPavementType.8': essPavementType,
    'essPavementSensorType.1': essPavementSensorType,
    'essPavementSensorType.2': essPavementSensorType,
    'essPavementSensorType.3': essPavementSensorType,
    'essPavementSensorType.4': essPavementSensorType,
    'essPavementSensorType.5': essPavementSensorType,
    'essPavementSensorType.6': essPavementSensorType,
    'essPavementSensorType.7': essPavementSensorType,
    'essPavementSensorType.8': essPavementSensorType,
    'essSurfaceStatus.1': essSurfaceStatus,
    'essSurfaceStatus.2': essSurfaceStatus,
    'essSurfaceStatus.3': essSurfaceStatus,
    'essSurfaceStatus.4': essSurfaceStatus,
    'essSurfaceStatus.5': essSurfaceStatus,
    'essSurfaceStatus.6': essSurfaceStatus,
    'essSurfaceStatus.7': essSurfaceStatus,
    'essSurfaceStatus.8': essSurfaceStatus,
    'essSurfaceTemperature.1': essTemperature,
    'essSurfaceTemperature.2': essTemperature,
    'essSurfaceTemperature.3': essTemperature,
    'essSurfaceTemperature.4': essTemperature,
    'essSurfaceTemperature.5': essTemperature,
    'essSurfaceTemperature.6': essTemperature,
    'essSurfaceTemperature.7': essTemperature,
    'essSurfaceTemperature.8': essTemperature,
    'essPavementTemperature.1': essTemperature,
    'essPavementTemperature.2': essTemperature,
    'essPavementTemperature.3': essTemperature,
    'essPavementTemperature.4': essTemperature,
    'essPavementTemperature.5': essTemperature,
    'essPavementTemperature.6': essTemperature,
    'essPavementTemperature.7': essTemperature,
    'essPavementTemperature.8': essTemperature,
    'essSurfaceSalinity.1': essSurfaceSalinity,
    'essSurfaceSalinity.2':	essSurfaceSalinity,
    'essSurfaceSalinity.3':	essSurfaceSalinity,
    'essSurfaceSalinity.4':	essSurfaceSalinity,
    'essSurfaceSalinity.5':	essSurfaceSalinity,
    'essSurfaceSalinity.6':	essSurfaceSalinity,
    'essSurfaceSalinity.7':	essSurfaceSalinity,
    'essSurfaceSalinity.8':	essSurfaceSalinity,
    'essSurfaceFreezePoint.1': essTemperature,
    'essSurfaceFreezePoint.2': essTemperature,
    'essSurfaceFreezePoint.3': essTemperature,	
    'essSurfaceFreezePoint.4': essTemperature,	
    'essSurfaceFreezePoint.5': essTemperature,
    'essSurfaceFreezePoint.6': essTemperature,	
    'essSurfaceFreezePoint.7': essTemperature,	
    'essSurfaceFreezePoint.8': essTemperature,	
    'essSurfaceBlackIceSignal.1': essSurfaceBlackIceSignal,
    'essSurfaceBlackIceSignal.2': essSurfaceBlackIceSignal,
    'essSurfaceBlackIceSignal.3': essSurfaceBlackIceSignal,	
    'essSurfaceBlackIceSignal.4': essSurfaceBlackIceSignal,	
    'essSurfaceBlackIceSignal.5': essSurfaceBlackIceSignal,	
    'essSurfaceBlackIceSignal.6': essSurfaceBlackIceSignal,
    'essSurfaceBlackIceSignal.7': essSurfaceBlackIceSignal,
    'essSurfaceBlackIceSignal.8': essSurfaceBlackIceSignal,
    'essSubSurfaceSensorIndex.1': essSubSurfaceSensorIndex,
    'essSubSurfaceSensorIndex.2': essSubSurfaceSensorIndex,
    'essSubSurfaceSensorIndex.3': essSubSurfaceSensorIndex,
    'essSubSurfaceSensorIndex.4': essSubSurfaceSensorIndex,
    'essSubSurfaceSensorIndex.5': essSubSurfaceSensorIndex,
    'essSubSurfaceSensorIndex.6': essSubSurfaceSensorIndex,
    'essSubSurfaceSensorIndex.7': essSubSurfaceSensorIndex,
    'essSubSurfaceSensorIndex.8': essSubSurfaceSensorIndex,
    'essSurfaceIceOrWaterDepth.1': essSurfaceIceOrWaterDepth,
    'essSurfaceIceOrWaterDepth.2': essSurfaceIceOrWaterDepth,
    'essSurfaceIceOrWaterDepth.3': essSurfaceIceOrWaterDepth,
    'essSurfaceIceOrWaterDepth.4': essSurfaceIceOrWaterDepth,
    'essSurfaceIceOrWaterDepth.5': essSurfaceIceOrWaterDepth,	
    'essSurfaceIceOrWaterDepth.6': essSurfaceIceOrWaterDepth,	
    'essSurfaceIceOrWaterDepth.7': essSurfaceIceOrWaterDepth,
    'essSurfaceIceOrWaterDepth.8': essSurfaceIceOrWaterDepth,
    'essSubSurfaceType.1': essSubSurfaceType,
    'essSubSurfaceType.2': essSubSurfaceType,
    'essSubSurfaceType.3': essSubSurfaceType,
    'essSubSurfaceType.4': essSubSurfaceType,
    'essSubSurfaceType.5': essSubSurfaceType,
    'essSubSurfaceType.6': essSubSurfaceType,
    'essSubSurfaceType.7': essSubSurfaceType,
    'essSubSurfaceType.8': essSubSurfaceType,
    'essSubSurfaceDepth.1': essSubSurfaceDepth,
    'essSubSurfaceDepth.2': essSubSurfaceDepth,
    'essSubSurfaceDepth.3': essSubSurfaceDepth,
    'essSubSurfaceDepth.4': essSubSurfaceDepth,
    'essSubSurfaceDepth.5': essSubSurfaceDepth,
    'essSubSurfaceDepth.6': essSubSurfaceDepth,
    'essSubSurfaceDepth.7': essSubSurfaceDepth,
    'essSubSurfaceDepth.8': essSubSurfaceDepth,
    'essSubSurfaceTemperature.1': essTemperature,
    'essSubSurfaceTemperature.2': essTemperature,
    'essSubSurfaceTemperature.3': essTemperature,
    'essSubSurfaceTemperature.4': essTemperature,
    'essSubSurfaceTemperature.5': essTemperature,
    'essSubSurfaceTemperature.6': essTemperature,
    'essSubSurfaceTemperature.7': essTemperature,
    'essSubSurfaceTemperature.8': essTemperature,	
}