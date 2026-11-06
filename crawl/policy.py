"""URL safety policies, SSRF defenses, and URL canonicalization."""

import ipaddress
import re
import socket
from typing import Optional, Set
from urllib.parse import parse_qsl, urlencode, urlsplit, urlunsplit

# Query parameters commonly used for tracking that should be stripped
TRACKING_PARAMS: Set[str] = {
    "utm_source",
    "utm_medium",
    "utm_campaign",
    "utm_term",
    "utm_content",
    "fbclid",
    "gclid",
    "gclsrc",
    "dclid",
    "msclkid",
    "ref",
    "source",
    "mc_eid",
    "zanpid",
}

# Explicit cloud metadata addresses to block
METADATA_IPS: Set[str] = {
    "169.254.169.254",  # AWS/GCP/Azure link-local metadata
    "fd00:ec2::254",    # AWS IPv6 metadata
}

DISALLOWED_HOSTS: Set[str] = {
    "localhost",
    "localhost.localdomain",
    "ip6-localhost",
    "ip6-loopback",
}


class URLSecurityError(ValueError):
    """Raised when a URL violates safety or SSRF policies."""
    pass


def canonicalize_url(url: str) -> str:
    """Normalize a URL by lowercasing host, stripping fragments, and removing tracking parameters.

    Args:
        url: Raw web URL.

    Returns:
        Canonical normalized URL string.
    """
    if not url:
        return ""

    try:
        parts = urlsplit(url.strip())
    except Exception as exc:
        raise URLSecurityError(f"Malformed URL: {exc}") from exc

    scheme = parts.scheme.lower()
    netloc = parts.netloc.lower()

    # Normalize default ports
    if scheme == "http" and netloc.endswith(":80"):
        netloc = netloc[:-3]
    elif scheme == "https" and netloc.endswith(":443"):
        netloc = netloc[:-4]

    # Normalize path
    path = parts.path or "/"
    # Collapse multiple consecutive slashes
    path = re.sub(r"/+", "/", path)

    # Filter tracking query parameters and sort remaining
    clean_params = []
    if parts.query:
        for key, val in parse_qsl(parts.query, keep_blank_values=True):
            if key.lower() not in TRACKING_PARAMS:
                clean_params.append((key, val))
    clean_params.sort(key=lambda x: x[0])
    new_query = urlencode(clean_params)

    # Fragments are stripped for canonical web sources
    return urlunsplit((scheme, netloc, path, new_query, ""))


def validate_url_safety(url: str, allow_localhost: bool = False) -> None:
    """Validate that a URL uses safe protocols and does not point to internal/SSRF targets.

    Args:
        url: The candidate URL to inspect.
        allow_localhost: If True, bypasses local IP restrictions (e.g., for local SearXNG).

    Raises:
        URLSecurityError: If URL violates any security constraint.
    """
    if not url or not isinstance(url, str):
        raise URLSecurityError("URL must be a non-empty string.")

    try:
        parts = urlsplit(url.strip())
    except Exception as exc:
        raise URLSecurityError(f"Malformed URL cannot be parsed: {exc}") from exc

    scheme = parts.scheme.lower()
    if scheme not in ("http", "https"):
        raise URLSecurityError(f"Disallowed URL scheme: '{scheme}'. Only http and https are permitted.")

    if not parts.hostname:
        raise URLSecurityError("URL is missing a valid hostname.")

    # Disallow user:password@host credentials
    if parts.username or parts.password:
        raise URLSecurityError("URLs containing user credentials are not permitted.")

    hostname = parts.hostname.lower()

    if not allow_localhost:
        if hostname in DISALLOWED_HOSTS or hostname.endswith(".local") or hostname.endswith(".internal"):
            raise URLSecurityError(f"Disallowed local or internal domain: '{hostname}'")

        # Resolve hostname to IP addresses and check each
        try:
            addr_info = socket.getaddrinfo(hostname, None)
        except socket.gaierror as exc:
            # If resolution fails, allow callers or fetchers to handle network failure,
            # but if it looks like a direct numeric IP address, validate it immediately
            try:
                ip_obj = ipaddress.ip_address(hostname)
                _check_ip_safety(ip_obj)
            except ValueError:
                # Hostname failed DNS; will fail safely during fetch
                return
            return

        for entry in addr_info:
            sockaddr = entry[4]
            ip_str = sockaddr[0]
            try:
                ip_obj = ipaddress.ip_address(ip_str)
                _check_ip_safety(ip_obj)
            except ValueError as exc:
                raise URLSecurityError(f"Invalid IP address format: {ip_str}") from exc


def _check_ip_safety(ip_obj: ipaddress.IPv4Address | ipaddress.IPv6Address) -> None:
    """Check that an IP address is not private, loopback, link-local, multicast, or metadata."""
    ip_str = str(ip_obj)

    if ip_str in METADATA_IPS:
        raise URLSecurityError(f"Blocked request to cloud metadata address: {ip_str}")

    if ip_obj.is_loopback:
        raise URLSecurityError(f"Blocked request to loopback address: {ip_str}")

    if ip_obj.is_private:
        raise URLSecurityError(f"Blocked request to private network address: {ip_str}")

    if ip_obj.is_link_local:
        raise URLSecurityError(f"Blocked request to link-local address: {ip_str}")

    if ip_obj.is_multicast:
        raise URLSecurityError(f"Blocked request to multicast address: {ip_str}")

    if ip_obj.is_reserved:
        raise URLSecurityError(f"Blocked request to reserved address: {ip_str}")


def is_safe_url(url: str, allow_localhost: bool = False) -> bool:
    """Return True if the URL passes all safety checks, False otherwise."""
    try:
        validate_url_safety(url, allow_localhost=allow_localhost)
        return True
    except URLSecurityError:
        return False
