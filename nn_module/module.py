from typing import Callable, Optional

import torch
from torch import nn


class Module(nn.Module):
    """
    Module: nn.Module with device and dtype properties
    """
    _device_buffer_name = "device_buffer"

    def __init__(self):
        super(Module, self).__init__()
        self.register_buffer(Module._device_buffer_name, torch.empty(0), persistent=True)

    def _get_device(self) -> torch.device:
        return self.state_dict()[Module._device_buffer_name].device

    def _set_device(self, device: torch.device):
        self.to(device)

    device = property(_get_device, _set_device)

    def _get_dtype(self) -> torch.dtype:
        return self.state_dict()[Module._device_buffer_name].dtype

    def _set_dtype(self, dtype: torch.dtype):
        self.to(dtype)

    dtype = property(_get_dtype, _set_dtype)


class Functional(Module):
    """
    Functional: wrapper for function
    """

    def __init__(self, f: Callable, name: Optional[str] = None):
        super(Functional, self).__init__()
        self.f = f
        if name is None:
            self.name = f
        else:
            self.name = name

    def __repr__(self):
        return f"{self.__class__.__name__} {self.name}"

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        return self.f(x)


class Batch(Module):
    """
    Batch: wrapper for non-batch module
    """

    def __init__(self, module: nn.Module):
        super(Batch, self).__init__()
        self.module = module

    def __repr__(self):
        return f"{self.__class__.__name__} {self.module}"

    def forward(self, x_batch: torch.Tensor) -> torch.Tensor:
        return torch.stack([
            self.module.forward(x)
            for x in x_batch
        ])
