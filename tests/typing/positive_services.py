"""Typed application ports: request handling and idempotent event ingestion."""

from dataclasses import dataclass
from typing import Protocol, assert_type

import gloe


@dataclass(frozen=True)
class Request:
    user_id: int
    token: str
    correlation_id: str


@dataclass(frozen=True)
class User:
    id: int
    name: str


@dataclass(frozen=True)
class Response:
    status: int
    body: str
    correlation_id: str


class Users(Protocol):
    async def fetch(self, user_id: int) -> User | None: ...


def authorized(request: Request) -> None:
    if request.token != "test-token":
        raise PermissionError("Invalid token")


@gloe.ensure(incoming=authorized)
def accept(request: Request) -> Request:
    return request


@gloe.transformer
async def lookup(request: Request, *, users: Users) -> User | None:
    return await users.fetch(request.user_id)


def respond(request: Request, user: User | None) -> Response:
    if user is None:
        return Response(404, "Not found", request.correlation_id)
    return Response(200, user.name, request.correlation_id)


def endpoint(users: Users) -> gloe.Transformer[[Request], Response]:
    result = (
        gloe.input()
        >> accept
        >> (gloe.input(), lookup(users=users))
        >> gloe.unpack(respond)
    )
    assert_type(result, gloe.Transformer[[Request], Response])
    return result


@dataclass(frozen=True)
class Event:
    id: str
    amount: int


@dataclass(frozen=True)
class Receipt:
    event_id: str
    total: int


class Ledger(Protocol):
    async def apply_once(self, event: Event) -> Receipt: ...


def valid_event(event: Event) -> None:
    if not event.id or event.amount <= 0:
        raise ValueError("Invalid event")


@gloe.transformer
@gloe.ensure(incoming=valid_event)
async def persist(event: Event, *, ledger: Ledger, attempts: int) -> Receipt:
    # Retry policy belongs to this application stage. Cancellation and unrelated
    # exceptions propagate; only the declared transient failure is retried.
    if attempts < 1:
        raise ValueError("attempts must be positive")
    for attempt in range(attempts):
        try:
            return await ledger.apply_once(event)
        except ConnectionError:
            if attempt + 1 == attempts:
                raise
    raise AssertionError("unreachable")


def ingestion(ledger: Ledger) -> gloe.Transformer[[Event], Receipt]:
    return gloe.input() >> persist(ledger=ledger, attempts=2)
