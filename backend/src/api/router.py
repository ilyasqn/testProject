from typing import Annotated
from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse
from src.schemas.test import TestSchemaRead
from src.services.test import TestService

from src.utils.unitofwork import UnitOfWork, IUnitOfWork

from src.utils import exceptions
from loguru import logger

from src.limiter import limiter

router = APIRouter()


@router.get(
    "/get_all_tests",
    response_model=list[TestSchemaRead],
    responses={
        **exceptions.BadRequestHTTPException.response()
    }
)
# @limiter.limit("5/minute")
async def get_tests(
        uow: Annotated[IUnitOfWork, Depends(UnitOfWork)]
):
    tests = await TestService.get_all_tests(uow)
    return tests
