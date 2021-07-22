
Python scripts for [Hopper Disassembler](http://hopperapp.com/) on OS X.

To install, copy the script to `~/Library/Application Support/Hopper/Scripts`. You may need to run the `Reload Script Folder Contents` command located in the `Scripts` menu.


### [Decompile to Text Editor](Decompile%20to%20Text%20Editor.py)

Open current procedure in your favorite text editor, so you can enjoy syntax coloring, registers selection, find next, find previous, find all and replace, _etc._. It's awesome with [Sublime Text](https://www.sublimetext.com/).


#### Requirements

A text editor: [BBEdit](http://www.barebones.com/products/bbedit/) "It doesn't suck.", [TextMate](https://macromates.com/), [SubEthaEdit](https://www.codingmonkeys.de/subethaedit/), [Sublime Text](https://www.sublimetext.com/), _etc._.


#### How to

Uncomment your text editor command line:

```python
# os.system("/usr/local/bin/bbedit '%s'" % dest)
# os.system("/usr/local/bin/mate '%s'" % dest)
# os.system("/usr/local/bin/see '%s'" % dest)
os.system("/usr/local/bin/subl '%s'" % dest)
```

And comment other text editors. Feel free to try with other text editors.



### [Demangle Swift](Demangle%20Swift.py)

Demangle all labels with [Swift](https://swift.org/) [mangled](https://mikeash.com/pyblog/friday-qa-2014-08-15-swift-name-mangling.html) names.

Use `libswiftDemangle.dylib` or fallback to `swift-demangle` on library load error.


#### Requirements

[Xcode](https://developer.apple.com/xcode/) or [Command Line Tools](https://developer.apple.com/downloads/).

