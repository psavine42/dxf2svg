# dxf2svg

Basic DXF to SVG converter.

## Usage

The only non-standard dependency is `dxfgrabber`.
If you dan't have it already, please install with
your favourite package manager, e.g.
```
pip install dxfgrabber
```

When it's done, you should be able to do things like:
Export layers with overridden colors:

```
python dxf2svg.py --source resources/cl.dxf --ovr resources/overrides.json --default_color "#000000" --mode training
```

```
python dxf2svg.py --source resources/cl.dxf --ovr resources/overrides.json --mode default
```

Export the layer dictionary to json
```
python dxf2svg.py --source resources/cl.dxf --mode make_json
```

```
python dxf2svg.py --source resources/cl.dxf --mode colors
```

Support types 
ARC, LINE, BLOCKS, TEXT, PLOYLINE 

line thickness and color are supported. There are no options on mapping a thickness to SVG thickness at this time

## TODO

* Add support for MTEXT, leaders
* Add support for block instances.

