import os
import sys
from typing import List, Dict
from zipfile import ZipFile

from PIL import Image
from loguru import logger
from natsort import natsorted


EXTENSIONS = ("png", "jpg", "jpeg")

logger.remove()  # prevent duplicate output
logger.add(sys.stdout, colorize=True, format="<green>{message}</green>", level="INFO")
logger.add(sys.stderr, colorize=True, format="<red>{message}</red>", level="ERROR")


def get_list_of_wallpapers(path: str) -> List[str]:
    """ Return a list of images from path with extensions such as png or jpg"""
    wallpapers = []
    try:
        for file in os.listdir(path):
            if os.path.isfile(os.path.join(path, file)) and file.endswith(EXTENSIONS):
                wallpapers.append(file)
    except FileNotFoundError:
        logger.error(f"Provided path {path} doesn't exists")
    except NotADirectoryError:
        logger.error(f"Provided path {path} isn't a directory")
    except PermissionError:
        logger.error(f"Don't have a permission for working with {path}")
    except (OSError, Exception) as exc:
        logger.error(f"{exc}")

    return wallpapers


def get_new_wallpapers_names(wallpapers: List[str]) -> Dict[str, str]:
    """ Define a new names for wallpapers """
    sorted_wallpapers = natsorted(wallpapers)
    rename_actions = {}

    for must_be, wallpaper in enumerate(sorted_wallpapers, 1):
        name = os.path.splitext(wallpaper)[0]
        try:
            if int(name) != must_be:
                rename_actions[wallpaper] = str(must_be) + os.path.splitext(wallpaper)[1]
        except ValueError:
            rename_actions[wallpaper] = str(must_be) + os.path.splitext(wallpaper)[1]
        finally:
            must_be += 1

    return rename_actions


def rename_wallpapers(path: str) -> None:
    """ Renames images in a directory numerically """
    wallpapers = get_list_of_wallpapers(path)
    wallpapers_to_rename = get_new_wallpapers_names(wallpapers)

    for old_name, new_name in wallpapers_to_rename.items():
        try:
            os.rename(os.path.join(path, old_name), os.path.join(path, new_name))
            logger.info(f"[*] Rename {old_name} to {new_name}")
        except (PermissionError, FileNotFoundError, IsADirectoryError) as exc:
            logger.error(f"Can't rename {old_name} to {new_name} because of {exc}")
        except (OSError, Exception) as exc:
            logger.error(f"Something went wrong {exc}")


def convert_wallpapers(path: str, to: str = "png") -> None:
    """ Convert all wallpapers in a directory to one type """
    wallpapers = get_list_of_wallpapers(path)
    wallpapers_to_convert = [x for x in wallpapers if not x.endswith(to) and os.path.isfile(os.path.join(path, x))]

    for wallpaper in wallpapers_to_convert:
        try:
            wallpaper_full_path = os.path.join(path, wallpaper)
            w = Image.open(wallpaper_full_path)
            w.save(os.path.join(path, os.path.splitext(wallpaper)[0] + "." + to))
            os.remove(wallpaper_full_path)

            logger.info(f"Converted {wallpaper} to {to}")
        except (OSError, Exception) as exc:
            logger.error(f"Can't convert {wallpaper} to {to}")
            logger.error(exc)


def make_backup(path: str, where_to_store: str = "") -> None:
    """ Create a zip archive with all wallpapers in it. """
    wallpapers = get_list_of_wallpapers(path)

    if where_to_store:
        archive_name = os.path.join(where_to_store, os.path.basename(path) + ".zip")
    else:
        archive_name = os.path.join(os.path.dirname(path), os.path.basename(path) + ".zip")

    with ZipFile(archive_name, "w") as archive:
        for wallpaper in wallpapers:
            archive.write(os.path.join(path, wallpaper), wallpaper)

        logger.info(f"Archive was successfully created at {archive_name}")
