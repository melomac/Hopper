# Hopper scripts

[Hopper Disassembler](http://hopperapp.com/) Python v3 scripts for macOS.

To install, copy or symlink the scripts to `~/Library/Application Support/Hopper/Scripts`.
If Hopper is already running, you'll have to run the `Reload Script Folder Content` command from the `Scripts` menu.

## [Decompile to Editor](Decompile%20to%20Editor.py)

Open current procedure in configured code editor for you to enjoy syntax coloring, highlighting, find keyboard shortcuts, _etc._.
Default editor is [Sublime Text](https://www.sublimetext.com/).

### Requirements

Any supported editor: Sublime Text, [Visual Studio Code](https://code.visualstudio.com/), [TextMate](https://macromates.com/), [BBEdit](http://www.barebones.com/products/bbedit/), [SubEthaEdit](https://www.codingmonkeys.de/subethaedit/), _etc._.

### How to

On first launch, the script creates a JSON configuration file at: `~/Library/Application Support/Hopper/Scripts/Decompile to Editor.json`

Here you have the JSON configuration default contents:

```json
{
  "editor": "Sublime Text",
  "editors": {
    "BBEdit": [
      "/usr/local/bin/bbedit"
    ],
    "MacVim": [
      "/Applications/MacVim.app/Contents/MacOS/Vim",
      "-g"
    ],
    "SubEthaEdit": [
      "/usr/local/bin/see"
    ],
    "Sublime Text": [
      "/usr/local/bin/subl"
    ],
    "TextMate": [
      "/usr/local/bin/mate"
    ],
    "Visual Studio Code": [
      "/usr/local/bin/code"
    ]
  }
}
```

Set the `editor` value to your favorite editor.
Add `editors` commands to support even more editors.
The temporary filepath is the last command parameter.

## [Demangle Swift](Demangle%20Swift.py)

Demangle all labels with [Swift](https://swift.org/) [mangled](https://mikeash.com/pyblog/friday-qa-2014-08-15-swift-name-mangling.html) names.

Attempt to load `libswiftDemangle.dylib` or run `swift-demangle` command-line interface on library load error.

### Requirements

[Xcode](https://developer.apple.com/xcode/) or [Command Line Tools](https://developer.apple.com/downloads/).
