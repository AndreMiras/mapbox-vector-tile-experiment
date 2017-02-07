#!/usr/bin/env python
"""
Extracts a SQLite MBTiles (with vector) file to a PBF file.
"""
from __future__ import print_function
import argparse
import sqlite3


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
        "mbtiles_file", help="SQLite MBTiles (with vector) file to load",
        type=argparse.FileType('r'))
    args = parser.parse_args()
    return args


def main():
    """
    Parses args and dumps MBTiles to PBF.
    Usage example:
    mbtiles2pbf.py -x 0 -y 0 -z 0 planet_z0-z5.mbtiles > planet_x0y0z0.pbf
    """
    args = argument_parser()
    args.mbtiles_file.close()
    mbtiles_file = args.mbtiles_file.name
    zoom = args.zoom
    tile_x = args.tilex
    tile_y = args.tiley
    conn = sqlite3.connect(mbtiles_file)
    c = conn.cursor()
    c.execute(
        ("SELECT tile_data FROM tiles WHERE "
         "zoom_level=? AND tile_column=? AND tile_row=?"),
        (zoom, tile_x, tile_y))
    one = c.fetchone()
    print(one[0], end='')


if __name__ == "__main__":
    main()
