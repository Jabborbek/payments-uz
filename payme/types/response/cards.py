import typing as t
import inspect
from dataclasses import dataclass


@dataclass
class Common:
    @classmethod
    def from_dict(cls, data: t.Dict):
        field_values = {}
        for field in cls.__dataclass_fields__:
            field_type = cls.__dataclass_fields__[field].type
            field_data = data.get(field)

            if isinstance(field_data, dict) and inspect.isclass(field_type) and issubclass(field_type, Common):
                field_values[field] = field_type.from_dict(field_data)
            else:
                field_values[field] = field_data

        return cls(**field_values)


@dataclass
class Card(Common):
    number: str
    expire: str
    token: str
    recurrent: bool
    verify: bool
    type: str
    number_hash: t.Optional[str] = None


@dataclass
class Result(Common):
    card: Card


@dataclass
class CardsCreateResponse(Common):
    jsonrpc: str
    result: Result


@dataclass
class VerifyResult(Common):
    sent: bool
    phone: str
    wait: int


@dataclass
class GetVerifyResponse(Common):
    jsonrpc: str
    result: VerifyResult


@dataclass
class VerifyResponse(Common):
    jsonrpc: str
    result: Result


@dataclass
class RemoveCardResult(Common):
    success: bool


@dataclass
class RemoveResponse(Common):
    jsonrpc: str
    result: RemoveCardResult


@dataclass
class CheckResponse(Common):
    jsonrpc: str
    result: Result
