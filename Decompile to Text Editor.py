#!/usr/bin/python

import os, time


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

	dest = "/tmp/{name}_{time}.m".format(name = name, time = time.time())

	f = file(dest, "w")
	f.write("%s {\n%s}" % (head, code))
	f.close()

	# os.system("/usr/local/bin/bbedit '%s'" % dest)
	# os.system("/usr/local/bin/mate '%s'" % dest)
	# os.system("/usr/local/bin/see '%s'" % dest)
	# os.system("/Applications/MacVim.app/Contents/MacOS/Vim -g '%s'" % dest)
	# os.system("open -n -b 'com.microsoft.VSCode' --args '%s'" % dest)
	os.system("/usr/local/bin/subl '%s'" % dest)


# ---------------------------------------------------------------------------

if __name__ == "__main__":
	main()

