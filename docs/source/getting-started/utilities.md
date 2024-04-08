# Utilities

## forward

The `forward` utility is quite useful when your flow starts with a divergent connection. For example:

```python
from gloe.utils import forward

send_emails = forward[list[User]]() >> (
    filter_basic_subscription >> send_basic_subscription_promotion_email,
    filter_premium_subscription >> send_premium_subscription_promotion_email,
    filter_unsubscribed >> send_unsubscribed_promotion_email
)
```

In this case, we have nothing to do before split the groups of users. So, when starting the pipeline with `forward` transformer, we are able to forward the incoming data to the next transformer directly.
```{important}
We have to explicitly define the incoming type of the forward transformer when it is used as the first step, because it is not known at the time of the definition.
```

## forward_incoming


## forget

It converts any input data to `None`.

## debug

It is quite useful when you want to see the flowing data at some points, for example:

```python
from gloe.utils import debug

send_emails = 
```
```{danger}
You must not deploy a pipeline containing this transformer to a production environment.
```