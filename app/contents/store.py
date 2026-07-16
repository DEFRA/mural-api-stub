from typing import Any

from app.common import s3
from app.murals import store


class ContentsStore:
    """S3-backed reader for a mural's stored widgets."""

    def __init__(self, s3_client: Any, bucket: str) -> None:
        self._s3_client = s3_client
        self._bucket = bucket

    async def get_widgets(self, mural_id: store.MuralId) -> list[dict[str, Any]] | None:
        data = await s3.get_json_object(
            self._s3_client, self._bucket, f"{mural_id.s3_prefix}/widgets.json"
        )

        if data is None:
            return None

        if isinstance(data, list):
            return data

        widgets: list[dict[str, Any]] = data.get("value", [])
        return widgets
