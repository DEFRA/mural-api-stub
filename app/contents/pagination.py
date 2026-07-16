_DEFAULT_OFFSET = 0


def decode_cursor(cursor: str | None) -> int:
    """Decode a ``next`` token into an offset, raising ValueError if malformed."""

    if not cursor:
        return _DEFAULT_OFFSET

    message = f"Invalid pagination token: {cursor}"

    try:
        offset = int(cursor)
    except ValueError as exc:
        raise ValueError(message) from exc

    if offset < _DEFAULT_OFFSET:
        raise ValueError(message)

    return offset


def encode_cursor(offset: int) -> str:
    return str(offset)
