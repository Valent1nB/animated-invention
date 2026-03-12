from fastapi import Response, status
from fastapi.responses import JSONResponse
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from fastapi_users.authentication.transport.base import (
    Transport,
    TransportLogoutNotSupportedError,
)
from fastapi_users.openapi import OpenAPIResponseType
from pydantic import BaseModel
from starlette.requests import Request


class BearerResponse(BaseModel):
    access_token: str
    token_type: str


class CustomHTTPBearer(HTTPBearer):
    async def __call__(  # type: ignore[override]
        self, request: Request
    ) -> str | None:
        """
        Workaround for Swagger UI login interface.

        FastAPI's HTTPBearer returns HTTPAuthorizationCredentials, but
        for application-level auth we only need the raw token string.
        Mypy complains because this intentionally narrows the return type.
        """
        credentials: HTTPAuthorizationCredentials | None = await super().__call__(request=request)
        return credentials.credentials if credentials else None


class HTTPBearerTransport(Transport):
    scheme: CustomHTTPBearer

    def __init__(self):
        self.scheme = CustomHTTPBearer(auto_error=False)

    async def get_login_response(self, token: str) -> Response:
        bearer_response = BearerResponse(access_token=token, token_type="bearer")
        return JSONResponse(bearer_response.model_dump())

    async def get_logout_response(self) -> Response:
        raise TransportLogoutNotSupportedError()

    @staticmethod
    def get_openapi_login_responses_success() -> OpenAPIResponseType:
        return {
            status.HTTP_200_OK: {
                "model": BearerResponse,
                "content": {
                    "application/json": {
                        "example": {
                            "access_token": "<token>",
                            "token_type": "bearer",
                        }
                    }
                },
            },
        }

    @staticmethod
    def get_openapi_logout_responses_success() -> OpenAPIResponseType:
        return {}
