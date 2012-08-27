# Taken from http://www.movable-type.co.uk/scripts/latlong.html
# More accurate stuff here: http://www.movable-type.co.uk/scripts/latlong.js

import math

R = 6371.0 # The radius of the Earth

class GPSPosn:
	def __init__ (self, latitude, longitude):
		self.latitude = latitude
		self.longitude = longitude

	# GPSPosn -> NaturalNumber
	# The distance, in kilometers, to the given GPS position.
	def distance_to (self, posn):
		dLat = math.radians(posn.latitude-self.latitude)
		dLon = math.radians(posn.longitude-self.longitude)
		a = math.sin(dLat/2.0) * math.sin(dLat/2.0) + \
			math.cos(math.radians(self.latitude)) * \
			math.cos(math.radians(posn.latitude)) * \
			math.sin(dLon/2.0) * math.sin(dLon/2.0)
		c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
		d = R * c
		return d

	# GPSPosn Degrees NaturalNumber -> GPSPosn
	# The GPS position arrived at by traveling along the given bearing
	# going the given distance from this position.
	def destination_point (self, bearing, distance):
		dist = distance / R
		brng = math.radians(bearing)
		lat1 = math.radians(self.latitude)
		lon1 = math.radians(self.longitude)

		lat2 = math.asin( \
			math.sin(lat1) * math.cos(dist) \
			+ math.cos(lat1) * math.sin(dist) \
			* math.cos(brng))
		lon2 = lon1 + math.atan2( \
			math.sin(brng)*math.sin(dist) \
			* math.cos(lat1), \
			math.cos(dist)-math.sin(lat1) \
			* math.sin(lat2))
		lon2 = (lon2+3*math.pi)%(2*math.pi) - math.pi
		return GPSPosn(math.degrees(lat2), math.degrees(lon2))

	# GPSPosn -> Degrees
	# The initial bearing, or azimuth, toward the given position in degrees.
	def bearing_to (self, posn):
		lat1 = math.radians(self.latitude)
		lat2 = math.radians(posn.latitude)
		dLon = math.radians(posn.longitude-self.longitude)
		y = math.sin(dLon) * math.cos(lat2);
		x = math.cos(lat1) * math.sin(lat2) \
			- math.sin(lat1) * math.cos(lat2) \
			* math.cos(dLon);
		brng = math.atan2(y,x)
		return (math.degrees(brng)+360)%360

	# A string representation of the GPS position.
	def to_string (self):
		return str(self.latitude)+","+str(self.longitude)

