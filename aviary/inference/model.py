from __future__ import annotations

from pathlib import Path
from typing import Protocol

import numpy.typing as npt
import onnxruntime as ort
import torch
from huggingface_hub import hf_hub_download

# noinspection PyProtectedMember
from aviary._functional.inference.model import (
    get_providers,
    onnx_segmentation_model,
)
# noinspection PyProtectedMember
from aviary._utils.types import (
    BufferSize,
    Device,
)
from aviary.inference.aviary import aviary


class Model(Protocol):
    """Protocol for models

    Currently implemented models:
        - ONNXSegmentationModel: ONNX model for segmentation
    """

    def __call__(
        self,
        inputs: npt.NDArray | torch.Tensor,
    ) -> npt.NDArray:
        """Runs the model.

        Parameters:
            inputs: inputs

        Returns:
            predictions
        """
        ...


class SegmentationModel:
    """Model for segmentation"""

    def __init__(
        self,
        path: Path,
        buffer_size: BufferSize,
        device: Device = Device.CPU,
    ) -> None:
        """
        Parameters:
            path: path to the model
            buffer_size: buffer size in pixels (specifies the area around the tile that is additionally fetched)
            device: device (`CPU` or `CUDA`)
        """
        self.path = path
        self.buffer_size = buffer_size
        self.device = device

    @classmethod
    def from_huggingface(
        cls,
        repo: str,
        path: str,
        buffer_size: BufferSize,
        device: Device = Device.CPU,
    ) -> SegmentationModel:
        """Creates a segmentation model from the Hugging Face Hub.

        Parameters:
            repo: repository (Hugging Face Hub, e.g. 'user/repo')
            path: path to the model (Hugging Face Hub)
            buffer_size: buffer size in pixels (specifies the area around the tile that is additionally fetched)
            device: device (`CPU` or `CUDA`)

        Returns:
            segmentation model
        """
        path = hf_hub_download(
            repo_id=repo,
            filename=path,
        )
        path = Path(path)
        return cls(
            path=path,
            buffer_size=buffer_size,
            device=device,
        )

    @classmethod
    def from_aviary(
        cls,
        name: str,
        buffer_size: BufferSize,
        device: Device = Device.CPU,
    ) -> SegmentationModel:
        """Creates a segmentation model from the name of a model in aviary.

        Parameters:
            name: name of the model
            buffer_size: buffer size in pixels (specifies the area around the tile that is additionally fetched)
            device: device (`CPU` or `CUDA`)

        Returns:
            segmentation model
        """
        model_card = aviary[name]
        return cls.from_huggingface(
            repo=model_card.repo,
            path=model_card.path,
            buffer_size=buffer_size,
            device=device,
        )


class ONNXSegmentationModel(SegmentationModel):
    """ONNX model for segmentation

    Implements the `Model` protocol.
    """

    def __init__(
        self,
        path: Path,
        buffer_size: BufferSize,
        device: Device = Device.CPU,
    ) -> None:
        """
        Parameters:
            path: path to the model
            buffer_size: buffer size in pixels (specifies the area around the tile that is additionally fetched)
            device: device (`CPU` or `CUDA`)
        """
        super().__init__(
            path=path,
            buffer_size=buffer_size,
            device=device,
        )
        self._providers = get_providers(device)
        self._model = ort.InferenceSession(
            path_or_bytes=self.path,
            providers=self._providers)
        self._model_input_name = self._model.get_inputs()[0].name
        self._model_output_name = self._model.get_outputs()[0].name

    def __call__(
        self,
        inputs: npt.NDArray,
    ) -> npt.NDArray:
        """Runs the model.

        Parameters:
            inputs: inputs

        Returns:
            predictions
        """
        return onnx_segmentation_model(
            model=self._model,
            model_input_name=self._model_input_name,
            model_output_name=self._model_output_name,
            inputs=inputs,
        )