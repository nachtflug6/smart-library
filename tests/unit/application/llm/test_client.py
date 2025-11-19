# Python
def test_chat_uses_default_model_and_returns_response():
    from smart_library.llm.client import LLMClient

    class FakeLLMClient(LLMClient):
        def __init__(self, api_key: str, default_model: str, response: str):
            super().__init__(api_key=api_key, default_model=default_model)
            self.response = response
            self.last_call = None

        def _call_api(
            self,
            model: str,
            messages,
            temperature: float,
            max_output_tokens: int,
            **kwargs,
        ) -> str:
            self.last_call = {
                "model": model,
                "messages": messages,
                "temperature": temperature,
                "max_output_tokens": max_output_tokens,
                "kwargs": kwargs,
            }
            return self.response

    client = FakeLLMClient(api_key="k", default_model="model-x", response="response-default")
    messages = [{"role": "user", "content": "hi"}]

    result = client.chat(messages)

    assert result == "response-default"
    assert client.last_call is not None
    assert client.last_call["model"] == "model-x"
    assert client.last_call["messages"] is messages  # ensure same object is passed through
    assert client.last_call["temperature"] == 0.7
    assert client.last_call["max_output_tokens"] == 1024
    assert client.last_call["kwargs"] == {}


def test_chat_overrides_model_and_forwards_parameters():
    from smart_library.llm.client import LLMClient

    class FakeLLMClient(LLMClient):
        def __init__(self, api_key: str, default_model: str, response: str):
            super().__init__(api_key=api_key, default_model=default_model)
            self.response = response
            self.last_call = None

        def _call_api(
            self,
            model: str,
            messages,
            temperature: float,
            max_output_tokens: int,
            **kwargs,
        ) -> str:
            self.last_call = {
                "model": model,
                "messages": messages,
                "temperature": temperature,
                "max_output_tokens": max_output_tokens,
                "kwargs": kwargs,
            }
            return self.response

    client = FakeLLMClient(api_key="k", default_model="model-x", response="response-override")
    messages = [{"role": "user", "content": "config"}]

    result = client.chat(messages, model="model-y", temperature=1.2, max_output_tokens=42)

    assert result == "response-override"
    assert client.last_call is not None
    assert client.last_call["model"] == "model-y"
    assert client.last_call["messages"] is messages
    assert client.last_call["temperature"] == 1.2
    assert client.last_call["max_output_tokens"] == 42
    assert client.last_call["kwargs"] == {}


def test_chat_forwards_arbitrary_kwargs():
    from smart_library.llm.client import LLMClient

    class FakeLLMClient(LLMClient):
        def __init__(self, api_key: str, default_model: str, response: str):
            super().__init__(api_key=api_key, default_model=default_model)
            self.response = response
            self.last_call = None

        def _call_api(
            self,
            model: str,
            messages,
            temperature: float,
            max_output_tokens: int,
            **kwargs,
        ) -> str:
            self.last_call = {
                "model": model,
                "messages": messages,
                "temperature": temperature,
                "max_output_tokens": max_output_tokens,
                "kwargs": kwargs,
            }
            return self.response

    client = FakeLLMClient(api_key="k", default_model="model-x", response="response-kwargs")
    messages = [{"role": "system", "content": "policy"}]

    extra_kwargs = {"top_p": 0.9, "user": "abc", "response_format": "json"}
    result = client.chat(messages, **extra_kwargs)

    assert result == "response-kwargs"
    assert client.last_call is not None
    assert client.last_call["kwargs"] == extra_kwargs