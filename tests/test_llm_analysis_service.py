"""
Unit tests for LLMAnalysisService fallback chain behavior.

The real OpenAI/OpenRouter client is never called — every test stubs
``_get_client`` with a fake whose ``chat.completions.create`` has a
scripted side effect (raise / return).
"""

from unittest.mock import MagicMock

from surfer.services.llm_analysis_service import LLMAnalysisService


class FakeResponse:
    def __init__(self, content="ok"):
        choice = MagicMock()
        choice.message.content = content
        self.choices = [choice]


def make_service(models, monkeypatch):
    """Build a service with a given model chain and a fake client."""
    svc = LLMAnalysisService()
    svc.models = models
    svc.api_key = "test-key"
    svc.base_url = "https://example.com/v1"
    svc.last_model = None

    fake_client = MagicMock()
    # Each test scripts its own side_effect on create().
    fake_client.chat.completions.create = MagicMock()
    monkeypatch.setattr(svc, "_get_client", lambda: fake_client)
    monkeypatch.setattr("surfer.services.llm_analysis_service.time.sleep", lambda s: None)
    return svc, fake_client


class TestParseModels:
    """LLM_MODEL comma-separated chain parsing."""

    def test_single_model(self):
        assert LLMAnalysisService.parse_models("gpt-4o-mini") == ["gpt-4o-mini"]

    def test_chain_with_spaces(self):
        result = LLMAnalysisService.parse_models("a, b,  c")
        assert result == ["a", "b", "c"]

    def test_ignores_empty_entries(self):
        result = LLMAnalysisService.parse_models("a,, ,b,,")
        assert result == ["a", "b"]

    def test_empty_string_returns_empty_list(self):
        assert LLMAnalysisService.parse_models("") == []
        assert LLMAnalysisService.parse_models(None) == []

    def test_free_router_is_preserved(self):
        result = LLMAnalysisService.parse_models("openai/gpt-oss-20b:free,openrouter/free")
        assert result == ["openai/gpt-oss-20b:free", "openrouter/free"]


class TestFallbackChain:
    """The analyze() loop tries models in order until one succeeds."""

    def test_returns_first_successful_model(self, monkeypatch):
        svc, fake_client = make_service(["model-a", "model-b"], monkeypatch)
        fake_client.chat.completions.create.side_effect = [RuntimeError("429"), FakeResponse("good")]
        result = svc.analyze("prompt")
        assert result == "good"
        assert svc.last_model == "model-b"
        assert fake_client.chat.completions.create.call_count == 2
        assert fake_client.chat.completions.create.call_args_list[0].kwargs["model"] == "model-a"
        assert fake_client.chat.completions.create.call_args_list[1].kwargs["model"] == "model-b"

    def test_stops_chain_after_first_success(self, monkeypatch):
        svc, fake_client = make_service(["model-a", "model-b", "model-c"], monkeypatch)
        fake_client.chat.completions.create.side_effect = [FakeResponse("good")]
        result = svc.analyze("prompt")
        assert result == "good"
        assert svc.last_model == "model-a"
        assert fake_client.chat.completions.create.call_count == 1

    def test_all_models_fail_returns_none(self, monkeypatch):
        svc, fake_client = make_service(["model-a", "model-b"], monkeypatch)
        fake_client.chat.completions.create.side_effect = [RuntimeError("429"), RuntimeError("404")]
        assert svc.analyze("prompt") is None
        assert svc.last_model is None
        assert fake_client.chat.completions.create.call_count == 2

    def test_resets_last_model_between_calls(self, monkeypatch):
        svc, fake_client = make_service(["model-a", "model-b"], monkeypatch)
        fake_client.chat.completions.create.side_effect = [FakeResponse("first")]
        assert svc.analyze("prompt-1") == "first"
        assert svc.last_model == "model-a"
        fake_client.chat.completions.create.side_effect = [RuntimeError("boom"), RuntimeError("boom")]
        assert svc.analyze("prompt-2") is None
        assert svc.last_model is None

    def test_system_prompt_is_included(self, monkeypatch):
        svc, fake_client = make_service(["model-a"], monkeypatch)
        fake_client.chat.completions.create.side_effect = [FakeResponse("ok")]
        svc.analyze("user-prompt", "system-prompt")
        kwargs = fake_client.chat.completions.create.call_args.kwargs
        assert kwargs["messages"][0] == {"role": "system", "content": "system-prompt"}
        assert kwargs["messages"][1] == {"role": "user", "content": "user-prompt"}

    def test_empty_models_returns_none_early(self, monkeypatch):
        """Empty chain returns None without touching the client."""
        svc, fake_client = make_service([], monkeypatch)
        assert svc.analyze("prompt") is None
        assert svc.last_model is None
        fake_client.chat.completions.create.assert_not_called()


class TestConfig:
    def test_is_configured_requires_key_and_url(self, monkeypatch):
        svc = LLMAnalysisService()
        svc.api_key = ""
        svc.base_url = "https://example.com"
        assert svc.is_configured() is False
        svc.api_key = "key"
        assert svc.is_configured() is True


class TestClientTimeout:
    """The OpenAI client must be built with the hardening timeout."""

    def test_client_constructed_with_timeout(self, monkeypatch):
        import openai
        import surfer.services.llm_analysis_service as mod

        captured = {}

        class FakeOpenAI:
            def __init__(self, *args, **kwargs):
                captured["kwargs"] = kwargs

        # Reset the module-level singleton so _get_client() builds a new client.
        LLMAnalysisService._client = None
        try:
            monkeypatch.setattr(openai, "OpenAI", FakeOpenAI)
            svc = LLMAnalysisService()
            svc.api_key = "k"
            svc.base_url = "https://openrouter.ai/api/v1"
            svc._get_client()
            assert captured["kwargs"]["timeout"] == mod.REQUEST_TIMEOUT_SECONDS
        finally:
            LLMAnalysisService._client = None
