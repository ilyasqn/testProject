import datetime
from typing import Annotated

from sqlalchemy import text, DateTime, String
from sqlalchemy.orm import mapped_column


str_email_c = Annotated[str, mapped_column(String(512))]
int_pk_c = Annotated[int, mapped_column(primary_key=True)]
created_at_c = Annotated[datetime.datetime, mapped_column(server_default=text("TIMEZONE('utc', now())"))]
updated_at_c = Annotated[datetime.datetime, mapped_column(
    server_default=text("TIMEZONE('utc', now())"), onupdate=datetime.datetime.now())]
datetime_c = Annotated[datetime.datetime, mapped_column(DateTime(timezone=False))]
