# Mapbox Vector Tile Experiment
This is highly experimental, do not try this at home.
I'm playing with Mapbox Vector Tile and Python, see how it works etc... I'm trying to generate a SVG image from Mapbox pbf files.

I've downloaded a vector.pbf from https://github.com/mapbox/vector-tile-js/tree/master/test/fixtures/ and I'm trying to render it purely in Python.

## Demo
```
python mvt2svg.py -x 2047 -y 2047 -z 12 -f 12-1143-1497.vector.pbf
```
It will generate a [test.svg](http://imgh.us/test_257.svg) image out from the Mapbox Vector Tile file.

## Usage
```
python mvt2svg.py --help
usage: mvt2svg.py [-h] -x TILEX -y TILEY -z ZOOM -f MVT

optional arguments:
  -h, --help            show this help message and exit
  -x TILEX, --tilex TILEX
                        Tile x index
  -y TILEY, --tiley TILEY
                        Tile y index
  -z ZOOM, --zoom ZOOM  Tile zoom
  -f MVT, --mvt MVT     Mapbox Vector Tile file to load
```
