#!/usr/bin/env python3

import os
import tempfile

EDITOR_CLI = {
    'BBEdit': '/usr/local/bin/bbedit',
    'MacVim': '/Applications/MacVim.app/Contents/MacOS/Vim -g',
    'SubEthaEdit': '/usr/local/bin/see',
    'Sublime Text': '/usr/local/bin/subl',
    'TextMate': '/usr/local/bin/mate',
    'Visual Studio Code': '/usr/local/bin/code'
}
EDITOR = EDITOR_CLI['Sublime Text']


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

    with tempfile.NamedTemporaryFile('w', suffix=".m") as temp:
        temp.write("%s {\n%s}\n" % (head, code))
        temp.flush()
        os.system(f"{EDITOR} '{temp.name}'")

if __name__ == '__main__':
    main()
