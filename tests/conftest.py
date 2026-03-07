"""Shared pytest fixtures for Lobster K8s Copilot tests."""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import pytest
from unittest.mock import patch


@pytest.fixture(autouse=True)
def patch_k8s():
    """Auto-use fixture that prevents real Kubernetes config loading during tests."""
    with patch('kubernetes.config.load_kube_config'), \
         patch('kubernetes.config.load_incluster_config'):
        yield
