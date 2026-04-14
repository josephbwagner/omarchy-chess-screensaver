import argparse
import curses
import signal
import sys

from .animation import run_screensaver


def main():
    parser = argparse.ArgumentParser(
        prog='omarchy-cmd-screensaver',
        description='Chess screensaver for Omarchy — replays elite Grandmaster games.',
    )
    parser.add_argument(
        '--speed', type=float, default=1.0, metavar='SECONDS',
        help='Seconds between moves (default: 1.0; use 0.5 for 2 moves/sec)',
    )
    args = parser.parse_args()

    def _cleanup(sig, frame):
        curses.endwin()
        sys.exit(0)

    signal.signal(signal.SIGINT,  _cleanup)
    signal.signal(signal.SIGTERM, _cleanup)

    try:
        curses.wrapper(lambda stdscr: run_screensaver(stdscr, args.speed))
    except KeyboardInterrupt:
        pass


if __name__ == '__main__':
    main()
