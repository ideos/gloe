# API Reference

## Packages

```{toctree}
:maxdepth: 4

gloe <self>
gloe.collection
gloe.gateways
gloe.utils
gloe.experimental
```

## Module contents

### Decorators

```{eval-rst}
.. autodecorator:: gloe.transformer
.. autodecorator:: gloe.async_transformer
.. autodecorator:: gloe.partial_transformer
.. autodecorator:: gloe.partial_async_transformer
.. autodecorator:: gloe.condition
.. autodecorator:: gloe.ensure
```

### Classes

```{eval-rst}
.. autoclass:: gloe.BaseTransformer
   :members:
   :show-inheritance:
.. autoclass:: gloe.Transformer
   :members:
   :show-inheritance:
.. autoclass:: gloe.AsyncTransformer
   :members:
   :show-inheritance:
.. autoclass:: gloe.If
   :members:
   :show-inheritance:
```

### Exceptions
```{eval-rst}
.. autoexception:: gloe.TransformerException
.. autoexception:: gloe.UnsupportedTransformerArgException
```