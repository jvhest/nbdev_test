# AUTOGENERATED! DO NOT EDIT! File to edit: nbs/00_core.ipynb (unless otherwise specified).

__all__ = ['DEBUG', 'extract_field', 'read_opf_file', 'get_title', 'get_author', 'get_date', 'create_book_title',
           'get_all_epubs', 'generate_epub_name', 'move_epub', 'move_all_epubs']

# Cell
import os
import zipfile
import shutil
from typing import Tuple

DEBUG = False

# Cell
def extract_field(buffer: str, query: str) -> str:
    """
    Buffer is an xml string. Search for :query: in buffer.
    The query should be a part of opening tag starting
    with < like <dc:title.
    If found the containing value of the tag will be returned.
    If not found empty string is returned.
    """
    field_value = ""
    pos = buffer.find(query)
    if pos >= 0:
        in_field = False
        for c in buffer[(pos + 1):]:
            if c == "<":
                break
            if in_field:
                field_value += c
            if c == ">":
                in_field = True
    return field_value

# Cell
def read_opf_file(epub_path: str) -> str:
    """
    Read and return the content of the *.opf file in epub "file-system".
    If no *.opf file in epub return empty string.
    """
    if not os.path.exists(epub_path):
        raise FileNotFoundError

    with zipfile.ZipFile(epub_path) as myzip:
        opf_fname = None
        for fn in myzip.namelist():
            if fn.endswith(".opf"):
                opf_fname = fn
                break

        if not opf_fname:
            print(f"{os.path.split(epub_path)[1]} has no *.opf file")
            return ""

        with myzip.open(opf_fname) as myfile:
            return myfile.read().decode()

# Cell
def get_title(buffer):
    return extract_field(buffer, "<dc:title")

# Cell
def get_author(buffer):
    creator = extract_field(buffer, "<dc:creator")
    if not creator:
        creator = extract_field(buffer, "<creator")
    return creator

# Cell
def get_date(buffer):
    date = extract_field(buffer, "<dc:date")
    if not date:
        date = extract_field(buffer, '<meta property="dcterms:modified"')
    if len(date) > 4:
        return date[:4]

# Cell
def create_book_title(buffer: str) -> str:
    """
    Returns a new name for the epub based on title, author and date.
    If title cannot be found then empty string will be returned
    """
    if DEBUG:
        lines = buffer.split("\r")
        for line in lines:
            print(line.strip())

    title = get_title(buffer)
    author = get_author(buffer)
    date = get_date(buffer)

    new_book_title = ""
    if title:
        new_book_title = (
            title
            + (" - " + author if author else "")
            + ("[" + date + "]" if date else "")
            + ".epub"
        )
        for character in "/":
            new_book_title = new_book_title.replace(character, "*")

    return new_book_title

# Cell
def get_all_epubs(folder: str) -> list[str]:
    """
    returns list with abs. path to all epubs in folder
    """
    epubs = [
        os.path.join(folder, fname)
        for fname in os.listdir(folder)
        if os.path.isfile(os.path.join(folder, fname)) and fname.endswith(".epub")
    ]
    print(f"aantal epubs in {folder} is {len(epubs)}\n")
    return epubs

# Cell
def generate_epub_name(epub_path: str) -> str:
    """
    generate epub name for :epub_path: based on content of .opf file
    """
    try:
        buffer = read_opf_file(epub_path)
    except FileNotFoundError:
        return ""

    if not buffer:
        return ""
    else:
        new_book_title = create_book_title(buffer)
        new_book_title = new_book_title if new_book_title else ""
    return new_book_title

# Cell
def move_epub(epub_path: str, backup_folder: str) -> Tuple[int, str]:
    """
    find new book title for :epub: in :folder: and copy
    the epubs with new book title to :backup_folder:
    """
    folder, epub = os.path.split()

    new_epub_name = generate_epub_name(epub_path)
    if new_epub_name == "":
        print(f"{epub_path} not moved")
        return False

    new_epub_backupname = os.path.join(backup_folder, new_epub_name)

    if not os.path.exists(new_epub_backupname):
        try:
            shutil.copy(epub_path, new_epub_backupname)

        except shutil.SameFileError:
            print(f"{new_epub}")
            print("Source and destination represents the same file.")

        except PermissionError:
            print(f"{new_epub}")
            print("Permission denied.")

        except:
            print(f"{new_epub}")
            print("Error occurred while copying file.")

    else:
        print(f"target exists: {os.path.split(new_epub)[1]}")
        print(f"source -> {os.path.split(epub)[1]}")

    return new_book_title

# Cell
def move_all_epubs(source_folder: str, backup_folder: str):
    """
    create new book title for first :count: epubs in :folder: and copy
    the epubs with new book title to :backup_folder:
    """
    epubs = get_all_epubs(source_folder)

    copied_epubs = {}
    copied = 0
    for epub in epubs:
        status, new_book_title = move_epub(epub, backup_folder)
        copied += status

        if new_book_title in copied_epubs:
            print(f"source -> {copied_epubs[new_book_title]}\n")
        else:
            copied_epubs[new_book_title] = os.path.split(epub)[1]

    print(f"aantal epubs copied to backupfolder: {copied}")