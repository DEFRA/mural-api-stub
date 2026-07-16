from typing import Any

import pydantic


class MuralResponse(pydantic.BaseModel):
    value: dict[str, Any]
