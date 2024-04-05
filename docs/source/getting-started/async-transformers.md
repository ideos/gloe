# Async Transformers

```python
import httpx
from gloe import async_transformer

@async_transformer
async def fetch_data(resource: str) -> Response:
    async with httpx.AsyncClient() as client:
        r = await client.get(f'{BASE_URL}/{resource}')
    return r
```