#!/usr/bin/env python
"""
Creates a SVG tile image from a Mapbox Vector Tile.
"""
from __future__ import print_function
import os
import math
import argparse
import mapbox_vector_tile
from enum import Enum
from lxml import etree
from tempfile import NamedTemporaryFile
from django.contrib.gis.geos import LineString, Polygon
from svgutils.transform import SVG, SVGFigure, FigureElement, LineElement
# `mapbox-vector-tile` has a hardcoded tile extent of 4096 units.
MVT_EXTENT = 4096
TILE_SIZE = 256
fig = SVGFigure(width=TILE_SIZE, height=TILE_SIZE)


class CustomLineElement(LineElement):
    """
    Inherits from LineElement, gives access to style attribute.
    """
    def __init__(self, points, width=1, color='black', style=''):
        linedata = "M{} {} ".format(*points[0])
        linedata += " ".join(map(lambda x: "L{} {}".format(*x), points[1:]))
        line = etree.Element(SVG+"path",
                             {"d": linedata,
                              "stroke-width": str(width),
                              "stroke": color,
                              "style": style})
        FigureElement.__init__(self, line)


class GeometryType(Enum):
    """
    See:
    https://github.com/mapbox/vector-tile-spec/tree/master/2.1
    4.3.4. Geometry Types
    """
    UNKNOWN = 0
    POINT = 1
    LINESTRING = 2
    POLYGON = 3


def draw_polyline(points, prop_type):
    """
    https://github.com/btel/svg_utils
    """
    # the Linestring seems to be a multi-linestring
    stroke = 'black'
    if prop_type == 'ferry':
        stroke = 'blue'
    style = "fill:none;stroke:%s" % (stroke)
    polyline = CustomLineElement(points, style=style)
    fig.append(polyline)


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


def shrink(xy_pairs):
    """
    Linear shrinking before drawing
    """
    ratio = (MVT_EXTENT / TILE_SIZE)
    for xy_pair in xy_pairs:
        xy_pair[0] /= ratio
        xy_pair[1] /= ratio


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


def convert2pixel(linestring):
    """
    Converts x, y to pixels coordinates.
    """
    def xy_pairs():
        for x_merc, y_merc in linestring:
            x = x_merc
            y = MVT_EXTENT - y_merc
            yield [x, y]
    return [p for p in xy_pairs()]


def process_linestring(linestring, prop_type):
    xy_pairs = convert2pixel(linestring)
    if not in_extent(linestring):
        print("Not in extent")
        return
    clipping(xy_pairs)
    shrink(xy_pairs)
    # draw_line(xy_pairs[0], xy_pairs[1], prop_type)
    draw_polyline(xy_pairs, prop_type)


def process_polygon(polygon, prop_type):
    linestring = polygon[0]
    process_linestring(linestring, prop_type)


def is_multilinestring(geometry):
    return type(geometry[0][0]) == list


def process_feature(layer_type, feature):
    geometry = feature['geometry']
    properties = feature['properties']
    prop_type = layer_type
    try:
        prop_type = properties['type']
    except KeyError:
        pass
    geometry_type_id = feature['type']
    geometry_type = GeometryType(geometry_type_id)
    if geometry_type == GeometryType.LINESTRING:
        if is_multilinestring(geometry):
            # MultiLineString processing
            for subgeometry in geometry:
                linestring = LineString(subgeometry)
                process_linestring(linestring, prop_type)
        else:
            linestring = LineString(geometry)
            process_linestring(linestring, prop_type)
    elif geometry_type == GeometryType.POLYGON:
        for subgeometry in geometry:
            polygon = Polygon(subgeometry)
            process_polygon(polygon, prop_type)
    else:
        print("Not supported geometry type:", geometry_type)
        pass


def process_features(layer_key, features):
    for feature in features:
        # looks like it's in Spherical/Web Mercator (EPSG:3857)
        process_feature(layer_key, feature)


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
        "mvt_file", help="Mapbox Vector Tile file to load")
    args = parser.parse_args()
    return args


def process_layer(layer_key, layer_value):
    features = layer_value['features']
    process_features(layer_key, features)


def process_layers(layers_dict):
    for layer_key, layer_value in layers_dict.iteritems():
        process_layer(layer_key, layer_value)


def main():
    """
    Parses args and processes features.
    Usage example:
    mvt2svg.py 6160.mvt > 6160.svg
    """
    args = argument_parser()
    mvt_file_path = args.mvt_file
    layers_dict = decode_pbf(mvt_file_path)
    process_layers(layers_dict)
    svg_image_file = NamedTemporaryFile(delete=False, suffix=".svg")
    svg_image_file.close()
    fig.save(svg_image_file.name)
    svg_image_file = open(svg_image_file.name)
    print(svg_image_file.read(), end='')
    svg_image_file.close()
    os.unlink(svg_image_file.name)


if __name__ == "__main__":
    main()
