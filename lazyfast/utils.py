import os, re, base64, hashlib, hmac
from urllib.parse import urlencode


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
    escaped_pattern = re.escape(pattern).replace(r"\{", "{").replace(r"\}", "}")
    match = re.match(f"^{escaped_pattern}", input_string)
    if match:
        return match.group(0)
