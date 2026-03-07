"""Tests for the AIDiagnoser class and AI provider routing logic."""
import os
from unittest.mock import MagicMock, patch

from ai_engine.diagnoser import AIDiagnoser


SAMPLE_CONTEXT = {
    "pod_name": "test-pod",
    "namespace": "default",
    "error_type": "CrashLoopBackOff",
    "describe": "Phase: Failed\nEvents:\nBackOff: Back-off restarting failed container",
    "logs": "Error: cannot connect to database at db:5432",
}


class TestAIDiagnoserNoProvider:
    """Tests for AIDiagnoser behaviour when no LLM provider is configured."""

    def test_returns_structured_dict_without_provider(self):
        """Should return a graceful fallback when no LLM is configured."""
        with patch.dict(os.environ, {}, clear=True):
            # Remove all API keys to simulate no-provider
            env_patch = {k: '' for k in ['OPENAI_API_KEY', 'GEMINI_API_KEY', 'OLLAMA_BASE_URL']}
            with patch.dict(os.environ, env_patch):
                diagnoser = AIDiagnoser()
                result = diagnoser.diagnose(SAMPLE_CONTEXT)
        assert 'root_cause' in result
        assert 'remediation' in result
        assert 'raw_analysis' in result
        assert 'model_used' in result


class TestAIDiagnoserWithMock:
    """Tests for AIDiagnoser with mocked LLM providers."""

    def test_uses_openai_when_configured(self):
        """Should call OpenAI and parse structured JSON when OPENAI_API_KEY is set."""
        mock_response = (
            '{"root_cause": "DB connection refused", "remediation": "kubectl exec..."}'
        )
        env = {'OPENAI_API_KEY': 'sk-test', 'GEMINI_API_KEY': '', 'OLLAMA_BASE_URL': ''}
        with patch.dict(os.environ, env):
            with patch('ai_engine.analyzers.openai_analyzer.OpenAI') as mock_openai:
                mock_client = MagicMock()
                mock_openai.return_value = mock_client
                mock_client.chat.completions.create.return_value = MagicMock(
                    choices=[MagicMock(message=MagicMock(content=mock_response))]
                )
                diagnoser = AIDiagnoser()
                result = diagnoser.diagnose(SAMPLE_CONTEXT)
        assert result['root_cause'] == 'DB connection refused'
        assert 'kubectl exec' in result['remediation']
        assert result['model_used'].startswith('openai/')

    def test_parse_response_handles_malformed_json(self):
        """_parse_response should return a valid dict even when the LLM returns non-JSON."""
        diagnoser = AIDiagnoser()
        result = diagnoser._parse_response(  # pylint: disable=protected-access
            "Not valid JSON but contains useful info"
        )
        assert 'root_cause' in result
        assert 'remediation' in result

    def test_parse_response_extracts_json_from_markdown(self):
        """_parse_response should unwrap JSON fenced in markdown code blocks."""
        diagnoser = AIDiagnoser()
        raw = '```json\n{"root_cause": "OOM", "remediation": "Increase limits"}\n```'
        result = diagnoser._parse_response(raw)  # pylint: disable=protected-access
        assert result['root_cause'] == 'OOM'
        assert result['remediation'] == 'Increase limits'

    def test_parse_response_extracts_detailed_analysis(self):
        """_parse_response should surface detailed_analysis when the LLM includes it."""
        diagnoser = AIDiagnoser()
        raw = (
            '{"root_cause": "OOM kill",'
            ' "detailed_analysis": "The container exceeded its memory limit.",'
            ' "remediation": "Increase memory limits"}'
        )
        result = diagnoser._parse_response(raw)  # pylint: disable=protected-access
        assert result['detailed_analysis'] == 'The container exceeded its memory limit.'

    def test_parse_response_detailed_analysis_none_on_malformed(self):
        """_parse_response should return None for detailed_analysis when JSON is malformed."""
        diagnoser = AIDiagnoser()
        result = diagnoser._parse_response(  # pylint: disable=protected-access
            "This is not JSON"
        )
        assert result.get('detailed_analysis') is None


class TestAIDiagnoserGeminiFallback:
    """Tests for AIDiagnoser fallback to Gemini when OpenAI is unavailable."""

    def test_falls_back_to_gemini_when_openai_absent(self):
        """Should use Gemini when OPENAI_API_KEY is absent and GEMINI_API_KEY is set."""
        mock_response = '{"root_cause": "Config error", "remediation": "Fix config"}'
        env = {'OPENAI_API_KEY': '', 'GEMINI_API_KEY': 'test-gemini-key', 'OLLAMA_BASE_URL': ''}
        with patch.dict(os.environ, env):
            with patch('ai_engine.analyzers.gemini_analyzer.genai') as mock_genai:
                mock_client = MagicMock()
                mock_genai.Client.return_value = mock_client
                mock_client.models.generate_content.return_value = MagicMock(text=mock_response)
                diagnoser = AIDiagnoser()
                result = diagnoser.diagnose(SAMPLE_CONTEXT)
        assert result['root_cause'] == 'Config error'
        assert result['model_used'].startswith('gemini/')

    def test_suggest_returns_empty_string_without_provider(self):
        """suggest() should return empty string gracefully when no AI provider is available."""
        env = {'OPENAI_API_KEY': '', 'GEMINI_API_KEY': '', 'OLLAMA_BASE_URL': ''}
        with patch.dict(os.environ, env):
            diagnoser = AIDiagnoser()
            result = diagnoser.suggest("Explain this Kubernetes issue")
        assert isinstance(result, str)
