import os
import re
import hmac
import json
import base64
import hashlib
from typing import Callable

import configparser
import http.client

from urllib.parse import urlencode


def url_join(
    *args, query_params: dict | None = None, path_params: dict | None = None
) -> str:
    parts = []

    for arg in args:
        if arg is not None:
            parts.extend(arg.split("/"))

    parts = [part for part in parts if part]
    start_slash = "/" if args[0] and args[0].startswith("/") else ""
    end_slash = "/" if args[-1] and args[-1].endswith("/") else ""
    url = start_slash + "/".join(parts) + end_slash

    if path_params:
        url = url.format(**path_params)

    if query_params:
        url = f"{url}?{urlencode(query_params)}"

    return url


def generate_csrf_token() -> str:
    secret_key = base64.urlsafe_b64encode(os.urandom(32)).decode("utf-8")
    token = hmac.new(secret_key.encode(), os.urandom(32), hashlib.sha256).hexdigest()
    return token


def str_hash(string: str) -> str:
    return hashlib.md5(string.encode()).hexdigest()


def extract_pattern(input_string: str, pattern: str, splitter: str) -> str | None:
    string = input_string.split(splitter)[0]

    regex_pattern = re.sub(r"([.^$+?()|\[\]\\])", r"\\\1", pattern)
    regex_pattern = re.sub(r"\{[^}]+\}", r"([^/]+)", regex_pattern)
    regex_pattern = "^" + regex_pattern

    if match := re.match(regex_pattern, string):
        return match.group(0)


def get_function_id(func: Callable) -> str:
    unique_string = f"{func.__name__}.{func.__module__}"
    return hashlib.md5(unique_string.encode()).hexdigest()


def check_library_version():
    def print_in_frame(text: str):
        text_length = len(text)
        border = "+" + "-" * (text_length + 2) + "+"
        print(border)
        print(f"| {text} |")
        print(border)

    config = configparser.ConfigParser()
    config.read("pyproject.toml")

    name = config["tool.poetry"]["name"].strip('"')
    current_version = config["tool.poetry"]["version"].strip('"')

    conn = http.client.HTTPSConnection("pypi.org")
    conn.request("GET", f"/pypi/{name}/json")
    response = conn.getresponse()

    if response.status == 200:
        data = json.loads(response.read())
        pypi_version = data["info"]["version"]

        if pypi_version != current_version:
            print_in_frame(
                f"LazyFast | new version available: ({current_version} -> {pypi_version})."
            )

check_library_version()
