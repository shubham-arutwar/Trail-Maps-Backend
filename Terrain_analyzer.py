import numpy as np
import rasterio
from rasterio import features
import geojson
from pyproj import Transformer

def calculate_slope(elevation, cell_size):
    dy, dx = np.gradient(elevation, cell_size, cell_size)
    slope = np.arctan(np.sqrt(dx*dx + dy*dy)) * 57.29578
    return slope

dem_path = "AP_27302_FBS_F0370_RT1.dem.tif"
with rasterio.open(dem_path) as src:
    dem = src.read(1)
    transform = src.transform
    crs = src.crs

cell_size = transform[0] # Calculate cell size

slope = calculate_slope(dem, cell_size)

dangerous_areas = slope > 15

# Convert to vector
shapes = features.shapes(dangerous_areas.astype(np.int16), mask=dangerous_areas, transform=transform)

# Create transformer to convert coordinates from CRS to WGS84
transformer = Transformer.from_crs(crs, "EPSG:4326", always_xy=True)

features = []
for i, (geom, value) in enumerate(shapes):
    if value == 1:
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

feature_collection = geojson.FeatureCollection(features)

with open('dangerous_hiking_areas.geojson', 'w') as f:
    geojson.dump(feature_collection, f)

print("GeoJSON file created: dangerous_hiking_areas.geojson")