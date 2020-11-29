### maybe_async
An experimental attempt to abstract away async/await semantics

#### Usage:
```python
import requests
import aiohttp
from maybe_async import maybe_async

@maybe_async
def fetch_data(client):
    resp = client.get('http://httpbin.org/get')
    return resp.json()

async def main():
    with requests.Session() as session:
        result = fetch_data(session)
        print(result)

    async with aiohttp.ClientSession() as session:
        result = await fetch_data(session)
        print(result)

asyncio.run(main())
```
