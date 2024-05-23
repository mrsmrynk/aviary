from __future__ import annotations

from dataclasses import dataclass, fields
from enum import Enum
from typing import Iterable, Iterator

import geopandas as gpd
import numpy as np
import numpy.typing as npt
import rasterio as rio
from shapely.geometry import box

BufferSize = int
Coordinates = npt.NDArray[np.int32]
EPSGCode = int
GroundSamplingDistance = float
TileSize = int
XMax = int
XMin = int
YMax = int
YMin = int


@dataclass
class BoundingBox(Iterable[int]):
    """
    Attributes:
        x_min: minimum x coordinate
        y_min: minimum y coordinate
        x_max: maximum x coordinate
        y_max: maximum y coordinate
    """
    x_min: XMin
    y_min: YMin
    x_max: XMax
    y_max: YMax

    def __post_init__(self) -> None:
        """Validates the bounding box.

        Raises:
            ValueError: Invalid bounding box (x_min >= x_max or y_min >= y_max)
        """
        if self.x_min >= self.x_max:
            message = (
                'Invalid bounding box! '
                'x_min must be less than x_max.'
            )
            raise ValueError(message)

        if self.y_min >= self.y_max:
            message = (
                'Invalid bounding box! '
                'y_min must be less than y_max.'
            )
            raise ValueError(message)

    def __len__(self) -> int:
        """Computes the number of coordinates.

        Returns:
            number of coordinates
        """
        return len(fields(self))

    def __getitem__(
        self,
        index: int,
    ) -> int:
        """Returns the coordinate given the index.

        Parameters:
            index: index of the coordinate

        Returns:
            coordinate
        """
        field = fields(self)[index]
        return getattr(self, field.name)

    def __iter__(self) -> Iterator[int]:
        """Iterates over the coordinates.

        Yields:
            coordinate
        """
        for field in fields(self):
            yield getattr(self, field.name)

    def quantize(
        self,
        value: int,
        inplace: bool = False,
    ) -> BoundingBox:
        """Quantizes the coordinates to the specified value.

        Parameters:
            value: value to quantize the coordinates to in meters
            inplace: if True, the bounding box is quantized inplace

        Returns:
            quantized bounding box
        """
        x_min = self.x_min - self.x_min % value
        y_min = self.y_min - self.y_min % value
        x_max = self.x_max + value - self.x_max % value
        y_max = self.y_max + value - self.y_max % value

        if inplace:
            self.x_min, self.y_min, self.x_max, self.y_max = x_min, y_min, x_max, y_max
            return self
        else:
            return BoundingBox(
                x_min=x_min,
                y_min=y_min,
                x_max=x_max,
                y_max=y_max,
            )

    def to_gdf(
        self,
        epsg_code: EPSGCode,
    ) -> gpd.GeoDataFrame:
        """Converts the bounding box to a geodataframe.

        Parameters:
            epsg_code: EPSG code

        Returns:
            bounding box
        """
        return gpd.GeoDataFrame(
            geometry=[box(self.x_min, self.y_min, self.x_max, self.y_max)],
            crs=f'EPSG:{epsg_code}',
        )


@dataclass
class DataFetcherInfo:
    """
    Attributes:
        bounding_box: bounding box (x_min, y_min, x_max, y_max)
        dtype: data type of each channel
        epsg_code: EPSG code
        ground_sampling_distance: ground sampling distance in meters
        num_channels: number of channels
    """
    bounding_box: BoundingBox
    dtype: list[DType]
    epsg_code: EPSGCode
    ground_sampling_distance: GroundSamplingDistance
    num_channels: int


class DType(Enum):
    """
    Attributes:
        BOOL: boolean data type
        FLOAT32: 32-bit floating point data type
        UINT8: 8-bit unsigned integer data type
    """
    BOOL = np.bool_
    FLOAT32 = np.float32
    UINT8 = np.uint8

    @classmethod
    def from_rio(
        cls,
        dtype: str,
    ) -> 'DType':
        """Converts the rasterio data type to the data type.

        Parameters:
            dtype: rasterio data type

        Returns:
            data type
        """
        mapping = {
            rio.dtypes.bool_: DType.BOOL,
            rio.dtypes.float32: DType.FLOAT32,
            rio.dtypes.uint8: DType.UINT8,
        }
        return mapping[dtype]


class GeospatialFilterMode(Enum):
    """
    Attributes:
        DIFFERENCE: difference mode
        INTERSECTION: intersection mode
    """
    DIFFERENCE = 'difference'
    INTERSECTION = 'intersection'


class InterpolationMode(Enum):
    BILINEAR = 'bilinear'
    NEAREST = 'nearest'

    def to_rio(self) -> rio.enums.Resampling:
        """Converts the interpolation mode to the rasterio resampling mode.

        Returns:
            rasterio resampling mode
        """
        mapping = {
            InterpolationMode.BILINEAR: rio.enums.Resampling.bilinear,
            InterpolationMode.NEAREST: rio.enums.Resampling.nearest,
        }
        return mapping[self]


class SetFilterMode(Enum):
    """
    Attributes:
        DIFFERENCE: difference mode
        INTERSECTION: intersection mode
        UNION: union mode
    """
    DIFFERENCE = 'difference'
    INTERSECTION = 'intersection'
    UNION = 'union'
