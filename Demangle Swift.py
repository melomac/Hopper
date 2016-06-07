#!/usr/bin/python

import re, subprocess


# ---------------------------------------------------------------------------

SWIFT_DEMANGLE = "/Applications/Xcode.app/Contents/Developer/Toolchains/XcodeDefault.xctoolchain/usr/bin/swift-demangle"


# ---------------------------------------------------------------------------

def findSwiftDemangle():
	global SWIFT_DEMANGLE
	
	process = subprocess.Popen( [ "xcrun", "--find", "swift-demangle" ],
								stdout = subprocess.PIPE,
								stderr = subprocess.PIPE)
	
	output, error = process.communicate()
	
	retcode = process.returncode
	if retcode != 0:
		raise Exception(" ".join(cmd), retcode, error.rstrip("\n"))

	SWIFT_DEMANGLE = output.rstrip("\n")


def demangleSwift(name):
	process = subprocess.Popen( [ SWIFT_DEMANGLE, "-compact" ],
								stdin  = subprocess.PIPE,
								stdout = subprocess.PIPE,
								stderr = subprocess.PIPE)

	output, error = process.communicate(name)

	retcode = process.returncode
	if retcode != 0:
		raise Exception(" ".join(cmd), retcode, error.rstrip("\n"))

	return output.rstrip("\n")


def demangleClassName(name):
	"""
	demangle: -[_TtC12Micro_Snitch13AppController init]
	            ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
	      to: -[Micro_Snitch.AppController init]
	            ^^^^^^^^^^^^^^^^^^^^^^^^^^
	"""

	rname = re.search(r"[^+-\[][\d\w]+", name).group(0)

	return re.sub(r"([+-\[])[\d\w]+(.*)", r"\1%s\2" % demangleSwift(rname), name)


def demangleIndirect(name):
	"""
	demangle: imp___stubs___TFO21MicroSnitchFoundation9MediaType5VideoFMS0_S0_
	                       ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
	      to: imp___stubs___MicroSnitchFoundation.MediaType.Video (MicroSnitchFoundation.MediaType.Type) -> MicroSnitchFoundation.MediaType
	                        ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
	"""

	rname = re.search(r"__T[\d\w]+", name).group(0)

	output = demangleSwift(rname)

	# fail
	if output in rname:
		doc = Document.getCurrentDocument()
		doc.log("Failed to demangle symbol at address: 0x%016x with name: %s" % (doc.getCurrentAddress(), name))

		return name

	# ivar
	output = re.sub(r"(.*) with unmangled suffix \"(.*)\"", r"\1\2", output)

	return re.sub(r"(.*?__)T[\d\w]+", r"\1" + output, name)


# ---------------------------------------------------------------------------

def main():
	findSwiftDemangle()

	doc = Document.getCurrentDocument()
	current = doc.getCurrentAddress()

	for index in xrange(doc.getSegmentCount()):
		seg = doc.getSegment(index)

		for address in xrange(seg.getStartingAddress(), seg.getStartingAddress() + seg.getLength()):
			name = seg.getNameAtAddress(address)

			if name is None:
				continue

			if name[0:4] in [ "+[_T", "-[_T" ]:
				doc.moveCursorAtAddress(address)
				seg.setNameAtAddress(address, demangleClassName(name))

			if name[0:4] in [ "objc", "imp_" ] and "__T" in name:
				doc.moveCursorAtAddress(address)
				seg.setNameAtAddress(address, demangleIndirect(name))

	doc.moveCursorAtAddress(current)


# ---------------------------------------------------------------------------

if __name__ == "__main__":
	main()

