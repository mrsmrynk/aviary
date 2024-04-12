from unittest.mock import patch

from src.data import GridGenerator


@patch('src.data.grid_generator.validate_grid_generator')
def test_init(mocked_validate_grid_generator) -> None:
    bounding_box = (-128, -128, 128, 128)
    epsg_code = 25832
    grid_generator = GridGenerator(
        bounding_box=bounding_box,
        epsg_code=epsg_code,
    )

    mocked_validate_grid_generator.assert_called_once_with(
        bounding_box=bounding_box,
        epsg_code=epsg_code,
    )
    assert grid_generator.bounding_box == bounding_box
    assert grid_generator.epsg_code == epsg_code
    assert grid_generator.x_min == bounding_box[0]
    assert grid_generator.y_min == bounding_box[1]
    assert grid_generator.x_max == bounding_box[2]
    assert grid_generator.y_max == bounding_box[3]


@patch('src.data.grid_generator.compute_coordinates')
def test_compute_coordinates(
    mocked_compute_coordinates,
    grid_generator: GridGenerator,
) -> None:
    tile_size = 256
    quantize = True
    grid_generator.compute_coordinates(
        tile_size=tile_size,
        quantize=quantize,
    )

    mocked_compute_coordinates.assert_called_once_with(
        tile_size=tile_size,
        x_min=grid_generator.x_min,
        y_min=grid_generator.y_min,
        x_max=grid_generator.x_max,
        y_max=grid_generator.y_max,
        quantize=quantize,
    )


@patch('src.data.grid_generator.generate_grid')
def test_generate_grid(
    mocked_generate_grid,
    grid_generator: GridGenerator,
) -> None:
    tile_size = 256
    quantize = True
    grid_generator.generate_grid(
        tile_size=tile_size,
        quantize=quantize,
    )

    assert mocked_generate_grid.called_once_with(
        tile_size=tile_size,
        x_min=grid_generator.x_min,
        y_min=grid_generator.y_min,
        x_max=grid_generator.x_max,
        y_max=grid_generator.y_max,
        epsg_code=grid_generator.epsg_code,
        quantize=quantize,
    )
