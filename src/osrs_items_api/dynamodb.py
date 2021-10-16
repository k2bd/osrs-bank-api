from decimal import Decimal
from typing import Any, Dict

import boto3

from osrs_items_api.constants import AWS_REGION, LOCAL_DYNAMODB_ENDPOINT


def dynamodb():
    config = {}
    if LOCAL_DYNAMODB_ENDPOINT is not None:
        config["endpoint_url"] = LOCAL_DYNAMODB_ENDPOINT
    elif AWS_REGION is not None:
        config["region_name"] = AWS_REGION
    else:
        msg = "Please set either AWS_REGION or LOCAL_DYNAMODB_ENDPOINT"
        raise EnvironmentError(msg)

    return boto3.resource("dynamodb", **config)


def from_dynamodb(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Convert from Decimal to the appropriate numerical form, etc
    """

    def convert_value(value: Any) -> Any:
        if isinstance(value, Decimal):
            if int(value) == value:
                return int(value)
            else:
                return float(value)
        else:
            return value

    return {k: convert_value(v) for k, v in data.items()}
