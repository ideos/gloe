# Utilities

```{admonition} API Reference
:class: seealso
- {func}`gloe.utils.forward`
- {func}`gloe.utils.attach`
- {func}`gloe.utils.forward_incoming`
- {data}`gloe.utils.forget`
- {func}`gloe.utils.debug`
```

## forward

The `forward` utility is used when your flow starts with a divergent connection. For example:

```python
from gloe.utils import forward

send_emails = forward[list[User]]() >> (
    filter_basic_subscription >> send_basic_subscription_promotion_email,
    filter_premium_subscription >> send_premium_subscription_promotion_email,
    filter_unsubscribed >> send_unsubscribed_promotion_email
)
```

In this case, we have nothing to do before splitting the groups of users. So, when starting the pipeline with a `forward` transformer, we are able to forward the incoming data to the next transformer directly.
```{important}
We have to explicitly define the incoming type of the forward transformer when it is used as the first step, because it is not known at the time of the definition.
```

## attach

Suppose you need to extract some statistics from a Pandas DataFrame. However, you still need the use the original data in the next transformers. In that case, you can use `attach`, which receives a transformer as an argument. The output of the `attach` is a tuple with the output of the encapsulated transformer and its input.

```python
get_data: Transformer[str, pd.DataFrame]
extract_statistics: Transformer[pd.DataFrame, Statistics]
process_statistics: Transformer[tuple[pd.DataFrame, Statistics], Result]

process_data = get_data >> attach(extract_statistics) >> process_statistics 
```

In the example above, both `get_data` and `extract_statistics` outputs are passed on as the input to `process_statistics`.

## forward_incoming

```{warning}
**Deprecated:** use `attach` instead.
```
## forget

Converts any input data to `None`. Quite useful in addition with {ref}`conditional-flows`.

## debug

It is quite useful when you want to see the flowing data at some points, for example:

```python
from gloe.utils import debug

send_emails = get_users >> filter_subscribed_users >> debug() >> send_subscribed_email
```

In this case, when calling `send_emails` in debugger mode, the processing will pause into the `debug` transformer. Then, we are able to see the output of the previous transformer (`filter_subscribed_users`) in the debug console.

```{Important}
This transformer is just a helper, you can keep adding breakpoints to any part of the transformers code as you are already used to.
```

```{Attention}
The execution will stop only if a debugger is active. In general, this verification is valid only under a debug mode in IDE.
```