import re
import sys

from pyvisa import ResourceManager
from pyvisa.errors import LibraryError, VisaIOError

def is_valid_folder_name(name: str):
    # Define a regular expression pattern to match forbidden characters
    ILLEGAL_NTFS_CHARS = r'[<>:/\\|?*\"]|[\0-\31]'
    # Define a list of forbidden names
    FORBIDDEN_NAMES = ['CON', 'PRN', 'AUX', 'NUL',
                       'COM1', 'COM2', 'COM3', 'COM4', 'COM5',
                       'COM6', 'COM7', 'COM8', 'COM9',
                       'LPT1', 'LPT2', 'LPT3', 'LPT4', 'LPT5',
                       'LPT6', 'LPT7', 'LPT8', 'LPT9']
    # Check for forbidden characters
    match = re.search(ILLEGAL_NTFS_CHARS, name)
    if match:
        raise ValueError(
            f"Invalid character '{match[0]}' for filename {name}")
    # Check for forbidden names
    platform = sys.platform
    if platform.startswith('cygwin') or platform.startswith('win32'):
        if name.upper() in FORBIDDEN_NAMES:
            raise ValueError(f"{name} is a reserved folder name in Windows")
        # Check for empty name (disallowed in Windows)
        if name.strip() == "":
            raise ValueError("Empty file name not allowed in Windows")
    # Check for names starting or ending with dot or space
    match = re.match(r'^[. ]|.*[. ]$', name)
    if match:
        raise ValueError(
            f"Invalid start or end character ('{match[0]}')"
            f" in folder name {name}"
        )    
        
def find_visas():
    # Return all VISA addresses (and the backend) which map to a Rigol DS1000Z.
    RIGOL_IDN_REGEX = "^RIGOL TECHNOLOGIES,DS1[01][057]4Z(-S)?( Plus)?,.+$"

    visas = []

    for visa_backend in ["@ivi", "@py"]:
        try:
            visa_manager = ResourceManager(visa_backend)
        except LibraryError:
            pass

        for visa_name in visa_manager.list_resources():
            try:
                visa_resource = visa_manager.open_resource(visa_name)
                match = re.search(RIGOL_IDN_REGEX, visa_resource.query("*IDN?"))
                if match:
                    visas.append((visa_name, visa_backend))
            except VisaIOError:
                pass
            finally:
                visa_resource.close()

    return visas