(gateways)=
# Gateways

```{admonition} API Reference
:class: seealso
- {func}`gloe.gateways.parallel`
- {func}`gloe.gateways.sequential`
```
## Parallel Gateway

When creating branches like below:

```python
get_posts_and_friends = get_user_by_id >> (
    fetch_user_posts,
    fetch_user_friends,
)
```

You are implicitly using the `gloe.gateways.parallel` gateway. So the above code has exactly the same behavior as following:


```python
from gloe.gateways import parallel

get_posts_and_friends = get_user_by_id >> parallel(
    fetch_user_posts,
    fetch_user_friends,
)
```
Currently, the parallelism of transformers is supported only by executing async transformers concurrently. So, if `fetch_user_posts` and `fetch_user_friends` are async transformers, they will be executed concurrently. If a mix of sync and async transformers are used, the async transformers will still run concurrently, but the sync transformers will run sequentially.

The important thing to notice here is that the parallelism refers to the fact that none of transformers used in the branches depends on the others, considering the order of execution. In future versions, we plan to support more complex parallelism strategies, like threads or using third-party libraries. If you keep the independent transformers into parallel branches, they will be able to run under really parallel mechanisms soon.

## Sequential Gateway

If you have transformers that don't depend on the output of the previous one but, for some reason, you want to run them sequentially, you can use the `gloe.gateways.sequential` gateway. For example:

```python
from gloe.gateways import sequential

write_on_disk = get_file_path >> sequential(
    delete_file_if_already_exists,
    write_file_on_disk,
    check_file_is_on_disk,
)
``` 

In the above case, all the transformers has only the file path as input, so they don't depend on the output of the previous one. But, due to IO operations, the transformers must be executed in order.

Some common use cases are IO calls, like writing something on the disk or on a database, or even when dealing with mutable object where you can alter its internal state by reference.

```{note}
We have plans to support more gateway types in the future.
```