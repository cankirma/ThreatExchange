#!/usr/bin/env python

"""
A wrapper around fetching, storing, and recovering the state from TE.
"""

import json
import pathlib
import typing as t

from . import TE, collab_config
from .content_type import meta
from .signal_type import base as signal_base


class Dataset:

    EXTENSION = ".te"

    def __init__(
        self,
        config: collab_config.CollaborationConfig,
        state_dir: t.Optional[pathlib.Path] = None,
    ) -> None:
        self.config = config
        if state_dir is None:
            state_dir = pathlib.Path.home() / config.default_state_dir_name
            assert not state_dir.is_file()
        self.state_dir = state_dir

    @property
    def is_cache_empty(self) -> bool:
        return not (
            self.state_dir.exists() and any(self.state_dir.glob(f"*{self.EXTENSION}"))
        )

    def clear_cache(self) -> None:
        for p in self.state_dir.iterdir():
            if p.suffix == self.EXTENSION:
                p.unlink()

    def _signal_state_file(self, signal_type: signal_base.SignalType) -> pathlib.Path:
        return self.state_dir / f"{signal_type.get_name()}{self.EXTENSION}"

    def load_cache(
        self, signal_types: t.Optional[t.Iterable[signal_base.SignalType]] = None
    ) -> t.List[signal_base.SignalType]:
        """Load everything in the state directory and initialize signal types"""
        if signal_types is None:
            signal_types = [s() for s in meta.get_all_signal_types()]
        ret = []
        for signal_type in signal_types:
            signal_state_file = self._signal_state_file(signal_type)
            if signal_state_file.exists():
                signal_type.load(signal_state_file)
            ret.append(signal_type)
        return ret

    def store_cache(self, signal_type: signal_base.SignalType) -> None:
        if not self.state_dir.exists():
            self.state_dir.mkdir()
        signal_type.store(self._signal_state_file(signal_type))