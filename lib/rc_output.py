import simplekml
import sys
import math
from math import trunc
from polycircles import polycircles
from collections import namedtuple

class Output(object):

	def route_folder_name(self, route):
		return u"{} (avg: {}, \u0394: {})".format(
			route.label,
			self.format_timedelta(route.average_duration()),
			self.format_timedelta(route.delta()))

	def format_timedelta(self, delta):
		hours, remainder = divmod(delta.total_seconds(), 3600)
		minutes, seconds = divmod(remainder, 60)
		if hours >= 1:
			return "{:d}h:{:d}m:{:d}s".format(trunc(hours), trunc(minutes), trunc(seconds))
		if minutes >= 1:
			return "{:d}m:{:d}s".format(trunc(minutes), trunc(seconds))
		return "{:d}s".format(trunc(seconds))
    
	def green_to_red_rgb(self, fraction):
		RgbColor = namedtuple('RgbColor', 'red green blue')		
		if fraction < 0.5:
			# each level in a gradient from green to yellow(00FF00 - 00FFFF)
			return RgbColor('{:02X}'.format(int(round(255 * fraction * 2))), 'FF', '00')
		else:
			# each level in a gradient from yellow to red (00FFFF - 0000FF)
			return RgbColor('FF', '{:02X}'.format(int(round(255 - ((fraction - 0.5) * 2 * 255)))), '00')

class KmlOutput(Output):
	
	kml = None
	
	def __init__(self):
		self.kml = simplekml.Kml()
		
		self.circle_style = simplekml.Style()
		self.circle_style.polystyle.color="77FF0000"
		self.circle_style.linestyle.color="77FF0000"
		
	
	def add_route(self, route):
		fol = self.kml.newfolder(name=self.route_folder_name(route))
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
    
	def line_color(self, fraction):
# 		sys.stderr.write("{} - {} - {}\n".format(fraction, int(round(255 * fraction * 2)), int(round(255 - ((fraction - 0.5) * 2 * 255)))))
		color = self.green_to_red_rgb(fraction)
		return '80{}{}{}'.format(color.blue, color.green, color.red);
        
	def write(self):
		print self.kml.kml().encode('utf-8')