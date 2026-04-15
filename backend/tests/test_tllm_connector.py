import pytest
from app.core.tllm_connector import TLLMConnector, TLLMConnectionError
from app.models.tllm_profile import TLLMProfile

@pytest.mark.asyncio
async def test_openai_missing_key():
    profile = TLLMProfile(id="1", name="Test", provider="openai")
    connector = TLLMConnector(profile)
    with pytest.raises(TLLMConnectionError):
        await connector.send("Hello")

@pytest.mark.asyncio
async def test_ollama_custom_endpoint():
    profile = TLLMProfile(id="2", name="Ollama Test", provider="ollama", endpoint_url="http://invalid-url-for-test.xyz")
    connector = TLLMConnector(profile)
    # Should throw httpx connect error or similar, wrapped in TLLMConnectionError
    with pytest.raises(TLLMConnectionError):
        await connector.send("Hello")
