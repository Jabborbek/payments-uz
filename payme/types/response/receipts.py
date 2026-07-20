import inspect
import typing as t

from dataclasses import dataclass


@dataclass
class Common:
    jsonrpc: str
    id: int

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
class Account(Common):
    _id: str
    account_number: str
    account_name: str
    account_type: str
    bank_name: str
    currency: str
    status: str


@dataclass
class PaymentMethod(Common):
    name: str
    title: str
    value: str
    main: t.Optional[bool] = None


@dataclass
class Detail(Common):
    discount: t.Optional[str] = None
    shipping: t.Optional[str] = None
    items: t.Optional[str] = None


@dataclass
class MerchantEpos(Common):
    eposId: str
    eposName: str
    eposType: str
    eposTerminalId: str


@dataclass
class Meta(Common):
    source: t.Any = None
    owner: t.Any = None
    host: t.Any = None


@dataclass
class Merchant:
    _id: str
    name: str
    organization: str
    address: t.Optional[str] = None
    business_id: t.Optional[str] = None
    epos: t.Optional[MerchantEpos] = None
    restrictions: t.Optional[str] = None
    date: t.Optional[int] = None
    logo: t.Optional[str] = None
    type: t.Optional[str] = None
    terms: t.Optional[str] = None


@dataclass
class Payer(Common):
    phone: str


@dataclass
class Receipt(Common):
    _id: str
    create_time: int
    pay_time: int
    cancel_time: int
    state: int
    type: int
    external: bool
    operation: int
    error: t.Any = None
    description: t.Optional[str] = None
    detail: t.Optional[Detail] = None
    currency: t.Optional[int] = None
    commission: t.Optional[int] = None
    card: t.Optional[str] = None
    creator: t.Optional[str] = None
    payer: t.Optional[Payer] = None
    amount: t.Optional[t.Union[float, int]] = None
    account: t.Optional[t.List[Account]] = None
    merchant: t.Optional[Merchant] = None
    processing_id: t.Optional[str] = None
    meta: t.Optional[Meta] = None


@dataclass
class CreateResult(Common):
    receipt: Receipt


@dataclass
class CreateResponse(Common):
    result: CreateResult


@dataclass
class PayResponse(CreateResponse):
    pass


@dataclass
class SendResult(Common):
    success: bool


@dataclass
class SendResponse(Common):
    result: SendResult


@dataclass
class CancelResponse(CreateResponse):
    pass


@dataclass
class CheckResult(Common):
    state: int


@dataclass
class CheckResponse(Common):
    result: CheckResult


@dataclass
class GetResponse(CreateResponse):
    pass


@dataclass
class GetAllResponse(Common):
    result: list[Receipt] = None


@dataclass
class SetFiscalDataResponse(Common):
    result: SendResult
