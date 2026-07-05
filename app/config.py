import logging
from typing import Annotated

import pydantic
import pydantic_settings

logger = logging.getLogger(__name__)

class AppConfig(pydantic_settings.BaseSettings):
    model_config = pydantic_settings.SettingsConfigDict()
    python_env: str | None = None
    host: str = "127.0.0.1"
    port: int = 8086
    log_config: str | None = None
    mongo_uri: str | None = None
    mongo_database: str = "mural-api-stub"
    mongo_truststore: str = "TRUSTSTORE_CDP_ROOT_CA"
    floci_endpoint_url: str | None = None
    aws_region: str = pydantic.Field(
        default="eu-west-2", description="AWS region for Bedrock and other services"
    )
    http_proxy: pydantic.HttpUrl | None = None
    enable_metrics: bool = False
    tracing_header: str = "x-cdp-request-id"
    

_config: AppConfig | None = None


def get_config() -> AppConfig:
    global _config

    if _config is not None:
        return _config

    try:
        _config = AppConfig()  # type: ignore[call-arg]
        return _config
    except pydantic.ValidationError as e:
        error_details = [
            {
                "field": ".".join(str(loc) for loc in error["loc"]),
                "type": error["type"],
                "message": error["msg"],
            }
            for error in e.errors()
        ]

        error_strings = [
            f"Field '{error['field']}' {error['message']}" for error in error_details
        ]

        msg = f"Config validation failed with errors: {', '.join(error_strings)}"
        logger.error(msg)
        raise RuntimeError(msg) from None
