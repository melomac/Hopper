# Hopper scripts

[Hopper Disassembler](http://hopperapp.com/) Python v3 scripts for macOS.

To install, copy or symlink the scripts to `~/Library/Application Support/Hopper/Scripts`.
You may need to run the `Reload Script Folder Content` command located in the `Scripts` menu.

## [Decompile to Text Editor](Decompile%20to%20Text%20Editor.py)

Open current procedure in configured text editor for you to enjoy syntax coloring, highlighting, find keyboard shortcuts, _etc._.
Default text editor is [Sublime Text](https://www.sublimetext.com/).

### Requirements

A text editor: Sublime Text, [Visual Studio Code](https://code.visualstudio.com/), [TextMate](https://macromates.com/), [BBEdit](http://www.barebones.com/products/bbedit/), [SubEthaEdit](https://www.codingmonkeys.de/subethaedit/), _etc._.

### How to

Set the `EDITOR` variable to your favorite editor command.
A dictionary of base commands is provided.

## [Demangle Swift](Demangle%20Swift.py)

Demangle all labels with [Swift](https://swift.org/) [mangled](https://mikeash.com/pyblog/friday-qa-2014-08-15-swift-name-mangling.html) names.

Attempt to load `libswiftDemangle.dylib` or run `swift-demangle` command-line interface on library load error.

### Requirements

[Xcode](https://developer.apple.com/xcode/) or [Command Line Tools](https://developer.apple.com/downloads/).
