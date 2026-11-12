"""Unified command line for collection, indexing and local services."""

from __future__ import annotations

import argparse
import importlib
import sys


COMMANDS = {
    "build-index": "sgt_kb.indexing.build_index",
    "crawl": "sgt_kb.collection.crawl",
    "daily-update": "sgt_kb.collection.daily_update",
    "en-poll": "sgt_kb.collection.en_poll",
    "exa-discover": "sgt_kb.collection.exa_discover",
    "export-pages": "sgt_kb.indexing.export_pages",
    "figure-pipeline": "sgt_kb.collection.figure_pipeline",
    "ingest-url": "sgt_kb.collection.ingest_url",
    "ingestion-queue": "sgt_kb.collection.ingestion_queue",
    "kb-gate": "sgt_kb.indexing.kb_gate",
    "kb-server": "sgt_kb.service.kb_server",
    "oneapi-wechat": "sgt_kb.collection.oneapi_wechat",
    "review-queue": "sgt_kb.collection.review_queue",
    "rss-poll": "sgt_kb.collection.rss_poll",
    "start-workbench": "sgt_kb.service.start_workbench",
    "video-ingest": "sgt_kb.collection.video_ingest",
    "wayback-catchup": "sgt_kb.collection.wayback_catchup",
    "wayback-wechat": "sgt_kb.collection.wayback_wechat",
    "wechat-auth-update": "sgt_kb.collection.wechat_auth_update",
    "wechat-catchup": "sgt_kb.collection.wechat_catchup",
    "wechat-identity": "sgt_kb.collection.wechat_identity",
    "wechat-mp": "sgt_kb.collection.wechat_mp",
    "wechat-webhook": "sgt_kb.collection.wechat_webhook",
    "weread-mp": "sgt_kb.collection.weread_mp",
    "workbench-api": "sgt_kb.service.workbench_api",
}

NO_ARGUMENT_COMMANDS = {
    "daily-update", "en-poll", "wayback-catchup", "wechat-auth-update", "wechat-catchup",
}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="python -m sgt_kb",
        description="SGT KB collection, indexing, static export and local services.",
        epilog="Use COMMAND --help for command options. Optional dependencies load only for the selected command.",
    )
    parser.add_argument("command", nargs="?", choices=sorted(COMMANDS))
    parser.add_argument("arguments", nargs=argparse.REMAINDER, help=argparse.SUPPRESS)
    args = parser.parse_args(argv)
    if args.command is None:
        parser.print_help()
        return 0

    if args.command in NO_ARGUMENT_COMMANDS:
        argparse.ArgumentParser(
            prog=f"{parser.prog} {args.command}",
            description=f"Run {args.command}; this command takes no options.",
        ).parse_args(args.arguments)

    module = importlib.import_module(COMMANDS[args.command])
    previous_argv = sys.argv
    try:
        sys.argv = [f"{parser.prog} {args.command}", *args.arguments]
        result = module.main()
    finally:
        sys.argv = previous_argv
    return result if isinstance(result, int) else 0


if __name__ == "__main__":
    raise SystemExit(main())
