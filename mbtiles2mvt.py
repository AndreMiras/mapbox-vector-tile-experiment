#!/usr/bin/env python
"""
Extracts a SQLite MBTiles (with vector) file to a MVT/PBF file.
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


def run(tile_x, tile_y, zoom, mbtiles_file):
    """
    Process the MBTile file and return the generated MVT content.
    """
    conn = sqlite3.connect(mbtiles_file)
    c = conn.cursor()
    c.execute(
        ("SELECT tile_data FROM tiles WHERE "
         "zoom_level=? AND tile_column=? AND tile_row=?"),
        (zoom, tile_x, tile_y))
    mvt_content = c.fetchone()[0]
    return mvt_content


def main():
    """
    Parses args and dumps MBTiles to MVT/PBF.
    Usage example:
    mbtiles2mvt.py -x 0 -y 0 -z 0 planet_z0-z5.mbtiles > planet_x0y0z0.mvt.gz
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
