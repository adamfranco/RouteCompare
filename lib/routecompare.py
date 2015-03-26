import sys
import copy
import geocalc

from pytz import timezone
import pytz

class Route(object):
	
	verbose = False
	
	label = "Unnamed Route"
	bidirectional = False
	
	start_label = "Start"
	start_latitude = 0
	start_longitude = 0
	start_radius = 100

	end_label = "End"
	end_latitude = 1
	end_longitude = 1
	end_radius = 100
	
	def collect_matches(self, tracks):
		matches = []
		for track in tracks:
			match = self.extract_match(track)
			if match is not None:
				matches.append(match)
	
	def extract_match(self, track):
		for segment in track.segments:
			start_position = self.find_start(segment, self.start_latitude, self.start_longitude, self.start_radius)
			if start_position is not None:
				prefix, remainder = segment.split(start_position)
				prefix = None
				
				end_position = self.find_end(remainder, self.end_latitude, self.end_longitude, self.end_radius)
				if end_position is not None:
					match, suffix = remainder.split(end_position)
					suffix = None
					remainder = None
					return RouteMatch(self, match)
					
				# If we didn't find one match, but not an end going one direction, search the other way
				elif self.bidirectional:
					reversed = segment.clone()
					segment.points.reverse()
					start_position = self.find_start(reversed, self.end_latitude, self.end_longitude, self.end_radius)
					if start_position is not None:
						prefix, remainder = reversed.split(start_position)
						prefix = None
				
						end_position = self.find_end(remainder, self.start_latitude, self.start_longitude, self.start_radius)
						if end_position is not None:
							match, suffix = remainder.split(end_position)
							suffix = None
							remainder = None
							match.points.reverse()
							return RouteMatch(self, match, True)
		return None
	
	def find_start(self, segment, latitude, longitude, radius):
		start = None
		for point, point_no in segment.walk():
			arc = geocalc.distance_on_unit_sphere(point.latitude, point.longitude, latitude, longitude)
			meters = arc * geocalc.rad_earth_m
			# Start will be be the last point within the radius.
			if meters <= radius:
				start = point_no
		
		return start
	
	def find_end(self, segment, latitude, longitude, radius):
		for point, point_no in segment.walk():
			arc = geocalc.distance_on_unit_sphere(point.latitude, point.longitude, latitude, longitude)
			meters = arc * geocalc.rad_earth_m
			# End will be be the first point within the radius.
			if meters <= radius:
				return point_no
		
		return None

class RouteMatch(object):

	segment = None
	route = None
	reversed = False
	
	def __init__(self, route, segment, reversed = False):
		self.route = route
		self.segment = segment
		self.reversed = reversed
		if self.route.verbose:
			if self.reversed:
				reversed = " (reversed)"
			else:
				reversed = ""
			sys.stderr.write("  {}  - found matching track on {} {}\n".format(self.route.label, self.start_time(), reversed))
			
	def start_time(self):
		time = self.segment.get_time_bounds().start_time.replace(tzinfo=timezone('UTC'))
		return time.astimezone(timezone('US/Eastern'))
			