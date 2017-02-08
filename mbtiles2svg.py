#!/usr/bin/env python
"""
Wraps both mvt2svg.py and mbtiles2mvt.py to generate SVG directly from
vector MBTiles.
"""
from __future__ import print_function
import zlib
import sqlite3
import mvt2svg
import mbtiles2mvt


def argument_parser():
    """
    Argument parser helper.
    """
    return mbtiles2mvt.argument_parser()


def run(tile_x, tile_y, zoom, mbtiles_file):
    """
    Processes the MBTile file and returns the generated SVG content.
    """
    conn = sqlite3.connect(mbtiles_file)
    c = conn.cursor()
    c.execute(
        ("SELECT tile_data FROM tiles WHERE "
         "zoom_level=? AND tile_column=? AND tile_row=?"),
        (zoom, tile_x, tile_y))
    mvt_content_gz = mbtiles2mvt.run(tile_x, tile_y, zoom, mbtiles_file)
    # decompresses gzipped content
    wbits_gzip_format = zlib.MAX_WBITS | 16
    mvt_content = zlib.decompress(mvt_content_gz, wbits_gzip_format)
    svg_content = mvt2svg.run(mvt_content)
    return svg_content


def main():
    """
    Parses args and dumps MBTiles to SVG image file.
    Usage example:
    mbtiles2svg.py -x 0 -y 0 -z 0 planet_z0-z5.mbtiles > planet_x0y0z0.svg
    """
    args = argument_parser()
    args.mbtiles_file.close()
    mbtiles_file = args.mbtiles_file.name
    zoom = args.zoom
    tile_x = args.tilex
    tile_y = args.tiley
    mvt_content = run(tile_x, tile_y, zoom, mbtiles_file)
    print(mvt_content, end='')


if __name__ == "__main__":
    main()
