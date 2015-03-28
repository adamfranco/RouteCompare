import simplekml
import sys
import math
from math import trunc
from polycircles import polycircles

class Kml(object):
	
	kml = None
	
	def __init__(self):
		self.kml = simplekml.Kml()
		
		self.circle_style = simplekml.Style()
		self.circle_style.polystyle.color="77FF0000"
		self.circle_style.linestyle.color="77FF0000"
		
	
	def add_route(self, route):
		folder_name=u"{} (avg: {}, \u0394: {})".format(route.label, self.format_timedelta(route.average_duration()), self.format_timedelta(route.delta()))
		fol = self.kml.newfolder(name=folder_name)
		polycircle = polycircles.Polycircle(latitude=route.start_latitude,
											longitude=route.start_longitude,
											radius=route.start_radius,
											number_of_vertices=36)
		polygon = fol.newpolygon(name=route.start_label, outerboundaryis=polycircle.to_kml())
		polygon.style = self.circle_style
		
		polycircle = polycircles.Polycircle(latitude=route.end_latitude,
											longitude=route.end_longitude,
											radius=route.end_radius,
											number_of_vertices=36)
		polygon = fol.newpolygon(name=route.end_label, outerboundaryis=polycircle.to_kml())
		polygon.style = self.circle_style
		
		route.matches.sort(key=lambda x: x.duration())
		
		for match in route.matches:
			line = fol.newlinestring(	name=match.name(), 
								description=match.description(),
								coords=match.coords())
			line.style.linestyle.width=3
			line.style.linestyle.color = self.line_color(match.normal_duration())
    
	def format_timedelta(self, delta):
		hours, remainder = divmod(delta.total_seconds(), 3600)
		minutes, seconds = divmod(remainder, 60)
		if hours >= 1:
			return "{:d}h:{:d}m:{:d}s".format(trunc(hours), trunc(minutes), trunc(seconds))
		if minutes >= 1:
			return "{:d}m:{:d}s".format(trunc(minutes), trunc(seconds))
		return "{:d}s".format(trunc(seconds))
    
	def line_color(self, fraction):
# 		sys.stderr.write("{} - {} - {}\n".format(fraction, int(round(255 * fraction * 2)), int(round(255 - ((fraction - 0.5) * 2 * 255)))))

		if fraction < 0.5:
			# each level in a gradient from green to yellow(00FF00 - 00FFFF)
			return '8000FF{:02X}'.format(int(round(255 * fraction * 2)))
		else:
			# each level in a gradient from yellow to red (00FFFF - 0000FF)
			return '8000{:02X}FF'.format(int(round(255 - ((fraction - 0.5) * 2 * 255))))
        
	def write(self):
		print self.kml.kml().encode('utf-8')