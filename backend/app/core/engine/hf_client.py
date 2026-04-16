"""HuggingFace Inference Endpoint wrapper — used by Mutation Engine for paraphrase + translation strategies."""
import httpx
from app.config import settings


class HFClientError(Exception):
    pass


class HFClient:
    def __init__(self, token: str | None = None, timeout: float = 30.0):
        self.token = token or settings.HF_API_TOKEN
        self.timeout = timeout

    @property
    def available(self) -> bool:
        return bool(self.token)

    async def _post(self, endpoint: str, payload: dict) -> list | dict:
        if not self.token:
            raise HFClientError("HF_API_TOKEN not configured")
        headers = {"Authorization": f"Bearer {self.token}"}
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            resp = await client.post(endpoint, json=payload, headers=headers)
        if resp.status_code >= 400:
            raise HFClientError(f"HF endpoint {resp.status_code}: {resp.text[:200]}")
        return resp.json()

    async def paraphrase(self, text: str) -> str:
        data = await self._post(settings.HF_PARAPHRASE_ENDPOINT, {"inputs": text})
        if isinstance(data, list) and data and isinstance(data[0], dict):
            return data[0].get("generated_text", text)
        return text

    async def translate_round_trip(self, text: str) -> str:
        forward = await self._post(settings.HF_TRANSLATE_EN_FR_ENDPOINT, {"inputs": text})
        intermediate = forward[0]["translation_text"] if isinstance(forward, list) else text
        back = await self._post(settings.HF_TRANSLATE_FR_EN_ENDPOINT, {"inputs": intermediate})
        return back[0]["translation_text"] if isinstance(back, list) else text
