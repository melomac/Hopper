#!/usr/bin/python3

import os
import re
import subprocess
from ctypes import cdll, create_string_buffer, sizeof
from datetime import datetime


# ---------------------------------------------------------------------------

SWIFT_DEMANGLE_CLI = None
SWIFT_DEMANGLE_FUN = None
SWIFT_DEMANGLE_LIB = None
SWIFT_DEMANGLE_SYM = 'swift_demangle_getSimplifiedDemangledName'


# ---------------------------------------------------------------------------

def execute(cmd, data=None):
    process = subprocess.Popen(
        cmd,
        encoding='utf-8',
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    output, error = process.communicate(data)
    retcode = process.returncode
    if retcode != 0:
        raise Exception(' '.join(cmd), data, retcode, error.rstrip('\n'))

    return output.rstrip('\n')


def find_swift_demangle():
    global SWIFT_DEMANGLE_CLI
    global SWIFT_DEMANGLE_LIB

    SWIFT_DEMANGLE_CLI = execute(['xcrun', '--find', 'swift-demangle'])
    SWIFT_DEMANGLE_LIB = os.path.realpath(SWIFT_DEMANGLE_CLI + '/../../lib/libswiftDemangle.dylib')


def load_swift_demangle_lib():
    global SWIFT_DEMANGLE_FUN

    SWIFT_DEMANGLE_FUN = cdll.LoadLibrary(SWIFT_DEMANGLE_LIB)[SWIFT_DEMANGLE_SYM]


def demangle_swift_lib(name, size=512):
    demangled = create_string_buffer(size)
    length = SWIFT_DEMANGLE_FUN(name.encode(), demangled, sizeof(demangled))

    if length > size:
        return demangle_swift_lib(name.encode(), length + 1)

    if length > 0:
        return demangled.value.decode()

    return name


def demangle_swift_cli(name):
    return execute([SWIFT_DEMANGLE_CLI], name)


def demangle_swift(name):
    if SWIFT_DEMANGLE_FUN:
        return demangle_swift_lib(name)

    return demangle_swift_cli(name)


# ---------------------------------------------------------------------------

def main():
    start = datetime.now()
    doc = Document.getCurrentDocument()

    find_swift_demangle()
    try:
        load_swift_demangle_lib()
    except (OSError, AttributeError) as error:
        doc.log(f"Failed to load library with error: {error}")
        doc.log('Falling back to CLI mode.')

    segs = [doc.getSegment(index) for index in range(doc.getSegmentCount())]
    names = sum([seg.getLabelsList() for seg in segs], [])
    regex = re.compile(r'(.*?)(_(?:T|\$S|\$s)[^\s@]+)(.*)')
    prefixes = ['_T', '_$S', '_$s']

    success = 0
    failure = 0
    skipped = 0
    for name in names:
        address = doc.getAddressForName(name)
        if not (address and any([prefix in name for prefix in prefixes])):
            # doc.log(f"Skipped symbol with name: {name}")
            skipped += 1
            continue

        matches = regex.search(name)
        if matches:
            prefix, mangled, suffix = matches.groups()
            demangled = prefix + demangle_swift(mangled) + suffix

        if not matches or demangled is name:
            doc.log(f"Failed to demangle symbol at address: {address:#08x} with name: {name}")
            failure += 1
            continue

        doc.setNameAtAddress(address, demangled)
        # doc.log(f"Demangled symbol at address: {address:#08x} with name: {demangled}")
        success += 1

    doc.log('--------------')
    doc.log('Demangle Swift')
    doc.log('--------------')
    doc.log(f"Success: {success} name(s)")
    doc.log(f"Failure: {failure} name(s)")
    doc.log(f"Skipped: {skipped} name(s)")
    doc.log(f"Elapsed: {datetime.now() - start}")


# ---------------------------------------------------------------------------

if __name__ == '__main__':
    main()
