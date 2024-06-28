# Using DEM Files for Terrain Analysis - _Terrain_analyzer.py_

- **this script marks the areas which have slope grater than given thrushold in a DEM (Digital elevation model) file.**
- this generated data can be further used to find optimal path between 2 points in unknown terrain which avoides areas with high slope.
- the dataset used here is from space mission by JAXA named ALOS.
  dataset is called ALOS PALSAR elevation dataset. available on "https://search.asf.alaska.edu/"
- reson to choose this dataset is its high resolution ie 12.5m. but dataset is very old between 2006-2011.
- there is also dataset Cartosat-1 DEM by ISRO which has 10m accuricy and has data till 2019.
- Cartosat-1 DEM dataset should be available on "https://bhoonidhi.nrsc.gov.in/bhoonidhi/index.html" but i was not able to download it.

## Libraries used

- numpy - arithmatic operations
- rasterio - r/w of raster data geoTIFF (.tif) format
- geojson - to generate geoJSON file for frontend
- pyproj - to work with coordinates

---

## Code explanation

```python
def calculate_slope(elevation, cell_size):
    dy, dx = np.gradient(elevation, cell_size, cell_size)
    slope = np.arctan(np.sqrt(dx*dx + dy*dy)) * 57.29578
    return slope
```

- dy and dx are gradient for that pixel in y and x axis. ([working of gradient in numpy](https://www.scaler.com/topics/numpy-gradient/))
- np.arctan( ) : converts gradient magnitude to angle in radians
- sqrt(dx*dx + dy*dy) : basically merges x-z graph with y-z graph as we dont need those two values seperately
- np.arctan( ) : converts the gradient magnitude to an angle in radians
- 57.29578 is constant which is used to convert radian to degrees.
- (1 radian = 57.29578 degrees)
- we get slope in degrees for each pixel

---

```python
with rasterio.open(dem_path) as src:
    dem = src.read(1)
    transform = src.transform
    crs = src.crs
```

- rasterio is used to handle tif files
- file is opened as 'src'
- raster files have multiple bands of data, each band(layer) contains a type of data
- in DEM file layer 1 contains elevation data. it stores data in form of 2D array each element denotes value at specific pixel
- 'dem' stores elevation data from file
- similarly src.transform is used to access coordinates of corners of geoTIFF file (area which the file covers on globe) and stored in 'transform'
- similarly 'crs', The CRS defines how the two-dimensional, projected map in the DEM file relates to real places on the Earth's surface.
  more details about CRS : https://geopandas.org/en/stable/docs/user_guide/projections.html

---

```python
cell_size = transform[0]
```

transform layer has 6 parameters :
transform[0]: Pixel width (often referred to as cell size in GIS terminology).
transform[1]: Row rotation (usually zero for north-up images).
transform[2]: X-coordinate of the upper-left corner of the top-left pixel.
transform[3]: Column rotation (usually zero for north-up images).
transform[4]: Y-coordinate of the upper-left corner of the top-left pixel.
transform[5]: Pixel height (negative if the image is oriented north-south).

we stored width of pixel in cell_size

---

```python
slope = calculate_slope(dem, cell_size)
```

calculates slope of each pixel and stores it in 'slope'

---

```python
dangerous_areas = slope > 15
```

descards pixels which have slope lower than 15

---

```python
shapes = features.shapes(dangerous_areas.astype(np.int16), mask=dangerous_areas, transform=transform)
```

converts 'dangerous_areas' data into polygons(vector shapes)

---

```python
transformer = Transformer.from_crs(crs, "EPSG:4326", always_xy=True)
```

this creates a transformer that converts coordinates from CRS to WGS84, which is coordinate system we used to store data

---

```python
features = []
for i, (geom, value) in enumerate(shapes):
    if value == 1:
        # Convert coordinates to lat/lon
        new_coords = []
        for ring in geom['coordinates']:
            new_ring = []
            for x, y in ring:
                lon, lat = transformer.transform(x, y)
                new_ring.append([lon, lat])
            new_coords.append(new_ring)

        feature = geojson.Feature(
            geometry={
                "type": "Polygon",
                "coordinates": new_coords
            },
            properties={
                "name": f"Unsuitable Area {i+1}",
                "fill": "#FF0000",
                "stroke": "#000000",
                "fill-opacity": 0.5,
                "stroke-width": 2
            }
        )
        features.append(feature)
```

converts dangerous_areas to geoJSON of given schema
