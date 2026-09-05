# Configured transformer factories

Use a normal factory when its parameters are ordinary Python arguments. Use
`@gloe.transformer` when keyword-only parameters are configuration that should
be bound before the data enters a pipeline.

```python
import gloe


def deliver(template: str, address: str) -> str:
    return f"{template}:{address}"


@gloe.transformer
def send_email(value: str, *, template: str) -> str:
    return deliver(template, value)


send_welcome = send_email(template="welcome")
pipeline = gloe.input[str]() >> send_welcome
result = pipeline.sync("ana@example.com")  # "welcome:ana@example.com"
```

After `template` is bound, `send_welcome` is an ordinary callable with the
unary input contract. It can be reused in several pipelines. The factory does
not hold invocation-specific state.

For a stage without configuration, prefer a plain function. A decorated
no-configuration stage is still a factory and must be called as `stage()` before
composition.

When a factory returns a whole pipeline, keep that pipeline's data contract
explicit and let the caller choose its input anchor:

```python
def for_department(template: str):
    return gloe.input[str]() >> send_email(template=template)


department_pipeline = for_department("reminder")
result = department_pipeline.sync("ana@example.com")  # "reminder:ana@example.com"
```
