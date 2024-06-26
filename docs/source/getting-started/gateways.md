(gateways)=
# Gateways

```{admonition} API Reference
:class: seealso
- {func}`gloe.gateways.parallel`
- {func}`gloe.gateways.sequential`
```
## Parallel Gateway

When creating branches as shown below:


```python
get_posts_and_friends = get_user_by_id >> (
    fetch_user_posts,
    fetch_user_friends,
)
```

You are implicitly using the `gloe.gateways.parallel` gateway. The above code has the same behavior as the following:


```python
from gloe.gateways import parallel

get_posts_and_friends = get_user_by_id >> parallel(
    fetch_user_posts,
    fetch_user_friends,
)
```
Currently, the parallelism of transformers is supported only by executing async transformers concurrently. So, if `fetch_user_posts` and `fetch_user_friends` are async transformers, they will execute concurrently. If a mix of sync and async transformers are used, the async transformers will still run concurrently, but the sync transformers will run sequentially.

The key point to note is that parallelism means that none of the transformers used in the branches depend on the others, considering the order of execution. In future versions, we plan to support more complex parallelism strategies, such as using threads or third-party libraries. By keeping independent transformers in parallel branches, they will soon be able to run under truly parallel mechanisms.



## Sequential Gateway
If you have transformers that don't depend on the output of the previous one but need to be run sequentially for some reason, you can use the `gloe.gateways.sequential` gateway. For example:

```python
from gloe.gateways import sequential

write_on_disk = get_file_path >> sequential(
    delete_file_if_already_exists,
    write_file_on_disk,
    check_file_is_on_disk,
)
``` 

In this case, all the transformers only require the file path as input, so they don't depend on the output of the previous one. However, due to IO operations, the transformers must be executed in order.

Common use cases include IO operations, such as writing to disk or a database, or dealing with mutable objects where internal state changes by reference.


```{note}
We have plans to support more gateway types in the future.
```