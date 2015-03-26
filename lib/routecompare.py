import sys
import geocalc

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
			start_position = self.find_start(segment)
			if start_position is not None:
				prefix, remainder = segment.split(start_position)
				prefix = None
				
				end_position = self.find_end(remainder)
				if end_position is not None:
					match, suffix = remainder.split(end_position)
					suffix = None
					remainder = None
					if self.verbose:
						sys.stderr.write("  {}  - found matching track on {}.\n".format(self.label, match.get_time_bounds()))
					
					return match
		return None
	
	def find_start(self, segment):
		start = None
		for point, point_no in segment.walk():
			arc = geocalc.distance_on_unit_sphere(point.latitude, point.longitude, self.start_latitude, self.start_longitude)
			meters = arc * geocalc.rad_earth_m
			# Start will be be the last point within the radius.
			if meters <= self.start_radius:
				start = point_no
		
		return start
	
	def find_end(self, segment):
		for point, point_no in segment.walk():
			arc = geocalc.distance_on_unit_sphere(point.latitude, point.longitude, self.end_latitude, self.end_longitude)
			meters = arc * geocalc.rad_earth_m
			# End will be be the first point within the radius.
			if meters <= self.end_radius:
				return point_no
		
		return None
	