from typing import Annotated

from email_validator import EmailNotValidError, validate_email
from pydantic import AfterValidator, BaseModel


def _validate_email_address(value: str) -> str:
    local_part, separator, domain = value.strip().rpartition("@")
    is_local_domain = separator and domain.lower().endswith(".local")
    if is_local_domain:
        domain = domain[:-len(".local")] + ".example"
        value = f"{local_part}@{domain}"

    try:
        normalized = validate_email(value, check_deliverability=False).normalized
        return normalized[:-len(".example")] + ".local" if is_local_domain else normalized
    except EmailNotValidError as exc:
        raise ValueError(str(exc)) from exc


EmailAddress = Annotated[str, AfterValidator(_validate_email_address)]


class UserCreate(BaseModel):
    name: str
    email: EmailAddress
    password: str


class UserLogin(BaseModel):
    email: EmailAddress
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: dict


class UserOut(BaseModel):
    id: int
    name: str
    email: str
    role: str
    is_active: bool
