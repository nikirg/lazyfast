import os, re, base64, hashlib, hmac
from typing import Callable
from urllib.parse import urlencode

import pkg_resources


def url_join(*args, query_params: dict | None = None) -> str:
    parts = []

    for arg in args:
        if arg is not None:
            parts.extend(arg.split("/"))

    parts = [part for part in parts if part]
    start_slash = "/" if args[0] and args[0].startswith("/") else ""
    end_slash = "/" if args[-1] and args[-1].endswith("/") else ""
    url = start_slash + "/".join(parts) + end_slash

    if query_params:
        url = f"{url}?{urlencode(query_params)}"

    return url


def generate_csrf_token() -> str:
    secret_key = base64.urlsafe_b64encode(os.urandom(32)).decode("utf-8")
    token = hmac.new(secret_key.encode(), os.urandom(32), hashlib.sha256).hexdigest()
    return token


def extract_pattern(input_string: str, pattern: str) -> str | None:
    escaped_pattern = (
        re.escape(pattern)
        .replace(r"\{", "{")
        .replace(r"\}", "}")
        .replace(r"{survey_id}", "([^/]+)")
    )
    match = re.match(f"^{escaped_pattern}", input_string)
    if match:
        return match.group(0)
    return None


def get_function_id(func: Callable) -> str:
    unique_string = f"{func.__name__}.{func.__module__}"
    return hashlib.md5(unique_string.encode()).hexdigest()


# def check_version():
#     package_name = "lazyfast"
#     current_version = pkg_resources.get_distribution(package_name).version

#     def print_message_in_box(message: str):
#         lines = message.split("\n")
#         max_length = max(len(line) for line in lines)
#         border = "+" + "-" * (max_length + 2) + "+"

#         print(border)
#         for line in lines:
#             print(f"| {line.ljust(max_length)} |")
#         print(border)

#     url = f"https://pypi.org/pypi/{package_name}/json"
#     try:
#         with urllib.request.urlopen(url) as response:
#             data = response.read()
#             pypi_data = json.loads(data.decode("utf-8"))
#             latest_version = pypi_data["info"]["version"]

#             if current_version != latest_version:
#                 message = (
#                     f"A new version of {package_name} is available: {latest_version}\n"
#                     f"Your current version: {current_version}"
#                 )
#             else:
#                 message = (
#                     f"You have the latest version of {package_name}: {current_version}"
#                 )

#             print_message_in_box(message)
#     except urllib.error.URLError:
#         print_message_in_box("Failed to fetch the latest version from PyPI")


# check_version()
