"""Functions related to io"""

from contextlib import contextmanager
import shutil
import tempfile


@contextmanager
def get_tempdir():
    """Returns a temporary directory that is cleaned up after usage

    Returns:
        str
    """
    temp_dir = tempfile.mkdtemp()
    try:
        yield temp_dir
    finally:
        shutil.rmtree(temp_dir)
