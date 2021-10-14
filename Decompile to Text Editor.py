#!/usr/bin/python3

import subprocess
import tempfile


# ---------------------------------------------------------------------------

EDITOR_CLI = {
    'BBEdit': ['/usr/local/bin/bbedit'],
    'MacVim': ['/Applications/MacVim.app/Contents/MacOS/Vim', '-g'],
    'SubEthaEdit': ['/usr/local/bin/see'],
    'Sublime Text': ['/usr/local/bin/subl'],
    'TextMate': ['/usr/local/bin/mate'],
    'Visual Studio Code': ['/usr/local/bin/code']
}
EDITOR = EDITOR_CLI['Sublime Text']


# ---------------------------------------------------------------------------

def main():
    doc = Document.getCurrentDocument()
    seg = doc.getCurrentSegment()
    addr = doc.getCurrentAddress()
    proc = seg.getProcedureAtAddress(addr)
    if proc is None:
        return

    sig = proc.signatureString()
    code = proc.decompile()
    text = "%s {\n%s}" % (sig, code)

    with tempfile.NamedTemporaryFile('w', suffix='.m') as temp:
        temp.write(text)
        temp.flush()
        _ = subprocess.call(EDITOR + [temp.name])


# ---------------------------------------------------------------------------

if __name__ == '__main__':
    main()
