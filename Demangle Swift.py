#!/usr/bin/python

import os, re, subprocess
from ctypes import cdll, create_string_buffer, sizeof
from datetime import datetime


# ---------------------------------------------------------------------------

SWIFT_DEMANGLE_CLI = None
SWIFT_DEMANGLE_FUN = None
SWIFT_DEMANGLE_LIB = None
SWIFT_DEMANGLE_SYM = "swift_demangle_getDemangledName"


# ---------------------------------------------------------------------------

def execute(cmd, data=None):
	process = subprocess.Popen(cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
	output, error = process.communicate(data)
	retcode = process.returncode

	if retcode != 0:
		raise Exception(" ".join(cmd), data, retcode, error.rstrip("\n"))

	return output.rstrip("\n")


def findSwiftDemangle():
	global SWIFT_DEMANGLE_CLI
	global SWIFT_DEMANGLE_LIB

	SWIFT_DEMANGLE_CLI = execute([ "xcrun", "--find", "swift-demangle" ])
	SWIFT_DEMANGLE_LIB = os.path.realpath(SWIFT_DEMANGLE_CLI + "/../../lib/libswiftDemangle.dylib")


def loadSwiftDemangleLib():
	global SWIFT_DEMANGLE_FUN

	SWIFT_DEMANGLE_FUN = cdll.LoadLibrary(SWIFT_DEMANGLE_LIB)[SWIFT_DEMANGLE_SYM]


def demangleSwiftLib(name, size=512):
	demangled = create_string_buffer(size)

	length = SWIFT_DEMANGLE_FUN(name, demangled, sizeof(demangled))

	if length > size:
		return demangleSwiftLib(name, length + 1)

	if length > 0:
		return demangled.value

	return name


def demangleSwiftCLI(name):
	return execute([ SWIFT_DEMANGLE_CLI ], name)


def demangleSwift(name):
	if SWIFT_DEMANGLE_FUN:
		return demangleSwiftLib(name)

	return demangleSwiftCLI(name)


def demangleLabel(name):
	rname = re.search(r"(.*?)(_T[\d\w]+)(.*)", name).group(2)

	output = demangleSwift(rname)

	# fail
	if output in rname:
		return name

	# ivar
	output = re.sub(r"(.*) with unmangled suffix \"(.*)\"", r"\1\2", output)

	return re.sub(r"(.*?)(_T[\d\w]+)(.*)", r"\1%s\3" % demangleSwift(output), name)


# ---------------------------------------------------------------------------

def main():
	start = datetime.now()

	findSwiftDemangle()
	try:
		loadSwiftDemangleLib()
	except (OSError, AttributeError) as e:
		doc.log("Failed to load library with error: %s" % str(e))
		doc.log("Falling back to CLI mode.")

	doc = Document.getCurrentDocument()

	names = []
	for index in xrange(doc.getSegmentCount()):
		seg = doc.getSegment(index)
		names += seg.getLabelsList()

	success = 0
	failure = 0
	skipped = 0
	for name in names:
		if "_T" in name[0:4] or "__T" in name:
			demangled = demangleLabel(name)
		else:
			skipped += 1
			# doc.log("Skipped symbol with name: %s" % name)
			continue

		address = doc.getAddressForName(name)
		# doc.moveCursorAtAddress(address)

		if demangled is name:
			failure += 1
			doc.log("Failed to demangle symbol at address: 0x%08x with name: %s" % (address, name))
			continue

		success += 1
		doc.setNameAtAddress(address, demangled)
		# doc.log("Demangled symbol at address: 0x%08x with name: %s" % (address, demangled))

	doc.log("--------------")
	doc.log("Demangle Swift")
	doc.log("--------------")
	doc.log("Success: %d name(s)" % success)
	doc.log("Failure: %d name(s)" % failure)
	doc.log("Skipped: %d name(s)" % skipped)
	doc.log("Elapsed: %s" % str(datetime.now() - start))


# ---------------------------------------------------------------------------

if __name__ == "__main__":
	main()

