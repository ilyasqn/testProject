from typing import Annotated
from fastapi import APIRouter, Depends, Request
from fastapi.responses import JSONResponse
from src.schemas.requests import WebhookRequestSchema, WebhookResponseSchema
from src.services.webhook_service import WebhookService

from src.utils.unitofwork import UnitOfWork, IUnitOfWork
from src.services.webhook_service import WebhookService

from src.utils import exceptions
from loguru import logger

from src.limiter import limiter

router = APIRouter()


@router.post(
    "/webhook",
    response_model=WebhookResponseSchema,
    responses={
        **exceptions.BadRequestHTTPException.response()
    }
)
@limiter.limit("5/minute")
async def webhook_endpoint(
        request: Request,
        webhook: WebhookRequestSchema,
        uow: Annotated[IUnitOfWork, Depends(UnitOfWork)]
):
    response = await WebhookService.process_message(webhook.content, str(webhook.callback_url),
                                                    uow)  # receiving url then convert to str
    return JSONResponse(content={
        "status": "success",
        "message": response
    })


@router.post(
    "/test_callback_response",
    response_model=WebhookResponseSchema,
    responses={
        **exceptions.NotAcceptableHTTPException.response()
    }
)
async def test_callback_response(webhook_response: WebhookResponseSchema):
    logger.info(f"Received callback response: {webhook_response}")
    return WebhookResponseSchema(
        message_id=webhook_response.message_id,
        response=webhook_response.response
    )
