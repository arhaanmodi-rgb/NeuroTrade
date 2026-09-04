"""Tests for API predictor service."""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

import pytest
import numpy as np


def test_adapt_state_exact():
    from api.services.predictor import Predictor
    p = Predictor.__new__(Predictor)  # don't call __init__ (avoids loading models)
    state = np.array([1.0, 2.0, 3.0], dtype=np.float32)
    result = p.adapt_state(state, 3)
    assert len(result) == 3
    assert list(result) == [1.0, 2.0, 3.0]


def test_adapt_state_truncate():
    from api.services.predictor import Predictor
    p = Predictor.__new__(Predictor)
    state = np.array([1.0, 2.0, 3.0, 4.0, 5.0], dtype=np.float32)
    result = p.adapt_state(state, 3)
    assert len(result) == 3
    assert list(result) == [1.0, 2.0, 3.0]


def test_adapt_state_pad():
    from api.services.predictor import Predictor
    p = Predictor.__new__(Predictor)
    state = np.array([1.0, 2.0], dtype=np.float32)
    result = p.adapt_state(state, 5)
    assert len(result) == 5
    assert result[2] == 0.0
    assert result[3] == 0.0


def test_action_names():
    from api.services.predictor import ACTION_NAMES
    assert ACTION_NAMES[0] == 'HOLD'
    assert ACTION_NAMES[1] == 'BUY'
    assert ACTION_NAMES[2] == 'SELL'
