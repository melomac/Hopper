#!/usr/bin/python3

import os
import time


# ---------------------------------------------------------------------------

EDITOR_CLI = {
    'BBEdit': '/usr/local/bin/bbedit',
    'MacVim': '/Applications/MacVim.app/Contents/MacOS/Vim -g',
    'SubEthaEdit': '/usr/local/bin/see',
    'Sublime Text': '/usr/local/bin/subl',
    'TextMate': '/usr/local/bin/mate',
    'Visual Studio Code': '/usr/local/bin/code'
}
EDITOR = EDITOR_CLI['Sublime Text']


# ---------------------------------------------------------------------------

def main():
    doc = Document.getCurrentDocument()
    seg = doc.getCurrentSegment()
    adr = doc.getCurrentAddress()
    proc = seg.getProcedureAtAddress(adr)
    if proc is None:
        return

    eip = proc.getEntryPoint()
    name = seg.getNameAtAddress(eip)
    head = proc.signatureString()
    code = proc.decompile()

    dest = f"/tmp/{name}_{time.time()}.m"
    with open(dest, 'w') as fd:
        _ = fd.write("%s {\n%s}" % (head, code))

    os.system(f"{EDITOR} '{dest}'")


# ---------------------------------------------------------------------------

if __name__ == '__main__':
    main()
