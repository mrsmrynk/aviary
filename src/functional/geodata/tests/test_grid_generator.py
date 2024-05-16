from unittest.mock import patch

import geopandas as gpd
import geopandas.testing
import numpy as np
import pytest
from shapely.geometry import box, Polygon

from ..grid_generator import (
    compute_coordinates,
    generate_grid,
    _generate_tiles,
    _quantize_coordinates,
)
from .data.data_test_grid_generator import (
    data_test_compute_coordinates,
    data_test__generate_tiles,
    data_test__quantize_coordinates,
)
from ....utils.types import (
    BoundingBox,
    Coordinates,
    TileSize,
    XMin,
    YMin,
)


@pytest.mark.parametrize('bounding_box, tile_size, quantize, expected', data_test_compute_coordinates)
def test_compute_coordinates(
    bounding_box: BoundingBox,
    tile_size: TileSize,
    quantize: bool,
    expected: Coordinates,
) -> None:
    coordinates = compute_coordinates(
        bounding_box=bounding_box,
        tile_size=tile_size,
        quantize=quantize,
    )

    np.testing.assert_array_equal(coordinates, expected)


@pytest.mark.parametrize('x_min, y_min, tile_size, expected', data_test__quantize_coordinates)
def test__quantize_coordinates(
    x_min: XMin,
    y_min: YMin,
    tile_size: TileSize,
    expected: tuple[XMin, YMin],
) -> None:
    quantized_x_min, quantized_y_min = _quantize_coordinates(
        x_min=x_min,
        y_min=y_min,
        tile_size=tile_size,
    )

    assert quantized_x_min == expected[0]
    assert quantized_y_min == expected[1]


@patch('src.functional.geodata.grid_generator._generate_tiles')
@patch('src.functional.geodata.grid_generator.compute_coordinates')
def test_generate_grid(
    mocked_compute_coordinates,
    mocked__generate_tiles,
) -> None:
    bounding_box = (-128, -128, 128, 128)
    tile_size = 128
    epsg_code = 25832
    quantize = True
    expected_tiles = [
        box(-128, -128, 0, 0),
        box(0, -128, 128, 0),
        box(-128, 0, 0, 128),
        box(0, 0, 128, 128),
    ]
    mocked__generate_tiles.return_value = expected_tiles
    expected = gpd.GeoDataFrame(
        geometry=mocked__generate_tiles.return_value,
        crs=f'EPSG:{epsg_code}',
    )
    grid = generate_grid(
        bounding_box=bounding_box,
        tile_size=tile_size,
        epsg_code=epsg_code,
        quantize=quantize,
    )

    mocked_compute_coordinates.assert_called_once_with(
        bounding_box=bounding_box,
        tile_size=tile_size,
        quantize=quantize,
    )
    mocked__generate_tiles.assert_called_once_with(
        coordinates=mocked_compute_coordinates.return_value,
        tile_size=tile_size,
    )
    gpd.testing.assert_geodataframe_equal(grid, expected)


@pytest.mark.parametrize('coordinates, tile_size, expected', data_test__generate_tiles)
def test__generate_tiles(
    coordinates: Coordinates,
    tile_size: TileSize,
    expected: list[Polygon],
) -> None:
    tiles = _generate_tiles(
        coordinates=coordinates,
        tile_size=tile_size,
    )

    assert all(polygon.equals(expected[i]) for i, polygon in enumerate(tiles))
