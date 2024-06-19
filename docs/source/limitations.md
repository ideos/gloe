
# Limitations

(work-in-progress)=
## Work in progress

The bellow limitations are already being investigated and will be released in the next versions.

- **Parallel execution**: branches in a graph are not executed in parallel nor concurrently yet.

## Python limitations

The following limitations are inherited from Python and can be only solved when it is solved by the language or resorting to the use of third-party workarounds.

- **Overload transformers**: Python provide us a way to [overload function](https://docs.python.org/3/library/typing.html#typing.overload) definitions and [get its overloads](https://docs.python.org/3/library/typing.html#typing.get_overloads) at execution time. However, apparently, there is no way to forward all this overloads to a complex structure created from the overloaded function (like transformers). It is possible to be done considering only the execution but the type checker will not be aware of the overloads.

- **Higher-Kinded Types**: this is a feature of strong typed languages, like [Scala](https://www.baeldung.com/scala/higher-kinded-types), [Haskell](https://serokell.io/blog/kinds-and-hkts-in-haskell) and [Rust](https://hugopeters.me/posts/14/). However, even in Typescript there is an [open issue](https://github.com/microsoft/TypeScript/issues/1213) for that and in Java this must be [simulated](https://medium.com/@johnmcclean/simulating-higher-kinded-types-in-java-b52a18b72c74). So, it was to be expected that we can't use it natively in Python yet. Although there already is [a workaround](https://returns.readthedocs.io/en/latest/pages/hkt.html) for that from the [Returns](https://returns.readthedocs.io) library, we didn't investigate a consistent way to integrate it to Gloe yet.