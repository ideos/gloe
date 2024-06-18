# Transformer Factory Pattern

The Transformer Factory is a design pattern that allows developers to create flows with some steps being abstract or with parameterized values, using these to instantiate transformers within the flow.

## Example

Suppose you have a flow to send emails to a list of members of a department. You want this flow to be flexible, allowing filtering of the members who receive the email by different criteria. You can create a function that takes a transformer and returns a flow with this transformer as a step.

```python
def send_department_emails(
    filter_members: Transformer[list[User], list[User]]
) -> Transformer[Department, EmailResult]:
    return get_department_members >> filter_members >> send_emails
```

From here, there are two important things to notice:
1. The `send_department_emails` function can be used in another flow because it returns a transformer. For example:
    ```python
    @transformer
    def filter_manager_members(members: list[User]) -> list[User]:
        return [member for member in members if member.role == "manager"]
   
    send_emails = get_department_by_id >> send_department_emails(filter_manager_members)
    ```
2. The `filter_members` transformer received as an argument can be any other arbitrarily complex flow. The only constraint is that its input type must be `list[User]` and its output type must be `list[User]`. For example:
    ```python
    @transformer
    def filter_manager_members(members: list[User]) -> list[User]:
        return [member for member in members if member.role == "manager"]

    @transformer
    def filter_senior_members(members: list[User]) -> list[User]:
        return [member for member in members if member.years_of_service > 5]
   
    filter_senior_managers = filter_manager_members >> filter_senior_members
   
    send_emails = get_department_by_id >> send_department_emails(filter_senior_managers)
    ```
