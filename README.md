RouteCompare
============

Do you have routes that you drive all of the time? Do you ever wonder which of
your alternate routes really is the fastest? While routing and mapping software
like GoogleMaps can give you an an example timing for an idealized trip, how
do your actual trips compare to that ideal, with traffic, weather, and actual
speeds factored in?

RouteCompare is a tool that searches the track-logs generated by your GPS device
and pulls out all of the segments that pass near configurable start and end points.
It then takes these segments and analyzes them to show you the travel-time of each,
the average travel-time between the two points, and the range of travel-times.

Example usage: crossing the city in rush hour
---------------------------------------------

I often find myself driving across our local city, Burlington, during rush-hour 
traffic. There are numerous ways in which one can cross the city each of which
encounters traffic at different parts of their routes, making direct comparison
difficult. Is it faster to stay on less-busy, but low-speed city streets or 
take the longer highway that dumps me onto a crowded arterial road?

After driving these routes for months, I downloaded the track-logs from my Garmin
Nuvi as a GPX file onto my computer to run the file through RouteCompare.

First, I need to pick two points that define the segment I'm interested in. I 
could just pick my normal start and end points, but in this case I'm most 
interested in portion of my route that diverges around different parts of the 
city and I didn't want slow traffic further down the road skewing the results.
I picked one point in Winooski with a 200m radius from which all of my routes
diverge. For my second point, I picked an intersection in Charlotte where my
routes all converge again. At the latter point I select a 400m radius to be sure
that at least one point in each track-log will match even with the higher highway
speeds. See the `examples/winooski-charlotte.ini` for these point configurations.

After I have my points configured, I can run my track-logs through RouteCompare
to extract just the matching segments:

    ./routecompare -v --route-config=examples/winooski-charlotte.ini examples/ExampleTracks.gpx > examples/winooski-charlotte.kml
    
The KML output from RouteCompare I then open in Google Earth. Looking at it, I
see the following information:

* Four of the six tracks went through my two points and had segments matched.
* Of the matching segments, the average travel-time was 24min:16sec with a
  variation of 4min:44sec between the fastest and slowest trips.
* Looking at the tracks on the map, I see that taking the highway has been both
  the fastest route as well as the second slowest (on a second trip). I also see
  that staying off the highway on back roads for too long just eats up several
  extra minutes beyond what I saved from avoiding traffic.

License
=======
Copyright (C) 2015 Adam Franco

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
