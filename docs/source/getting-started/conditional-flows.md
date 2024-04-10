(conditional-flows)=
# Conditional Flows

```{admonition} API Reference
:class: seealso
- {func}`gloe.condition`
- {class}`gloe.If`
```

Often you need to write a flow with some conditions. For example, suppose you need to send a specific email to administrator users and another email to non-administrator users:

```python
from gloe.conditional import condition

@condition
def is_admin(user: User) -> bool:
    return "admin" in user.roles

send_email = (
    is_admin
    .Then(fetch_admin_data >> send_admin_email)
    .Else(send_member_email)
)

send_email_to_user = get_user_by_id >> send_email

...

send_email_to_user(user_id)
```
> `fetch_admin_data`, `send_admin_email`, `send_member_email` and `get_user_by_id` are transformers.

In the above example, the `@condition` decorator converts the `is_admin` function to a `Condition`. It allows us to use the `.Then` method, which receives a transformer as an argument. You have to finish the condition chain with an `.Else`, which also receives a transformer as an argument.

Another way to write the given flow is using the `If` class with a lambda function:

```python
from gloe.conditional import If

send_email = (
    If(lambda user: "admin" in user.roles)
        .Then(fetch_admin_data >> send_admin_email)
    .Else(send_member_email)
)

send_email_to_user = get_user_by_id >> send_email
```

## Chaining Many Conditions

Suppose now we have to send another type of email to users with a "manager" role, we can adapt that flow to send this specific email to that users using the `.ElseIf` method:

```python
from gloe.conditional import If

send_email = (
    If(lambda user: "admin" in user.roles)
        .Then(fetch_admin_data >> send_admin_email)
    .ElseIf(lambda user: "manager" in user.roles)
        .Then(fetch_manager_data >> send_manager_email)
    .Else(send_member_email)
)

send_email_to_user = get_user_by_id >> send_email
```
```{tip}
You can chain as many `ElseIf`'s as you want.
```

## Understanding the Types

Assume the below transformers and conditions:

```python
condition1: Callable[[In], bool]
then_transformer1: Transformer[In, Out1]
condition2: Callable[[In], bool]
then_transformer2: Transformer[In, Out2]
...
conditionN: Callable[[In], bool]
then_transformerN: Transformer[In, OutN]
else_transformer: Transformer[In, ElseOut]
```

Lets chain the conditions:
```python
chained_conditions = (
    If(condition1).Then(then_transformer1)
    .ElseIf(condition2).Then(then_transformer2)
    ...
    .ElseIf(conditionN).Then(then_transformerN)
    .Else(else_transformer)
)
```

The type of `chained_conditions` is:
```python
Transformer[In, Out1 | Out2 | ... | OutN | ElseOut]
```

It means, the transformer after the `chained_conditions` must be able to deal with all possible output types of the cases.

```{hint}
If you are not familiar with the type annotation syntax used above, we strongly recommend you to read the [Mypy types documentation](https://mypy.readthedocs.io/en/stable/builtin_types.html).
```