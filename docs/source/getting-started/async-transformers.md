(async-transformers)=
# Async Transformers

```{admonition} API Reference
:class: seealso
- {func}`gloe.async_transformer`
- {func}`gloe.partial_async_transformer`
- {class}`gloe.AsyncTransformer`
```


Transformer can be also created from [coroutines](https://docs.python.org/3/library/asyncio-task.html#coroutines), but, in this case, you need to use the `@async_transformer` decorator. For example, consider the bellow transformer that fetchs data from an external http server:

```python
import httpx
from gloe import async_transformer

@async_transformer
async def fetch_data(resource: str) -> httpx.Response:
    async with httpx.AsyncClient() as client:
        r = await client.get(f'{BASE_URL}/{resource}')
    return r
```
The `@async_transformer` decorator converts the `fetch_data` function to an instance of the `AsyncTransformer` class.

To call this transformer, we need to use the `await` syntax, just like a normal coroutine:

```python
await fetch_data('users')
```

## Async Pipelines

An async transformer can be composed with other async transformers or with other sync transformers (normal transformers). For example:

```python
@async_transformer
async def get_user_by_id(user_id: int) -> User: ...

@transformer
def extract_user_roles(user: User) -> list[Role]: ...

get_user_roles = get_user_by_id >> extract_user_roles
```

When a pipeline has at least one async transformer, the entire pipeline becomes async, so we must call it using the `await` statement as well:

```python
await get_user_roles(user_id)
```

Alternatively, we can start the pipeline with a sync transformer and append an async transformer to it:

```python
@transformer
def extract_user_id(request: Request) -> int: ...

get_user = extract_user_id >> get_user_by_id
```

Briefly, you can mix async and sync transformers together without care about its concurrent nature, just about the types as before.

(partial-async-transformers)=
## Partial Async Transformers

As well as in sync transformers, you can create [partial transformers](/getting-started/partial-transformers) with an async behavoir. It can be done using the `@partial_async_transformer`:

```python
from gloe import partial_async_transformer

@partial_async_transformer
def get_users_by_role(role: str, page: int = 0, page_size: int = 10) -> Page[User]:
    "Get users with a specific role. The response is paginated."
    ...

```
