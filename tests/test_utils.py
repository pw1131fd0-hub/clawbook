import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import pytest
from backend.utils import mask_sensitive_data, is_secret_resource, K8S_NAME_RE, PodNotFoundError


class TestMaskSensitiveData:
    def test_masks_password(self):
        text = 'password: supersecret123'
        result = mask_sensitive_data(text)
        assert 'supersecret123' not in result
        assert '[MASKED]' in result

    def test_masks_token(self):
        text = 'token=eyJhbGciOiJSUzI1NiJ9.payload'
        result = mask_sensitive_data(text)
        assert 'eyJhbGciOiJSUzI1NiJ9' not in result

    def test_masks_api_key(self):
        text = 'api_key: sk-abc123xyz'
        result = mask_sensitive_data(text)
        assert 'sk-abc123xyz' not in result

    def test_masks_bearer_token(self):
        text = 'Authorization: Bearer eyJhbGciOiJSUzI1NiJ9longtokenvalue'
        result = mask_sensitive_data(text)
        assert 'eyJhbGciOiJSUzI1NiJ9longtokenvalue' not in result

    def test_preserves_non_sensitive(self):
        text = 'Hello World, this is a normal message'
        result = mask_sensitive_data(text)
        assert result == text

    def test_empty_string(self):
        assert mask_sensitive_data('') == ''


class TestIsSecretResource:
    def test_secret_kind(self):
        assert is_secret_resource({'kind': 'Secret'}) is True

    def test_secret_kind_lowercase(self):
        assert is_secret_resource({'kind': 'secret'}) is True

    def test_deployment_kind(self):
        assert is_secret_resource({'kind': 'Deployment'}) is False

    def test_empty_dict(self):
        assert is_secret_resource({}) is False


class TestK8sNameRe:
    """Tests for the Kubernetes DNS-subdomain name validation regex."""

    def test_valid_simple_name(self):
        assert K8S_NAME_RE.match('my-pod') is not None

    def test_valid_alphanumeric(self):
        assert K8S_NAME_RE.match('pod123') is not None

    def test_valid_single_char(self):
        assert K8S_NAME_RE.match('a') is not None

    def test_valid_with_hyphens(self):
        assert K8S_NAME_RE.match('my-app-v2-deployment') is not None

    def test_invalid_uppercase(self):
        assert K8S_NAME_RE.match('MyPod') is None

    def test_invalid_starts_with_hyphen(self):
        assert K8S_NAME_RE.match('-bad-name') is None

    def test_invalid_ends_with_hyphen(self):
        assert K8S_NAME_RE.match('bad-name-') is None

    def test_invalid_underscore(self):
        assert K8S_NAME_RE.match('bad_name') is None

    def test_invalid_empty_string(self):
        assert K8S_NAME_RE.match('') is None

    def test_invalid_dot(self):
        assert K8S_NAME_RE.match('bad.name') is None


class TestPodNotFoundError:
    """Tests for the PodNotFoundError custom exception."""

    def test_error_message_contains_pod_name(self):
        err = PodNotFoundError('my-pod', 'default')
        assert 'my-pod' in str(err)

    def test_error_message_contains_namespace(self):
        err = PodNotFoundError('my-pod', 'production')
        assert 'production' in str(err)

    def test_stores_pod_name_attribute(self):
        err = PodNotFoundError('crash-pod', 'staging')
        assert err.pod_name == 'crash-pod'

    def test_stores_namespace_attribute(self):
        err = PodNotFoundError('crash-pod', 'staging')
        assert err.namespace == 'staging'

    def test_is_exception(self):
        err = PodNotFoundError('pod', 'ns')
        assert isinstance(err, Exception)
