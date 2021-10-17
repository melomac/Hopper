#!/usr/bin/python3

import json
import subprocess
import tempfile
from pathlib import Path


# ---------------------------------------------------------------------------
# Configuration

DEFAULT_CONFIG = {
    'editor': 'Sublime Text',
    'editors': {
        'BBEdit': ['/usr/local/bin/bbedit'],
        'MacVim': ['/Applications/MacVim.app/Contents/MacOS/Vim', '-g'],
        'SubEthaEdit': ['/usr/local/bin/see'],
        'Sublime Text': ['/usr/local/bin/subl'],
        'TextMate': ['/usr/local/bin/mate'],
        'Visual Studio Code': ['/usr/local/bin/code']
    }
}


def get_config_path():
    script = Path(__file__)
    filename = script.stem + '.json'
    filepath = script.parent.joinpath(filename)
    return filepath


def read_config():
    config_path = get_config_path()
    if not config_path.is_file():
        save_config(DEFAULT_CONFIG)
    return json.loads(config_path.read_text())


def save_config(data):
    config_path = get_config_path()
    _ = config_path.write_text(json.dumps(data, indent=2))


def get_editor_command():
    try:
        config = read_config()
    except:
        config = DEFAULT_CONFIG
    editor = config['editor']
    command = config['editors'][editor]
    return command


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

    command = get_editor_command()  # ['/usr/local/bin/subl']
    with tempfile.NamedTemporaryFile('w', suffix='.m') as temp:
        temp.write(text)
        temp.flush()
        command.append(temp.name)
        _ = subprocess.call(command)


# ---------------------------------------------------------------------------

if __name__ == '__main__':
    main()
