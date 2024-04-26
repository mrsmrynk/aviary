from pathlib import Path
from unittest.mock import patch

import geopandas as gpd
import numpy as np
import pytest

from src.data.coordinates_filter import (
    CompositeFilter,
    DuplicatesFilter,
    GeospatialFilter,
    MaskFilter,
    SetFilter,
)
from src.data.data_fetcher import (
    VRTDataFetcher,
)
from src.data.grid_generator import GridGenerator
from src.utils.types import (
    GeospatialFilterMode,
    InterpolationMode,
    SetFilterMode,
)


@pytest.fixture(scope='session')
def composite_filter() -> CompositeFilter:
    mask = np.array([0, 1, 0, 1], dtype=np.bool_)
    coordinates_filters = [
        DuplicatesFilter(),
        MaskFilter(
            mask=mask,
        ),
    ]
    return CompositeFilter(
        coordinates_filters=coordinates_filters,
    )


@pytest.fixture(scope='session')
def duplicates_filter() -> DuplicatesFilter:
    return DuplicatesFilter()


@pytest.fixture(scope='session')
def geospatial_filter() -> GeospatialFilter:
    tile_size = 128
    epsg_code = 25832
    gdf = gpd.GeoDataFrame(
        geometry=[],
        crs=f'EPSG:{epsg_code}',
    )
    mode = GeospatialFilterMode.DIFFERENCE
    return GeospatialFilter(
        tile_size=tile_size,
        epsg_code=epsg_code,
        gdf=gdf,
        mode=mode,
    )


@pytest.fixture(scope='session')
def grid_generator() -> GridGenerator:
    bounding_box = (-128, -128, 128, 128)
    epsg_code = 25832
    return GridGenerator(
        bounding_box=bounding_box,
        epsg_code=epsg_code,
    )


@pytest.fixture(scope='session')
def mask_filter() -> MaskFilter:
    mask = np.array([0, 1, 0, 1], dtype=np.bool_)
    return MaskFilter(
        mask=mask,
    )


@pytest.fixture(scope='session')
def set_filter() -> SetFilter:
    additional_coordinates = np.array([[-128, 0], [0, 0]], dtype=np.int32)
    mode = SetFilterMode.DIFFERENCE
    return SetFilter(
        additional_coordinates=additional_coordinates,
        mode=mode,
    )


@pytest.fixture(scope='session')
@patch('src.data.data_fetcher.vrt_data_fetcher_info')
def vrt_data_fetcher(
    _mocked_vrt_data_fetcher_info,
) -> VRTDataFetcher:
    path = Path('test/test.vrt')
    tile_size = 128
    ground_sampling_distance = .2
    interpolation_mode = InterpolationMode.BILINEAR
    buffer_size = None
    drop_channels = None
    return VRTDataFetcher(
        path=path,
        tile_size=tile_size,
        ground_sampling_distance=ground_sampling_distance,
        interpolation_mode=interpolation_mode,
        buffer_size=buffer_size,
        drop_channels=drop_channels,
    )
