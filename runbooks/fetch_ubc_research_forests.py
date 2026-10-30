#!/usr/bin/env python3
"""Download the UBC Research Forests OneDrive dropbox into the private store.

The shared folder requires a Microsoft Graph access token.  Set
``MS_GRAPH_TOKEN`` (delegated ``Files.Read.All``) or pass ``--token``.  The
script resolves the sharing URL, walks the folder tree, and writes files under
the DataLad submodule's ``raw/`` directory.

Usage::

    MS_GRAPH_TOKEN=... python runbooks/fetch_ubc_research_forests.py \
      --share-url 'https://ubcca-my.sharepoint.com/:f:/r/personal/...' \
      --out-dir external/ubc-research-forests-data/raw

The share URL must be readable by the token.  Anonymous links work without a
token only when the folder is shared with "Anyone with the link"; the current
UBC tenant link is restricted and returns 403.
"""

from __future__ import annotations

import argparse
import base64
import json
import os
import urllib.request
from pathlib import Path

GRAPH = "https://graph.microsoft.com/v1.0"


def _share_id(url: str) -> str:
    """Encode a sharing URL as a Graph share ID."""
    encoded = base64.urlsafe_b64encode(url.encode()).decode().rstrip("=")
    return f"u!{encoded}"


def _get(url: str, token: str | None) -> dict:
    """GET a Graph resource."""
    request = urllib.request.Request(url)
    if token:
        request.add_header("Authorization", f"Bearer {token}")
    with urllib.request.urlopen(request, timeout=60) as response:
        return json.load(response)


def _download(url: str, destination: Path) -> None:
    """Download one driveItem content URL."""
    destination.parent.mkdir(parents=True, exist_ok=True)
    with urllib.request.urlopen(url, timeout=120) as response:
        destination.write_bytes(response.read())
    print(f"downloaded {destination} ({destination.stat().st_size} bytes)")


def _walk(item: dict, destination: Path, token: str | None) -> None:
    """Recursively download a driveItem."""
    name = item.get("name", "unnamed")
    if "folder" in item:
        folder = destination / name
        folder.mkdir(parents=True, exist_ok=True)
        # Use the item's own children endpoint; the share root is handled by
        # the caller.
        children = _get(
            f"{GRAPH}/drives/{item['parentReference']['driveId']}/items/{item['id']}/children",
            token,
        )
        for child in children.get("value", []):
            _walk(child, folder, token)
        while "@odata.nextLink" in children:
            children = _get(children["@odata.nextLink"], token)
            for child in children.get("value", []):
                _walk(child, folder, token)
        return
    download_url = item.get("@microsoft.graph.downloadUrl")
    if download_url:
        _download(download_url, destination / name)


def main() -> None:
    """Resolve the share and download all files."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--share-url", required=True)
    parser.add_argument("--out-dir", type=Path, required=True)
    parser.add_argument("--token", default=os.environ.get("MS_GRAPH_TOKEN"))
    args = parser.parse_args()
    if not args.token:
        raise SystemExit(
            "MS_GRAPH_TOKEN is not set. Provide a delegated Files.Read.All token "
            "or re-share the folder as Anyone with the link and use a public "
            "download URL."
        )
    share = _share_id(args.share_url)
    root = _get(f"{GRAPH}/shares/{share}/driveItem", args.token)
    root["_share_id"] = share
    args.out_dir.mkdir(parents=True, exist_ok=True)
    children = _get(f"{GRAPH}/shares/{share}/driveItem/children", args.token)
    for child in children.get("value", []):
        _walk(child, args.out_dir, args.token)
    while "@odata.nextLink" in children:
        children = _get(children["@odata.nextLink"], args.token)
        for child in children.get("value", []):
            _walk(child, args.out_dir, args.token)
    print(f"done: {args.out_dir}")


if __name__ == "__main__":
    main()
