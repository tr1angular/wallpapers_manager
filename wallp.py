import argparse
from functools import partial
from time import sleep

from watchdog.observers import Observer

from wallpapers_manager import *


def arguments_handler() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser()
    parser.add_argument("-c", "--convert", choices=["png", "jpg", "jpeg"], help="Convert all files to specific format")
    parser.add_argument("-r", "--rename", action="store_true", help="Rename all files in a directory numerically")
    parser.add_argument(
        "-b", "--backup", nargs="?", const="without_arg", metavar="DEST",
        help="Make a ZIP archive with all wallpapers")
    parser.add_argument("-d", "--dispatch", action="store_true", help="Watch directory for changes")
    parser.add_argument("path", help="Path with all wallpapers")
    return parser


def perform_actions(args: argparse.Namespace) -> None:
    """ Renaming, converting or backing up """
    if args.rename:
        rename_wallpapers(args.path)

    if args.convert:
        convert_wallpapers(args.path)

    if args.backup is None:
        ...
    elif args.backup == "without_arg":
        make_backup(args.path)
    else:
        make_backup(args.path, where_to_store=args.backup)


def main() -> None:
    args = arguments_handler().parse_args()

    if args.dispatch:
        observer = Observer()
        observer.schedule(WallpapersHandler(partial(perform_actions, args)), path=args.path, recursive=False)
        observer.start()

        try:
            while True:
                sleep(1)
        except KeyboardInterrupt:
            observer.stop()

        observer.join()
    else:
        perform_actions(args)


if __name__ == "__main__":
    main()
