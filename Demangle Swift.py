#!/usr/bin/python

import re, subprocess
from ctypes import cdll, create_string_buffer, sizeof
from datetime import datetime


# ---------------------------------------------------------------------------

SWIFT_DEMANGLE_CLI = "/Applications/Xcode.app/Contents/Developer/Toolchains/XcodeDefault.xctoolchain/usr/bin/swift-demangle"

SWIFT_DEMANGLE_FUN = None
SWIFT_DEMANGLE_LIB = "/Applications/Xcode.app/Contents/Developer/Toolchains/XcodeDefault.xctoolchain/usr/lib/libswiftDemangle.dylib"
SWIFT_DEMANGLE_SYM = "swift_demangle_getDemangledName"


# ---------------------------------------------------------------------------

def findSwiftDemangleCLI():
	global SWIFT_DEMANGLE_CLI

	process = subprocess.Popen( [ "xcrun", "--find", "swift-demangle" ],
								stdout = subprocess.PIPE,
								stderr = subprocess.PIPE)

	output, error = process.communicate()
	retcode = process.returncode

	if retcode != 0:
		raise Exception(" ".join(cmd), retcode, error.rstrip("\n"))

	SWIFT_DEMANGLE_CLI = output.rstrip("\n")


def findSwiftDemangleLib():
	global SWIFT_DEMANGLE_LIB

	process = subprocess.Popen( [ "xcode-select", "--print-path" ],
								stdout = subprocess.PIPE,
								stderr = subprocess.PIPE)

	output, error = process.communicate()
	retcode = process.returncode

	if retcode != 0:
		raise Exception(" ".join(cmd), retcode, error.rstrip("\n"))

	SWIFT_DEMANGLE_LIB = output.rstrip("\n") + "/Toolchains/XcodeDefault.xctoolchain/usr/lib/libswiftDemangle.dylib"


def loadSwiftDemangleLib():
	global SWIFT_DEMANGLE_FUN

	SWIFT_DEMANGLE_FUN = cdll.LoadLibrary(SWIFT_DEMANGLE_LIB)[SWIFT_DEMANGLE_SYM]


def demangleSwiftLib(name):
	demangled = create_string_buffer(len(name) * 4)

	length = SWIFT_DEMANGLE_FUN(name, demangled, sizeof(demangled))

	if length > 0:
		return demangled.value

	return name


def demangleSwiftCLI(name):
	process = subprocess.Popen( [ SWIFT_DEMANGLE_CLI ],
								stdin  = subprocess.PIPE,
								stdout = subprocess.PIPE,
								stderr = subprocess.PIPE)

	output, error = process.communicate(name)

	retcode = process.returncode
	if retcode != 0:
		raise Exception(" ".join(cmd), retcode, error.rstrip("\n"))

	return output.rstrip("\n")


def demangleSwift(name):
	if SWIFT_DEMANGLE_FUN:
		return demangleSwiftLib(name)

	return demangleSwiftCLI(name)


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
	      to: imp___stubs__MicroSnitchFoundation.MediaType.Video (MicroSnitchFoundation.MediaType.Type) -> MicroSnitchFoundation.MediaType
	                       ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
	"""

	rname = re.search(r"_T[\d\w]+", name).group(0)

	output = demangleSwift(rname)

	# fail
	if output in rname:
		return name

	# ivar
	output = re.sub(r"(.*) with unmangled suffix \"(.*)\"", r"\1\2", output)

	return re.sub(r"(.*?_)_T[\d\w]+", r"\1" + output, name)


# ---------------------------------------------------------------------------

def main():
	start = datetime.now()
	names = []

	doc = Document.getCurrentDocument()

	for index in xrange(doc.getSegmentCount()):
		seg = doc.getSegment(index)
		names += seg.getLabelsList()

	findSwiftDemangleCLI()
	findSwiftDemangleLib()

	try:
		loadSwiftDemangleLib()
	except (OSError, AttributeError) as e:
		doc.log("Failed to load library with error: %s" % str(e))
		doc.log("Falling back to CLI mode.")

	success = 0
	failure = 0
	skipped = 0

	for name in names:
		if name[0:4] in [ "+[_T", "-[_T" ]:
			demangled = demangleClassName(name)

		elif name[0:4] in [ "objc", "imp_" ] and "__T" in name:
			demangled = demangleIndirect(name)

		else:
			skipped += 1
			continue

		address = doc.getAddressForName(name)

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

