"""
Creates a SVG tile image from a Mapbox Vector Tile.
"""
import argparse
import svgwrite
import mapbox_vector_tile
# enum34==1.1.4
from enum import Enum
# https://github.com/mapbox/vector-tile-py
from vector_tile import renderer
import mercantile
import math
from django.contrib.gis.geos import LineString, Polygon
SRID_LNGLAT = 4326
SRID_SPHERICAL_MERCATOR = 3857
# `mapbox-vector-tile` has a hardcoded tile extent of 4096 units.
MVT_EXTENT = 4096
dwg = svgwrite.Drawing('test.svg', profile='tiny')


class GeometryType(Enum):
    UNKNOWN = 0
    POINT = 1
    LINESTRING = 2
    POLYGON = 3


def draw_line(start, end):
    """
    https://pythonhosted.org/svgwrite/classes/shapes.html#line
    """
    # the Linestring seems to be a multi-linestring
    stroke = svgwrite.rgb(200, 10, 16, '%')
    line = dwg.line(start=start, end=end, stroke=stroke)
    dwg.add(line)
    dwg.save()


def deg2num(lat_deg, lon_deg, zoom):
    """
    lat, lon, zoom to tile numbers
    https://wiki.openstreetmap.org/wiki/Slippy_map_tilenames
    http://gis.stackexchange.com/a/133535
    """
    lat_rad = math.radians(lat_deg)
    n = 2.0 ** zoom
    xtile = int((lon_deg + 180.0) / 360.0 * n)
    ytile = int(
            (1.0 -
                math.log(
                    math.tan(lat_rad) + (1 / math.cos(lat_rad))) /
                math.pi) /
            2.0 * n)
    return (xtile, ytile)


def recommended_tile_xyz(line_string, zoom):
    """
    From a line_string and a zoom,
    returns the tile containing a given point.
    """
    assert(line_string.srid == SRID_SPHERICAL_MERCATOR)
    # mercantile.tile(*mercantile.ul(486, 332, 10) + (10,))
    # mercantile.tile(lng, lat, zoom)
    lng, lat = renderer.merc2lonlat(line_string[0][0], line_string[0][1])
    xtile, ytile = deg2num(lat, lng, zoom)
    print "recommended_tile_xyz:", (xtile, ytile, zoom)
    return (xtile, ytile)


def shrink(xy_pairs):
    """
    Linear shrinking before drawing
    """
    ratio = 4
    for xy_pair in xy_pairs:
        xy_pair[0] /= ratio
        xy_pair[1] /= ratio


def mercator2tile(tile_bounds, line):
    """
    Converts the LineString Mercator coordinates to tile-based coordinates
    by computing the pixel location within the tile.
    """
    # we work with both in Spherical Mercator
    assert(tile_bounds.srid == SRID_SPHERICAL_MERCATOR)
    assert(line.srid == SRID_SPHERICAL_MERCATOR)
    (x0, y0, x_max, y_max) = tile_bounds.extent
    x_span = x_max - x0
    y_span = y_max - y0

    def xy_pairs():
        for x_merc, y_merc in line:
            yield [
                int((x_merc - x0) * MVT_EXTENT / x_span),
                int((y_merc - y0) * MVT_EXTENT / y_span),
                ]
    return [p for p in xy_pairs()]


def in_extent(pairs):
    """
    Returns False if none of the points are in the extent.
    """
    for x, y in pairs:
        if x >= 0 and x <= MVT_EXTENT:
            return True
        if y >= 0 and y <= MVT_EXTENT:
            return True
    return False


def clipping(pairs):
    """
    Returns the pairs clipped, so it fits in the extent.
    """
    for point in pairs:
        # makes sure it's above or equal to 0
        point[0] = max(point[0], 0)
        point[1] = max(point[1], 0)
        # makes sure it's below or equal to MVT_EXTENT
        point[0] = min(point[0], MVT_EXTENT)
        point[1] = min(point[1], MVT_EXTENT)


def xyz_tile_mercator_bounds(x, y, zoom):
    """
    Returns XYZ tile Mercator bounds.
    """
    tile_bounds = Polygon.from_bbox(mercantile.bounds(x, y, zoom))
    tile_bounds.srid = SRID_LNGLAT
    tile_bounds.transform(SRID_SPHERICAL_MERCATOR)
    return tile_bounds


def process_linestring(tile_xyz, lnglat_line):
    tile_bounds = xyz_tile_mercator_bounds(*tile_xyz)
    # recommended_tile_xyz(lnglat_line, zoom)
    xy_pairs = mercator2tile(tile_bounds, lnglat_line)
    if not in_extent(xy_pairs):
        print "Not in extent"
        return
    clipping(xy_pairs)
    shrink(xy_pairs)
    draw_line(xy_pairs[0], xy_pairs[1])


def process_feature(tile_xyz, feature):
    x, y, zoom = tile_xyz
    geometry = feature['geometry']
    geometry_type_id = feature['type']
    geometry_type = GeometryType(geometry_type_id)
    # print "geometry_type:", geometry_type
    if geometry_type == GeometryType.LINESTRING:
        lnglat_line = LineString(geometry, srid=SRID_SPHERICAL_MERCATOR)
        process_linestring(tile_xyz, lnglat_line)
    else:
        print "Not a LINESTRING"


def process_features(tile_xyz, features):
    for feature in features:
        # looks like it's in Spherical/Web Mercator (EPSG:3857)
        process_feature(tile_xyz, feature)


def decode_pbf(mvt_file_path):
    """
    Open the file at "mvt_file_path" read-only, decodes the PBF tile
    as a layers dictionary.
    For instance decodes 12-1143-1497.vector.pbf, downloaded from:
    https://github.com/mapbox/vector-tile-js/tree/master/test/fixtures/
    Can also download some from:
    http://download.geofabrik.de/
    """
    with open(mvt_file_path, 'r') as mvt_file:
        pbf_data = mvt_file.read()
        layers_dict = mapbox_vector_tile.decode(pbf_data)
    return layers_dict


def argument_parser():
    """
    Argument parser helper.
    """
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-x", "--tilex", help="Tile x index", type=int, required=True)
    parser.add_argument(
        "-y", "--tiley", help="Tile y index", type=int, required=True)
    parser.add_argument(
        "-z", "--zoom", help="Tile zoom", type=int, required=True)
    parser.add_argument(
        "-f", "--mvt", help="Mapbox Vector Tile file to load", required=True)
    args = parser.parse_args()
    return args


def main():
    """
    Parses args and processes features.
    Usage example:
    mvt2svg.py -x 164 -y 367 -z 10 -f fixtures/12-1143-1497.vector.pbf
    mvt2svg.py -x 2047 -y 2047 -z 12 -f fixtures/12-1143-1497.vector.pbf
    mvt2svg.py -x 8190 -y 8189 -z 14 -f fixtures/12-1143-1497.vector.pbf
    """
    args = argument_parser()
    mvt_file_path = args.mvt
    tile_xyz = (args.tilex, args.tiley, args.zoom)
    layers_dict = decode_pbf(mvt_file_path)
    process_features(tile_xyz, layers_dict['road']['features'])


if __name__ == "__main__":
    main()
