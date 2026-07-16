import dataclasses
from typing import Any

from app.common import s3
from app.murals import errors


@dataclasses.dataclass(frozen=True)
class MuralId:
    """A stub mural identifier, encoding the S3 workspace/board location."""

    raw: str
    workspace_id: str
    board_id: str

    @classmethod
    def parse(cls, raw: str, default_workspace_id: str | None) -> MuralId:
        if "." in raw:
            workspace_id, board_id = raw.split(".", 1)
            return cls(raw=raw, workspace_id=workspace_id, board_id=board_id)

        if default_workspace_id is None:
            raise errors.MuralNotFoundError(raw)

        return cls(raw=raw, workspace_id=default_workspace_id, board_id=raw)

    @property
    def s3_prefix(self) -> str:
        return f"{self.workspace_id}/{self.board_id}"


class MuralStore:
    """S3-backed reader for a mural's stored board data."""

    def __init__(self, s3_client: Any, bucket: str) -> None:
        self._s3_client = s3_client
        self._bucket = bucket

    async def get_board(self, mural_id: MuralId) -> dict[str, Any] | None:
        data = await s3.get_json_object(
            self._s3_client, self._bucket, f"{mural_id.s3_prefix}/board.json"
        )

        if data is None:
            return None

        value: dict[str, Any] = data["value"]
        return value
