"""Entry point: `python -m wealthsignals.cli run` or `... analytics`."""
import argparse
import sys

from . import analytics, config as config_mod, notify, pipeline, state as state_mod


def run_analytics() -> None:
    cfg = config_mod.load_youtube_oauth()
    state = state_mod.load()
    try:
        client = analytics.get_client(
            client_id=cfg.client_id,
            client_secret=cfg.client_secret,
            refresh_token=cfg.refresh_token,
        )
        per_video = analytics.pull_recent_performance(client)
        analytics.update_topic_performance(state, per_video)
        analytics.write_log_entry(per_video, state)
        state_mod.record_run(state, status="success", detail="analytics pass")
    except Exception as e:
        state_mod.record_run(state, status="failure", detail=f"analytics: {e}")
        if state.consecutive_failures >= 3:
            notify.alert(
                topic=cfg.ntfy_topic,
                title="WealthSignals: analytics job failing",
                message=f"Analytics pass has failed {state.consecutive_failures} times in a row: {e}",
            )
        raise
    finally:
        state_mod.save(state)


def main() -> None:
    parser = argparse.ArgumentParser(prog="wealthsignals")
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("run", help="Generate and upload one Short.")
    sub.add_parser("analytics", help="Pull YouTube Analytics and log decisions.")
    args = parser.parse_args()

    if args.command == "run":
        pipeline.run()
    elif args.command == "analytics":
        run_analytics()
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()
