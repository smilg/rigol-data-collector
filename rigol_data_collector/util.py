import re

from pyvisa import ResourceManager
from pyvisa.errors import LibraryError, VisaIOError

def find_visas() -> list[tuple]:
    '''
    Return all VISA addresses (and the backend) which map to a Rigol DS1000Z.

    Returns:
        list[tuple]: A list of VISA addresses and backends mapping to Rigol DS1000Zs.
    '''
    RIGOL_IDN_REGEX = "^RIGOL TECHNOLOGIES,DS1[01][057]4Z(-S)?( Plus)?,.+$"

    visas = []

    for visa_backend in ["@ivi", "@py"]:
        try:
            visa_manager = ResourceManager(visa_backend)
        except LibraryError:
            pass
        except OSError:
            pass

        for visa_name in visa_manager.list_resources():
            try:
                visa_resource = visa_manager.open_resource(visa_name)
                match = re.search(RIGOL_IDN_REGEX, visa_resource.query("*IDN?"))    # type:ignore
                if match:
                    visas.append((visa_name, visa_backend))
            except VisaIOError:
                pass
            finally:
                visa_resource.close()

    return visas

def add_extension_if_needed(path: str, extension: str) -> str:
    '''
    Adds a file extension to a path if the path doesn't already have that
    extension.

    Args:
        path (str): A file path.
        extension (str): A file extension. Must begin with "." (e.g. ".csv", not "csv").

    Returns:
        str: The supplied path with the supplied file extension.
    '''
    if path.endswith(extension):
        return path
    else:
        return path + extension
