# coding:utf-8
"""
Copyright (year) Beijing Volcano Engine Technology Ltd.

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

     http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""

import datetime
import hashlib
import hmac
import logging
import typing
from urllib.parse import quote

import httpx

logger = logging.getLogger(__name__)

DEFAULT_SERVICE = "vefaas"
DEFAULT_VERSION = "2024-06-06"
DEFAULT_REGION = "cn-beijing"
HOST = "open.volcengineapi.com"
CONTENT_TYPE = "application/x-www-form-urlencoded"

ACTION_CONFIG_MAP = {
    "CreateSandbox": {"service": "vefaas", "version": "2024-06-06"},
    "KillSandbox": {"service": "vefaas", "version": "2024-06-06"},
    "DescribeSandbox": {"service": "vefaas", "version": "2024-06-06"},
    "SetSandboxTimeout": {"service": "vefaas", "version": "2024-06-06"},
    "ListSandboxes": {"service": "vefaas", "version": "2024-06-06"},
    "ListTriggers": {"service": "vefaas", "version": "2024-06-06"},
    "ListRoutes": {"service": "apig", "version": "2022-11-12"},
}


def norm_query(params: typing.Mapping[str, typing.Any]) -> str:
    parts = []
    for key in sorted(params.keys()):
        value = params[key]
        if isinstance(value, list):
            for item in value:
                parts.append(
                    f"{quote(str(key), safe='-_.~')}={quote(str(item), safe='-_.~')}"
                )
        else:
            parts.append(
                f"{quote(str(key), safe='-_.~')}={quote(str(value), safe='-_.~')}"
            )
    return "&".join(parts).replace("+", "%20")


def hmac_sha256(key: bytes, content: str) -> bytes:
    return hmac.new(key, content.encode("utf-8"), hashlib.sha256).digest()


def hash_sha256(content: str) -> str:
    return hashlib.sha256(content.encode("utf-8")).hexdigest()


def request(
    method: str,
    date: datetime.datetime,
    query: typing.Mapping[str, str],
    header: typing.Mapping[str, str],
    ak: str,
    sk: str,
    token: typing.Optional[str],
    action: str,
    body: typing.Optional[str],
    region: typing.Optional[str] = None,
    version: typing.Optional[str] = None,
) -> typing.Any:
    action_config = ACTION_CONFIG_MAP.get(
        action, {"service": DEFAULT_SERVICE, "version": DEFAULT_VERSION}
    )
    content_type = action_config.get("content_type") or CONTENT_TYPE
    if method == "POST":
        content_type = "application/json"

    request_body = body or ""
    credential = {
        "access_key_id": ak,
        "secret_access_key": sk,
        "service": action_config["service"],
        "region": region or DEFAULT_REGION,
    }
    if token:
        credential["session_token"] = token

    request_param = {
        "body": request_body,
        "host": HOST,
        "path": "/",
        "method": method,
        "content_type": content_type,
        "date": date,
        "query": {"Action": action, "Version": version or action_config["version"], **query},
    }

    x_date = request_param["date"].strftime("%Y%m%dT%H%M%SZ")
    short_x_date = x_date[:8]
    x_content_sha256 = hash_sha256(request_body)
    signed_headers_str = "content-type;host;x-content-sha256;x-date"

    canonical_request_str = "\n".join(
        [
            request_param["method"].upper(),
            request_param["path"],
            norm_query(request_param["query"]),
            f"content-type:{request_param['content_type']}",
            f"host:{request_param['host']}",
            f"x-content-sha256:{x_content_sha256}",
            f"x-date:{x_date}",
            "",
            signed_headers_str,
            x_content_sha256,
        ]
    )
    hashed_canonical_request = hash_sha256(canonical_request_str)
    credential_scope = "/".join(
        [short_x_date, credential["region"], credential["service"], "request"]
    )
    string_to_sign = "\n".join(
        ["HMAC-SHA256", x_date, credential_scope, hashed_canonical_request]
    )
    k_date = hmac_sha256(credential["secret_access_key"].encode("utf-8"), short_x_date)
    k_region = hmac_sha256(k_date, credential["region"])
    k_service = hmac_sha256(k_region, credential["service"])
    k_signing = hmac_sha256(k_service, "request")
    signature = hmac_sha256(k_signing, string_to_sign).hex()

    sign_result = {
        "Host": request_param["host"],
        "X-Content-Sha256": x_content_sha256,
        "X-Date": x_date,
        "Content-Type": request_param["content_type"],
        "Authorization": (
            "HMAC-SHA256 "
            f"Credential={credential['access_key_id']}/{credential_scope}, "
            f"SignedHeaders={signed_headers_str}, Signature={signature}"
        ),
    }

    final_header = {**header, **sign_result}
    if token:
        final_header["X-Security-Token"] = token

    response = httpx.request(
        method=request_param["method"],
        url=f"https://{request_param['host']}{request_param['path']}",
        headers=final_header,
        params=request_param["query"],
        content=request_body or None,
        timeout=30.0,
    )
    response.raise_for_status()
    return response.json()
