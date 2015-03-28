import sys
import copy
import geocalc
import datetime

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
	
	matches = None

	def __init__(self):
		self.matches = []
	
	def collect_matches(self, tracks):
		for track in tracks:
			match = self.extract_match(track)
			if match is not None:
				self.matches.append(match)
				self.max = None
				self.min = None
		
	
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
	
	def max_duration(self):
		if self.max is None:
			self.max = self.matches[0].duration()
			for match in self.matches:
				if match.duration() > self.max:
					self.max = match.duration()
		return self.max
		
	def min_duration(self):
		if self.min is None:
			self.min = self.matches[0].duration()
			for match in self.matches:
				if match.duration() < self.min:
					self.min = match.duration()
		return self.min
	
	def average_duration(self):
		sum = 0
		num = 0
		for duration in self.durations_as_seconds():
			sum += duration
			num += 1
		return datetime.timedelta(seconds=(sum / num))
	
	def durations_as_seconds(self):
		for match in self.matches:
			yield match.duration().total_seconds()
	
	def delta(self):
		return self.max_duration() - self.min_duration()
		
class RouteMatch(object):

	segment = None
	route = None
	reversed = False
	
	def __init__(self, route, segment, reversed = False):
		self.route = route
		self.segment = segment
		self.reversed = reversed
		if self.route.verbose:
			sys.stderr.write("  {}  - found matching track on {} {}\n".format(self.route.label, self.start_time(), self.reversed_string()))
			
	def start_time(self):
		time = self.segment.get_time_bounds().start_time.replace(tzinfo=timezone('UTC'))
		return time.astimezone(timezone('US/Eastern'))
	
	def name(self):
		return "{} - {}".format(self.route.label, self.start_time())
	
	def description(self):
		return "{}\n{}".format(self.reversed_string(), self.duration())
		
	def reversed_string(self):
		if self.reversed:
			return "(reversed)"
		else:
			return ""
	
	def duration(self):
		bounds = self.segment.get_time_bounds()
		if bounds.start_time > bounds.end_time:
			return bounds.start_time - bounds.end_time
		else:
			return bounds.end_time - bounds.start_time
	
	def normal_duration(self):
		max = self.route.max_duration()
		min = self.route.min_duration()
		return (self.duration() - min).total_seconds() / (max - min).total_seconds()
	
	def coords(self):
		coords = []
		for point in self.segment.walk(True):
			coords.append((point.longitude, point.latitude))
		return coords
			