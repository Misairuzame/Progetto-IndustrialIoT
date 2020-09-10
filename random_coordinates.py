# Modified from:
# https://gis.stackexchange.com/questions/164005/getting-random-coordinates-based-on-country

import re
import random
import shapefile
from shapely.geometry import shape, Point

def random_point_in_country(country_name):
    shp_location = "/home/zeradias/Scrivania/ProgettoIIoT/mqtt-mosquitto-client/geoloc/ne_10m_admin_0_countries"
    shapes = shapefile.Reader(shp_location+".shp", shp_location+".shx", shp_location+".dbf")
    country = [s for s in shapes.records() if country_name in s][0]
    country_id = int(re.findall(r'\d+', str(country))[0])

    shapeRecs = shapes.shapeRecords()
    feature = shapeRecs[country_id].shape.__geo_interface__

    shp_geom = shape(feature)

    minx, miny, maxx, maxy = shp_geom.bounds
    while True:
        p = Point(random.uniform(minx, maxx), random.uniform(miny, maxy))
        if shp_geom.contains(p):
            return p.x, p.y