(collectiosn)=
# Collections

```{admonition} API Reference
:class: seealso
- {class}`gloe.collection.Map`
- {class}`gloe.collection.Filter`
- {class}`gloe.collection.MapOver`
```

Gloe provides a way to work of collections of data in a functional way, but using transformers instead of functions. The `Map`, `Filter`, and `MapOver` classes are the main tools to work with collections.

## Map

The {class}`gloe.collection.Map` class is used to apply a transformer to each element of a collection. For example, consider we have a list of users and we want to get the age of each one:

```python
from gloe import transformer
from gloe.collection import Map

@transformer
def get_user_age(user: User) -> int:
    return user.age

get_users_ages = Map(get_user_age)  # Transformer[Iterable[User], Iterable[int]]

get_users_ages([
    User(name='Anny', age=16),
    User(name='Alice', age=25),
    User(name='Bob', age=30)
])  # returns [16, 25, 30]
```

## Filter

The {class}`gloe.collection.Filter` class is used to filter elements of a collection. For example, consider the same previous list of users and we want to filter only the ones older than 18:

```python
from gloe import transformer
from gloe.collection import Filter

@transformer
def is_older_than_18(user: User) -> bool:
    return user.age > 18

filter_older_than_18 = Filter(is_older_than_18)  # Transformer[Iterable[User], Iterable[User]]

filter_older_than_18([
    User(name='Anny', age=16),
    User(name='Alice', age=25),
    User(name='Bob', age=30)
]) # returns [User(name='Alice', age=25), User(name='Bob', age=30)]
```

We can also do both:
```python
get_ages_greater_than_18 = Filter(is_older_than_18) >> Map(get_user_age)

get_ages_greater_than_18([
    User(name='Anny', age=16),
    User(name='Alice', age=25),
    User(name='Bob', age=30)
]) # returns [25, 30]
```

## MapOver

The {class}`gloe.collection.MapOver` class is used zip the input collection with a static collection passed as argument during the instantiation.
For example, consider the same previous list of users, we want to zip each user with a static list of roles, then format the user's name with the role name:

```python
from gloe import transformer
from gloe.collection import MapOver

roles: list[Role] = [admin_role, member_role, manager_role]

@transformer
def format_user(entry: tuple[User, Role]) -> str:
    user, role = entry
    return f'{user.name} is {role.name}'

format_users = MapOver(roles, format_user)  # Transformer[Iterable[User], Iterable[str]]

format_users([
    User(name='Anny', age=16),
    User(name='Alice', age=25),
    User(name='Bob', age=30)
]) # returns ['Anny is admin', 'Alice is member', 'Bob is manager']
```
