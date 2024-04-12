# Plotting the Graph ⚠

```{admonition} Under development
:class: danger

You should not use the plotting feature in a production enviroment. We are still developing and testing it.
```

Every transformer has a method `export`, which is used to export the transformer as graph using the [dot format](https://graphviz.org/doc/info/lang.html).

Assume the following graph:

```python
@transformer
def extract_role(request: Request) -> str: ...

@transformer
def get_users(role: str) -> list[User]: ...

@transformer
def filter_basic_subscription(users: list[User]) -> list[User]: ...

@transformer
def filter_premium_subscription(users: list[User]) -> list[User]: ...

@transformer
def filter_unsubscribed(users: list[User]) -> list[User]: ...

@transformer
def send_basic_subscription_promotion_email(users: list[User]) -> Result: ...

@transformer
def send_premium_subscription_promotion_email(users: list[User]) -> Result: ...

@transformer
def send_unsubscribed_promotion_email(users: list[User]) -> Result: ...

@transformer
def log_emails_result(results: tuple[Result, Result, Result]) -> None: ...


send_promotion = (
    extract_role >>
    get_users >> (
        filter_basic_subscription >> send_basic_subscription_promotion_email,
        filter_premium_subscription >> send_premium_subscription_promotion_email,
        filter_unsubscribed >> send_unsubscribed_promotion_email,
    ) >> log_emails_result
)
```

We can call the method `export` of the `send_promotion` transformer instance:
```python
send_promotion.export('send_promotion_graph.dot', with_edge_labels=True)
```
```{attention}
This feature requires the library [pygraphviz](https://pygraphviz.github.io).
```

Then, we can use any dot visualizer tool to plot the graph. For example, we can use [edotor.net](https://edotor.net/). We need just to copy the content of `send_promotion_graph.dot` file and paste it on edotor.net editor.

The resulted plot is:
![Graph for send_promotion](../_static/assets/graph_example.jpeg)
> [Click here](https://edotor.net/?engine=dot#strict%20digraph%20%22%22%20%7B%0A%09graph%20%5Bsplines%3Dortho%5D%3B%0A%09node%20%5Blabel%3D%22%5CN%22%5D%3B%0A%09%2299c6dd71-ff1a-4a99-b61b-a6ad27c70698%22%09%5Blabel%3Dlog_emails_result%2C%0A%09%09shape%3Dbox%5D%3B%0A%09%226fc26b89-244f-4f65-ad07-685b53fcf4e5%22%09%5Bheight%3D0.5%2C%0A%09%09label%3D%22%22%2C%0A%09%09shape%3Ddiamond%2C%0A%09%09width%3D0.5%5D%3B%0A%09%226fc26b89-244f-4f65-ad07-685b53fcf4e5%22%20-%3E%20%2299c6dd71-ff1a-4a99-b61b-a6ad27c70698%22%09%5Blabel%3D%22(Result%2C%20Result%2C%20Result)%22%5D%3B%0A%09%22fd136d17-ac70-46a5-80f0-ee2b68176ccf%22%09%5Blabel%3Dsend_basic_subscription_promotion_email%2C%0A%09%09shape%3Dbox%5D%3B%0A%09%22fd136d17-ac70-46a5-80f0-ee2b68176ccf%22%20-%3E%20%226fc26b89-244f-4f65-ad07-685b53fcf4e5%22%09%5Blabel%3DResult%5D%3B%0A%09%22a2e1458d-4bad-4a43-a931-65f05c318670%22%09%5Blabel%3Dfilter_basic_subscription%2C%0A%09%09shape%3Dbox%5D%3B%0A%09%22a2e1458d-4bad-4a43-a931-65f05c318670%22%20-%3E%20%22fd136d17-ac70-46a5-80f0-ee2b68176ccf%22%09%5Blabel%3D%22list%5BUser%5D%22%5D%3B%0A%09%2204df83ae-5eee-4ff1-900c-3b37156a4ea4%22%09%5Blabel%3Dget_users%2C%0A%09%09shape%3Dbox%5D%3B%0A%09%2204df83ae-5eee-4ff1-900c-3b37156a4ea4%22%20-%3E%20%22a2e1458d-4bad-4a43-a931-65f05c318670%22%09%5Blabel%3D%22list%5BUser%5D%22%5D%3B%0A%09%2241436403-56b6-4b1e-bda3-a2828871e354%22%09%5Blabel%3Dfilter_premium_subscription%2C%0A%09%09shape%3Dbox%5D%3B%0A%09%2204df83ae-5eee-4ff1-900c-3b37156a4ea4%22%20-%3E%20%2241436403-56b6-4b1e-bda3-a2828871e354%22%09%5Blabel%3D%22list%5BUser%5D%22%5D%3B%0A%09%22ba03301e-af31-4e36-abb4-6da5d21767e2%22%09%5Blabel%3Dfilter_unsubscribed%2C%0A%09%09shape%3Dbox%5D%3B%0A%09%2204df83ae-5eee-4ff1-900c-3b37156a4ea4%22%20-%3E%20%22ba03301e-af31-4e36-abb4-6da5d21767e2%22%09%5Blabel%3D%22list%5BUser%5D%22%5D%3B%0A%09%22f2707bfb-820c-442a-85dd-5e63fdf52f51%22%09%5Blabel%3Dextract_role%2C%0A%09%09shape%3Dbox%5D%3B%0A%09%22f2707bfb-820c-442a-85dd-5e63fdf52f51%22%20-%3E%20%2204df83ae-5eee-4ff1-900c-3b37156a4ea4%22%09%5Blabel%3Dstr%5D%3B%0A%09%22bc1d4b6e-b555-4b5c-bc83-6e7b5b5ce1b8%22%09%5Blabel%3Dsend_premium_subscription_promotion_email%2C%0A%09%09shape%3Dbox%5D%3B%0A%09%22bc1d4b6e-b555-4b5c-bc83-6e7b5b5ce1b8%22%20-%3E%20%226fc26b89-244f-4f65-ad07-685b53fcf4e5%22%09%5Blabel%3DResult%5D%3B%0A%09%2241436403-56b6-4b1e-bda3-a2828871e354%22%20-%3E%20%22bc1d4b6e-b555-4b5c-bc83-6e7b5b5ce1b8%22%09%5Blabel%3D%22list%5BUser%5D%22%5D%3B%0A%09%222a6b6f14-c99e-488a-83e6-6ff401ad5d6d%22%09%5Blabel%3Dsend_unsubscribed_promotion_email%2C%0A%09%09shape%3Dbox%5D%3B%0A%09%222a6b6f14-c99e-488a-83e6-6ff401ad5d6d%22%20-%3E%20%226fc26b89-244f-4f65-ad07-685b53fcf4e5%22%09%5Blabel%3DResult%5D%3B%0A%09%22ba03301e-af31-4e36-abb4-6da5d21767e2%22%20-%3E%20%222a6b6f14-c99e-488a-83e6-6ff401ad5d6d%22%09%5Blabel%3D%22list%5BUser%5D%22%5D%3B%0A%7D%0A) to see this graph on edotor.net.


```{important}
We are already working on a dedicated solution to visualize and interact with Gloe graphs.  
```
