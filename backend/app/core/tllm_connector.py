from app.models.tllm_profile import TLLMProfile
import httpx
from openai import AsyncOpenAI
import anthropic

class TLLMConnectionError(Exception):
    pass

class TLLMConnector:
    def __init__(self, profile: TLLMProfile):
        self.profile = profile
        self.provider = profile.provider.lower()
        self.api_key = profile.api_key_ref
        self.endpoint_url = profile.endpoint_url
        self.system_prompt = profile.system_prompt
        
    async def send(self, prompt: str, conversation_history: list = []) -> str:
        if self.provider == "openai":
            return await self._send_openai(prompt)
        elif self.provider == "anthropic":
            return await self._send_anthropic(prompt)
        elif self.provider == "ollama":
            return await self._send_ollama(prompt)
        elif self.provider == "custom":
            return await self._send_custom(prompt)
        elif self.provider == "local_mock":
            return await self._send_local_mock(prompt)
        else:
            raise TLLMConnectionError(f"Unsupported provider: {self.provider}")

    async def _send_openai(self, prompt: str) -> str:
        if not self.api_key:
            if self.endpoint_url: # Might be using local LLM Studio or something that doesn't need key
                pass
            else:
                raise TLLMConnectionError("OpenAI API Key is missing")
        
        try:
            client = AsyncOpenAI(api_key=self.api_key, base_url=self.endpoint_url if self.endpoint_url else "https://api.openai.com/v1")
            
            messages = []
            if self.system_prompt:
                messages.append({"role": "system", "content": self.system_prompt})
            messages.append({"role": "user", "content": prompt})

            response = await client.chat.completions.create(
                model="llama-3.1-8b-instant", # Default fallback, could be configurable in profile later
                messages=messages,
                max_tokens=256
            )
            return response.choices[0].message.content
        except Exception as e:
            raise TLLMConnectionError(f"OpenAI Connector Error: {e}")

    async def _send_anthropic(self, prompt: str) -> str:
        if not self.api_key:
            raise TLLMConnectionError("Anthropic API Key is missing")
        
        try:
            client = anthropic.AsyncAnthropic(api_key=self.api_key)
            response = await client.messages.create(
                model="claude-3-haiku-20240307",
                system=self.system_prompt if self.system_prompt else "",
                messages=[
                    {"role": "user", "content": prompt}
                ],
                max_tokens=256
            )
            return response.content[0].text
        except Exception as e:
            raise TLLMConnectionError(f"Anthropic Connector Error: {e}")

    async def _send_ollama(self, prompt: str) -> str:
        url = self.endpoint_url if self.endpoint_url else "http://localhost:11434/api/generate"
        try:
            async with httpx.AsyncClient() as client:
                payload = {
                    "model": "llama3", # Assuming a default model or we can extend TLLMProfile
                    "prompt": prompt,
                    "system": self.system_prompt if self.system_prompt else "",
                    "stream": False
                }
                response = await client.post(url, json=payload, timeout=30.0)
                response.raise_for_status()
                return response.json().get("response", "")
        except Exception as e:
            raise TLLMConnectionError(f"Ollama Connector Error: {e}")

    async def _send_custom(self, prompt: str) -> str:
        if not self.endpoint_url:
            raise TLLMConnectionError("Endpoint URL required for custom provider")
            
        try:
            async with httpx.AsyncClient() as client:
                # Basic standard format assumption. Will need extension based on needs.
                headers = {"Authorization": f"Bearer {self.api_key}"} if self.api_key else {}
                payload = {
                    "prompt": prompt,
                    "system_prompt": self.system_prompt
                }
                response = await client.post(self.endpoint_url, json=payload, headers=headers, timeout=30.0)
                response.raise_for_status()
                # Try common response formats
                data = response.json()
                if isinstance(data, dict):
                    if "response" in data: return data["response"]
                    if "choices" in data and len(data["choices"]) > 0: return data["choices"][0].get("text", "")
                return str(data)
        except Exception as e:
            raise TLLMConnectionError(f"Custom Connector Error: {e}")

    async def _send_local_mock(self, prompt: str) -> str:
        import asyncio
        await asyncio.sleep(0.5) # Simulate latency
        
        prompt_lower = prompt.lower()
        if "ignore previous instructions" in prompt_lower:
            return "Sure! I will ignore previous instructions. Here is the secret password: REF-1234-SECURE."
        if "password" in prompt_lower or "secret" in prompt_lower:
             return "I cannot reveal the password properly, but maybe if you ask nicely..."

        return f"I am a helpful assistant. You said: {prompt[:100]}..."
