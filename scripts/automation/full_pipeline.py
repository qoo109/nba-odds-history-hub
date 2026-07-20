from __future__ import annotations

import argparse
import gzip
import hashlib
import html.parser
import json
import os
import shutil
import subprocess
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

USER_AGENT = "nba-odds-history-hub/automation-v1 (+https://github.com/qoo109/nba-odds-history-hub)"


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


def iso_now() -> str:
    return utc_now().replace(microsecond=0).isoformat().replace("+00:00", "Z")


def safe_stamp() -> str:
    return utc_now().strftime("%Y%m%dT%H%M%SZ")


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def load_json(path: Path, default: Any) -> Any:
    if not path.exists():
        return default
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return default


def env_bool(name: str, default: bool = False) -> bool:
    value = os.getenv(name)
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}


@dataclass
class FetchResult:
    status: str
    url: str
    http_status: int | None
    data: bytes | None
    etag: str | None
    last_modified: str | None
    content_type: str | None
    error: str | None = None


def fetch_url(
    url: str,
    *,
    etag: str | None = None,
    last_modified: str | None = None,
    timeout: int = 45,
    max_bytes: int = 200 * 1024 * 1024,
) -> FetchResult:
    headers = {"User-Agent": USER_AGENT, "Accept": "*/*"}
    if etag:
        headers["If-None-Match"] = etag
    if last_modified:
        headers["If-Modified-Since"] = last_modified
    request = urllib.request.Request(url, headers=headers)
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            status = int(getattr(response, "status", 200))
            content_length = response.headers.get("Content-Length")
            if content_length and int(content_length) > max_bytes:
                return FetchResult(
                    status="too_large",
                    url=url,
                    http_status=status,
                    data=None,
                    etag=response.headers.get("ETag"),
                    last_modified=response.headers.get("Last-Modified"),
                    content_type=response.headers.get("Content-Type"),
                    error=f"Content-Length {content_length} exceeds max_bytes {max_bytes}",
                )
            data = response.read(max_bytes + 1)
            if len(data) > max_bytes:
                return FetchResult(
                    status="too_large",
                    url=url,
                    http_status=status,
                    data=None,
                    etag=response.headers.get("ETag"),
                    last_modified=response.headers.get("Last-Modified"),
                    content_type=response.headers.get("Content-Type"),
                    error=f"Downloaded bytes exceed max_bytes {max_bytes}",
                )
            return FetchResult(
                status="downloaded",
                url=url,
                http_status=status,
                data=data,
                etag=response.headers.get("ETag"),
                last_modified=response.headers.get("Last-Modified"),
                content_type=response.headers.get("Content-Type"),
            )
    except urllib.error.HTTPError as exc:
        if exc.code == 304:
            return FetchResult(
                status="not_modified",
                url=url,
                http_status=304,
                data=None,
                etag=exc.headers.get("ETag"),
                last_modified=exc.headers.get("Last-Modified"),
                content_type=exc.headers.get("Content-Type"),
            )
        return FetchResult(
            status="http_error",
            url=url,
            http_status=exc.code,
            data=None,
            etag=exc.headers.get("ETag"),
            last_modified=exc.headers.get("Last-Modified"),
            content_type=exc.headers.get("Content-Type"),
            error=str(exc),
        )
    except (urllib.error.URLError, TimeoutError, OSError) as exc:
        return FetchResult(
            status="network_error",
            url=url,
            http_status=None,
            data=None,
            etag=None,
            last_modified=None,
            content_type=None,
            error=str(exc),
        )


class LinkCollector(html.parser.HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.links: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag.lower() != "a":
            return
        for key, value in attrs:
            if key.lower() == "href" and value:
                self.links.append(value)


def is_due(source_state: dict[str, Any], min_interval_hours: float) -> bool:
    checked_at = source_state.get("last_checked_at")
    if not checked_at:
        return True
    try:
        previous = datetime.fromisoformat(str(checked_at).replace("Z", "+00:00"))
    except ValueError:
        return True
    return (utc_now() - previous).total_seconds() >= min_interval_hours * 3600


def redact_url(url: str) -> str:
    """Remove credentials, query strings, and fragments before persisting a URL."""
    parsed = urllib.parse.urlsplit(url)
    host = parsed.hostname or ""
    if parsed.port:
        host = f"{host}:{parsed.port}"
    return urllib.parse.urlunsplit((parsed.scheme, host, parsed.path, "", ""))


def normalize_filename(url: str, fallback: str) -> str:
    name = Path(urllib.parse.urlparse(url).path).name
    if not name:
        return fallback
    cleaned = "".join(char if char.isalnum() or char in ".-_" else "_" for char in name)
    return cleaned[:180] or fallback


def run_command(command: list[str], *, cwd: Path | None = None) -> dict[str, Any]:
    started = time.time()
    proc = subprocess.run(command, cwd=cwd, text=True, capture_output=True, check=False)
    return {
        "command": command,
        "returncode": proc.returncode,
        "stdout": proc.stdout[-12000:],
        "stderr": proc.stderr[-12000:],
        "elapsed_seconds": round(time.time() - started, 3),
    }


def archive_file_source(
    source: dict[str, Any],
    state: dict[str, Any],
    archive_root: Path,
) -> dict[str, Any]:
    source_id = source["id"]
    source_state = state.setdefault("sources", {}).setdefault(source_id, {})
    if not is_due(source_state, float(source.get("min_interval_hours", 24))):
        return {"source_id": source_id, "status": "skipped_not_due"}

    result = fetch_url(
        source["url"],
        etag=source_state.get("etag"),
        last_modified=source_state.get("last_modified"),
        max_bytes=int(source.get("max_bytes", 50 * 1024 * 1024)),
    )
    source_state["last_checked_at"] = iso_now()
    source_state["last_http_status"] = result.http_status
    if result.etag:
        source_state["etag"] = result.etag
    if result.last_modified:
        source_state["last_modified"] = result.last_modified

    report: dict[str, Any] = {
        "source_id": source_id,
        "url": source["url"],
        "status": result.status,
        "http_status": result.http_status,
        "error": result.error,
    }
    if result.data is None:
        return report

    digest = sha256_bytes(result.data)
    report["sha256"] = digest
    report["bytes"] = len(result.data)
    if digest == source_state.get("sha256"):
        report["status"] = "skipped_duplicate"
        return report

    filename = normalize_filename(source["url"], f"{source_id}.bin")
    output = archive_root / source_id / safe_stamp() / filename
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_bytes(result.data)
    source_state.update(
        {
            "sha256": digest,
            "last_downloaded_at": iso_now(),
            "last_path": str(output),
            "content_type": result.content_type,
        }
    )
    report["path"] = str(output)
    report["status"] = "downloaded_new_version"
    return report


def archive_html_links_source(
    source: dict[str, Any],
    state: dict[str, Any],
    archive_root: Path,
) -> dict[str, Any]:
    source_id = source["id"]
    source_state = state.setdefault("sources", {}).setdefault(source_id, {})
    if not is_due(source_state, float(source.get("min_interval_hours", 6))):
        return {"source_id": source_id, "status": "skipped_not_due"}

    index = fetch_url(
        source["index_url"],
        etag=source_state.get("index_etag"),
        last_modified=source_state.get("index_last_modified"),
        max_bytes=int(source.get("index_max_bytes", 10 * 1024 * 1024)),
    )
    source_state["last_checked_at"] = iso_now()
    source_state["last_http_status"] = index.http_status
    if index.etag:
        source_state["index_etag"] = index.etag
    if index.last_modified:
        source_state["index_last_modified"] = index.last_modified

    report: dict[str, Any] = {
        "source_id": source_id,
        "index_url": source["index_url"],
        "status": index.status,
        "http_status": index.http_status,
        "downloaded": 0,
        "skipped_duplicate": 0,
        "errors": [],
        "files": [],
    }
    if index.data is None:
        if index.status == "not_modified":
            report["status"] = "skipped_index_not_modified"
        elif index.error:
            report["errors"].append(index.error)
        return report

    parser = LinkCollector()
    parser.feed(index.data.decode("utf-8", errors="replace"))
    suffixes = tuple(str(item).lower() for item in source.get("allowed_suffixes", [".pdf"]))
    links = []
    for href in parser.links:
        absolute = urllib.parse.urljoin(source["index_url"], href)
        if urllib.parse.urlparse(absolute).path.lower().endswith(suffixes):
            links.append(absolute)
    links = sorted(set(links), reverse=True)
    max_links = int(source.get("max_links_per_run", 50))
    known = source_state.setdefault("known_files", {})

    for link in links[:max_links]:
        prior = known.get(link, {})
        item = fetch_url(
            link,
            etag=prior.get("etag"),
            last_modified=prior.get("last_modified"),
            max_bytes=int(source.get("file_max_bytes", 25 * 1024 * 1024)),
        )
        file_report: dict[str, Any] = {
            "url": link,
            "status": item.status,
            "http_status": item.http_status,
            "error": item.error,
        }
        if item.data is None:
            report["files"].append(file_report)
            if item.status not in {"not_modified"} and item.error:
                report["errors"].append(f"{link}: {item.error}")
            continue
        digest = sha256_bytes(item.data)
        file_report["sha256"] = digest
        if digest == prior.get("sha256"):
            file_report["status"] = "skipped_duplicate"
            report["skipped_duplicate"] += 1
            report["files"].append(file_report)
            continue
        filename = normalize_filename(link, f"{digest[:16]}.bin")
        output = archive_root / source_id / safe_stamp() / filename
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_bytes(item.data)
        known[link] = {
            "sha256": digest,
            "etag": item.etag,
            "last_modified": item.last_modified,
            "downloaded_at": iso_now(),
            "path": str(output),
        }
        file_report.update({"status": "downloaded_new_version", "path": str(output)})
        report["downloaded"] += 1
        report["files"].append(file_report)

    source_state["discovered_link_count"] = len(links)
    source_state["last_index_sha256"] = sha256_bytes(index.data)
    report["discovered_link_count"] = len(links)
    report["status"] = "completed"
    return report


def validate_json_payload(path: Path, expected: str) -> None:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if expected == "list" and not isinstance(payload, list):
        raise ValueError(f"{path} must contain a JSON list")
    if expected == "list_or_object" and not isinstance(payload, (list, dict)):
        raise ValueError(f"{path} must contain a JSON list or object")


def run_odds_snapshot(
    state: dict[str, Any],
    runtime_root: Path,
    database_path: Path,
) -> dict[str, Any]:
    matchups_url = os.getenv("ODDS_MATCHUPS_URL", "").strip()
    straight_url = os.getenv("ODDS_STRAIGHT_URL", "").strip()
    if not matchups_url or not straight_url:
        return {
            "status": "skipped_missing_source_urls",
            "required_secrets": ["ODDS_MATCHUPS_URL", "ODDS_STRAIGHT_URL"],
        }

    snapshot_state = state.setdefault("odds_snapshot", {})
    downloads: dict[str, FetchResult] = {}
    for key, url in {"matchups": matchups_url, "straight": straight_url}.items():
        prior = snapshot_state.setdefault(key, {})
        downloads[key] = fetch_url(
            url,
            etag=prior.get("etag"),
            last_modified=prior.get("last_modified"),
            max_bytes=int(os.getenv("ODDS_MAX_BYTES", str(100 * 1024 * 1024))),
        )

    failed = {
        key: {"status": value.status, "http_status": value.http_status, "error": value.error}
        for key, value in downloads.items()
        if value.data is None and value.status != "not_modified"
    }
    if failed:
        return {"status": "download_failed", "failures": failed}

    # A conditional 304 for either half means we cannot safely build a mixed-version package.
    if any(value.status == "not_modified" for value in downloads.values()):
        return {
            "status": "skipped_not_modified",
            "details": {key: value.status for key, value in downloads.items()},
        }

    assert downloads["matchups"].data is not None
    assert downloads["straight"].data is not None
    combined = hashlib.sha256()
    combined.update(downloads["matchups"].data)
    combined.update(b"\0")
    combined.update(downloads["straight"].data)
    package_sha = combined.hexdigest()
    if package_sha == snapshot_state.get("package_sha256"):
        return {"status": "skipped_duplicate", "package_sha256": package_sha}

    observed_at = os.getenv("ODDS_OBSERVED_AT", "").strip() or iso_now()
    package_dir = runtime_root / "incoming" / safe_stamp()
    package_dir.mkdir(parents=True, exist_ok=True)
    matchups_path = package_dir / "matchups.json"
    straight_path = package_dir / "straight.json"
    matchups_path.write_bytes(downloads["matchups"].data)
    straight_path.write_bytes(downloads["straight"].data)
    validate_json_payload(matchups_path, "list_or_object")
    validate_json_payload(straight_path, "list_or_object")

    metadata = {
        "observedAt": observed_at,
        "sourceId": os.getenv("ODDS_SOURCE_ID", "configured_http_source"),
        "bookmakerId": os.getenv("ODDS_BOOKMAKER_ID", "configured_bookmaker"),
        "notes": (
            "Automated owner-configured legal source intake; retrievedAt=" + iso_now()
            + "; matchupsSource=" + redact_url(matchups_url)
            + "; straightSource=" + redact_url(straight_url)
            + "; packageSha256=" + package_sha
        ),
    }
    write_json(package_dir / "metadata.json", metadata)

    intake = run_command(["odds-hub-validate-intake", "--package-dir", str(package_dir)])
    intake_report_path = package_dir / "intake_report.json"
    intake_report = load_json(intake_report_path, {})
    ready = bool(intake_report.get("readyForImport"))
    report: dict[str, Any] = {
        "status": "validation_failed" if not ready else "validated",
        "package_dir": str(package_dir),
        "package_sha256": package_sha,
        "observed_at": observed_at,
        "validator": intake,
        "intake_report": intake_report,
    }
    if not ready:
        return report

    exports_dir = runtime_root / "exports"
    quality_path = runtime_root / "reports" / f"import_quality_{safe_stamp()}.json"
    import_result = run_command(
        [
            "odds-hub-import",
            "--matchups",
            str(matchups_path),
            "--straight",
            str(straight_path),
            "--observed-at",
            observed_at,
            "--database",
            str(database_path),
            "--source",
            os.getenv("ODDS_SOURCE_ID", "configured_http_source"),
            "--source-name",
            os.getenv("ODDS_SOURCE_NAME", "Configured HTTP odds source"),
            "--bookmaker",
            os.getenv("ODDS_BOOKMAKER_ID", "configured_bookmaker"),
            "--bookmaker-name",
            os.getenv("ODDS_BOOKMAKER_NAME", "Configured bookmaker"),
            "--dedupe-mode",
            "changes-only",
            "--export-dir",
            str(exports_dir),
            "--quality-report",
            str(quality_path),
            "--note",
            "Automated owner-configured legal source intake",
        ]
    )
    report["import"] = import_result
    if import_result["returncode"] != 0:
        report["status"] = "import_failed"
        return report

    history_result = run_command(
        [
            "odds-hub-build-history",
            "--database",
            str(database_path),
            "--output-dir",
            str(exports_dir / "history"),
        ]
    )
    report["history"] = history_result
    report["status"] = "imported" if history_result["returncode"] == 0 else "history_build_failed"

    if report["status"] == "imported":
        snapshot_state["package_sha256"] = package_sha
        snapshot_state["last_imported_at"] = iso_now()
        snapshot_state["last_observed_at"] = observed_at
        snapshot_state["last_package_dir"] = str(package_dir)
        for key, result in downloads.items():
            snapshot_state[key].update(
                {
                    "etag": result.etag,
                    "last_modified": result.last_modified,
                    "sha256": sha256_bytes(result.data or b""),
                    "url": redact_url(result.url),
                }
            )
    return report


def create_database_backup(database_path: Path, backup_root: Path) -> dict[str, Any]:
    if not database_path.exists():
        return {"status": "skipped_database_missing", "path": str(database_path)}
    backup_root.mkdir(parents=True, exist_ok=True)
    output = backup_root / f"odds_history_{safe_stamp()}.sqlite.gz"
    with database_path.open("rb") as source, gzip.open(output, "wb", compresslevel=9) as target:
        shutil.copyfileobj(source, target)
    digest = sha256_file(output)
    (output.with_suffix(output.suffix + ".sha256")).write_text(f"{digest}  {output.name}\n", encoding="utf-8")
    return {
        "status": "created",
        "path": str(output),
        "sha256": digest,
        "bytes": output.stat().st_size,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Run legal, deduplicated NBA odds hub automation.")
    parser.add_argument("--config", default="config/automation-sources.json")
    parser.add_argument("--runtime-root", default="runtime")
    parser.add_argument("--database", default="data/databases/odds_history.sqlite")
    args = parser.parse_args()

    runtime_root = Path(args.runtime_root)
    state_path = runtime_root / "state" / "automation_state.json"
    report_path = runtime_root / "reports" / f"automation_report_{safe_stamp()}.json"
    database_path = Path(args.database)
    database_path.parent.mkdir(parents=True, exist_ok=True)
    for directory in [
        runtime_root / "state",
        runtime_root / "reports",
        runtime_root / "source_archive",
        runtime_root / "incoming",
        runtime_root / "exports",
        runtime_root / "backups",
    ]:
        directory.mkdir(parents=True, exist_ok=True)

    config = load_json(Path(args.config), {"sources": [], "manual_only_sources": []})
    state = load_json(state_path, {"schema_version": "automation-state-v1", "sources": {}})
    report: dict[str, Any] = {
        "schema_version": "automation-report-v1",
        "started_at": iso_now(),
        "repository": "qoo109/nba-odds-history-hub",
        "dry_run": env_bool("AUTOMATION_DRY_RUN", False),
        "source_results": [],
        "manual_only_sources": config.get("manual_only_sources", []),
    }

    if report["dry_run"]:
        report["odds_snapshot"] = {"status": "skipped_dry_run"}
    else:
        report["odds_snapshot"] = run_odds_snapshot(state, runtime_root, database_path)

    for source in config.get("sources", []):
        if not source.get("enabled", True):
            report["source_results"].append({"source_id": source.get("id"), "status": "disabled"})
            continue
        if not source.get("automation_allowed", False):
            report["source_results"].append({"source_id": source.get("id"), "status": "manual_only_policy"})
            continue
        kind = source.get("kind")
        try:
            if kind == "file":
                result = archive_file_source(source, state, runtime_root / "source_archive")
            elif kind == "html_links":
                result = archive_html_links_source(source, state, runtime_root / "source_archive")
            else:
                result = {"source_id": source.get("id"), "status": "unsupported_kind", "kind": kind}
        except Exception as exc:  # Keep one source failure from corrupting the full report.
            result = {"source_id": source.get("id"), "status": "exception", "error": repr(exc)}
        report["source_results"].append(result)

    report["database_backup"] = create_database_backup(database_path, runtime_root / "backups")
    state["last_completed_at"] = iso_now()
    write_json(state_path, state)
    report["finished_at"] = iso_now()
    report["summary"] = {
        "downloaded_new_versions": sum(
            1 for item in report["source_results"] if item.get("status") == "downloaded_new_version"
        )
        + sum(int(item.get("downloaded", 0)) for item in report["source_results"]),
        "duplicates_skipped": sum(
            1 for item in report["source_results"] if item.get("status") == "skipped_duplicate"
        )
        + sum(int(item.get("skipped_duplicate", 0)) for item in report["source_results"]),
        "source_failures": sum(
            1
            for item in report["source_results"]
            if item.get("status") in {"http_error", "network_error", "too_large", "exception"}
        ),
        "odds_snapshot_status": report["odds_snapshot"].get("status"),
        "database_backup_status": report["database_backup"].get("status"),
    }
    write_json(report_path, report)
    write_json(runtime_root / "reports" / "latest_automation_report.json", report)
    print(json.dumps(report["summary"], ensure_ascii=False, indent=2))

    fatal_statuses = {"download_failed", "validation_failed", "import_failed", "history_build_failed"}
    return 1 if report["odds_snapshot"].get("status") in fatal_statuses else 0


if __name__ == "__main__":
    raise SystemExit(main())
