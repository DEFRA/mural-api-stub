from typing import Any

import pydantic


class WidgetsResponse(pydantic.BaseModel):
    value: list[dict[str, Any]]
    next: str | None = None
