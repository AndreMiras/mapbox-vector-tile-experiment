# Mapbox Vector Tile Experiment
This is highly experimental, do not try this at home.
I'm playing with Mapbox Vector Tile and Python, see how it works etc... I'm trying to generate a SVG image from Mapbox pbf files.

I've downloaded [6160.mvt](http://a.tiles.mapbox.com/v4/mapbox.mapbox-streets-v7/14/4823/6160.mvt?access_token=pk.eyJ1IjoibWFwYm94IiwiYSI6ImNpbG10dnA3NzY3OTZ0dmtwejN2ZnUycjYifQ.1W5oTOnWXQ9R1w8u3Oo1yA) from the example given in https://www.mapbox.com/vector-tiles/ and I'm trying to render it purely in Python.

## Demo
```
python mvt2svg.py 6160.mvt
```
It will generate a [test.svg](http://imgh.us/test_259.svg) image out from the Mapbox Vector Tile file.


## Troubleshooting
### libgeos_c.so
```
OSError: Could not find lib geos_c or load any of its variants ['libgeos_c.so.1', 'libgeos_c.so'].
```
This is required by `mapbox_vector_tile` module, install it:

Ubuntu
```
apt install libgeos-c1
```
Gentoo
```
emerge sci-libs/geos
```
