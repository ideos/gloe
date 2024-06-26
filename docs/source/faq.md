(faq)=
# FAQ

## General

### Which Python versions support Gloe?

Gloe can be used in projects running Python 3.9, 3.10, 3.11, and 3.12.

### Do I need to use type hints in my code?

According to our {ref}`philosophy <philosophy>`, Gloe is designed to be used with explicitly typed code. You can choose to ignore this and still take advantage of other Gloe features; however, you will be on your own path.

### Can I use a Python type checker other than Mypy?

Gloe utilizes the default Python typing features. Its compatibility depends on the capability and completeness of the type checker you wish to use. Gloe is fully tested only with Mypy, but you are encouraged to test it on alternative tools (like [Pyright](https://microsoft.github.io/pyright)) and provide us feedback.

### Do I need a Mypy plugin to use Gloe?

No. Gloe does not require any Mypy plugins.

### Is Gloe a workflow orchestrator?

Currently, unlike platforms like [Airflow](https://airflow.apache.org/) that include scheduler backends for task orchestration, Gloe's primary purpose is to aid in development. The graph structure aims to make the code [more flat and hence more readable](https://en.wikibooks.org/wiki/Computer_Programming/Coding_Style/Minimize_nesting). However, it is important to note that Gloe does not offer functionalities for executing tasks in a dedicated environment, nor does it directly contribute to execution speed or scalability improvements.

### Can I debug my code as I am used to?

Yes! Gloe does not change the standard debugging process. The {func}`gloe.utils.debug` utility is just an extra helper.

### Does Gloe have a limit on the number of nodes for the graph?

No. You can compose as many transformers as you want. The only current limitation of Gloe is the number of nested branches: you can't have more than approximately 350 nested branches (i.e., a branch that contains another branch, which in turn contains another branch, and so on). **This scenario is not feasible and is discouraged by Gloe principles.**

### Does Gloe make my code slower?

We are currently developing benchmarks to be published. However, we can provide a preliminary evaluation:

- **Task**: Simulate a computation with a duration of **2ms** 450 times.
- **Environment**: VM with 1 GB RAM, 25 GB Disk, Ubuntu 22.04 (LTS) x64, and a single CPU core. The command `pyperf system tune` from the [pyperf](https://github.com/psf/pyperf) library was applied before the tests.
- **Approach 1**: Use only a for loop.
  ```python
  def fake_computation():
    for _ in range(450):
        time.sleep(0.002) 
  ```
- **Approach 2**: Use a Gloe pipeline in which each operation is a transformer in a graph, resulting in **450 nodes**.
  ```python
  @transformer
  def fake_transformer(_):
      time.sleep(0.002)
  
  fake_computation = fake_transformer
  for _ in range(450 - 1):  # the above line already performs one operation 
      fake_computation = fake_computation >> fake_transformer
  ```
- **Test execution**: The test was executed using the pyperf library with the default number of loops, values and warmups.
- **Time difference**: Approach 2 (with Gloe) took about **9 milliseconds** longer:
    ```text
    +------------------+------------+----------------------+
    | Benchmark        | Approach 2 | Approach 1           |
    +==================+============+======================+
    | fake_computation | 883 ms     | 874 ms: 1.01x faster |
    +------------------+------------+----------------------+
    ```
    When running the same experiment with 100 nodes instead of 450, the difference is only **~1ms**.

We allow users to determine if the duration is excessive for their specific use cases.


## Good and Bad Practices


### What is the size of a transformer?
It depends (you were expecting that answer, right?). A single transformer can wrap the entire code of your flow, much like a Java main class can encompass an entire application. However, it is common practice to break our code into pieces to adhere to principles like [SOLID](https://en.wikipedia.org/wiki/SOLID) and [DDD](https://en.wikipedia.org/wiki/Domain-driven_design). In this spirit, we encourage developers to think of transformers as **units of responsibility**: a block that, at first glance, has a clear role in the flow, while involving aspects whose underlying details can be reserved for deeper analysis. So, in your context, the size of a transformer depends on the set of responsibilities you want to make explicit in your flow.

### Can I call a transformer inside another transformer?

```{note}
This case refers to the follwing:

```python
@transformer
def my_transformer():
    flow = foo_transformer >> bar_transformer
    return flow() # nested transformer call
``` 


**Definitely not!** As stated in {ref}`this section <flat-is-better-than-nested>` from the philosophy page, Gloe promotes flatness in code. Of course, a transformer can utilize other components in its logic, such as classes and objects, but all these components should work together to implement a single atomic responsibility: the transformer's responsibility. Thus, the code reader/maintainer does not want to find a whole separated flow being called in the middle of a transformer's logic.
