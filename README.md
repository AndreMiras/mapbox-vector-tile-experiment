# Mapbox Vector Tile Experiment
This is highly experimental, do not try this at home.
I'm playing with Mapbox Vector Tile and Python, see how it works etc... I'm trying to generate a SVG image from Mapbox Vector Tiles (.pbf/.mvt) files.
If you have SQLite vector MBTiles, I'm also providing a script that queries the database and dumps to MVT given tile x, tile y and zoom level.

## MVT/PBF to SVG
I've downloaded [6160.mvt](http://a.tiles.mapbox.com/v4/mapbox.mapbox-streets-v7/14/4823/6160.mvt?access_token=pk.eyJ1IjoibWFwYm94IiwiYSI6ImNpbG10dnA3NzY3OTZ0dmtwejN2ZnUycjYifQ.1W5oTOnWXQ9R1w8u3Oo1yA) from the example given in https://www.mapbox.com/vector-tiles/.
Now let's render it purely in Python.
```
python mvt2svg.py 6160.mvt > 6160.svg
```
It will generate a [6160.svg](http://imgh.us/test_259.svg) image out from the Mapbox Vector Tile file.

## Vector MBTiles to MVT/PBF
Having only a vector .mbtile file, it's possible to dump it as MVT/PBF given x, y and zoom level.
```
python mbtiles2mvt.py -x 0 -y 0 -z 0 planet_z0-z5.mbtiles > planet_x0y0z0.mvt.gz
```
It will dump the gzipped tile data, next thing is to extract it and use it with mvt2svg.py script.
```
zcat planet_x0y0z0.mvt.gz > planet_x0y0z0.mvt
python mvt2svg.py planet_x0y0z0.mvt > planet_x0y0z0.svg
```

## MBTiles to SVG directly
It's also possible to use a wrapper script to generate a SVG directly from vector MBTiles file.
```
python mbtiles2svg.py -x 0 -y 0 -z 0 planet_z0-z5.mbtiles > planet_x0y0z0.svg
```

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
