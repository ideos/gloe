# Transformer Factory Pattern

The Transformer Factory is a design pattern that allows the developer to create flow with some steps being abstracts or with parameterized values using to instantiate transformers within the flow.

## Basic Example

Suppose you have a flow to send emails to a list of members of some department, but you want to let this flow flexible allowing to filter the members to receive the email by another criteria. You can create a function that receives a transformer any returns a flow with this transformer as a step.

```python
def send_department_emails(
    filter_members: Transformer[list[User], list[User]]
) -> Transformer[Department, EmailResult]:
    return get_department_members >> filter_members >> send_emails
```

From here, there are two important things to notice:
1. The `send_department_emails` function can be called into another flow be cause it returns a transformer. For example:
    ```python
    @transformer
    def filter_manager_members(members: list[User]) -> list[User]:
        return [member for member in members if member.role == "manager"]
   
    send_emails = get_department_by_id >> send_department_emails(filter_manager_members)
    ```
2. The `filter_members` transformer received as argument can be any other arbitrary complex flow. The only constraint is that its incoming type must be `list[User]` and its outcome type must be `list[User]`. For example:
    ```python
    @transformer
    def filter_manager_members(members: list[User]) -> list[User]:
        return [member for member in members if member.role == "manager"]

    @transformer
    def filter_female_members(members: list[User]) -> list[User]:
        return [member for member in members if member.gender == "female"]
   
    filter_female_managers = filter_manager_members >> filter_female_members
   
    send_emails = get_department_by_id >> send_department_emails(filter_female_managers)
    ```
