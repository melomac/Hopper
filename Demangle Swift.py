#!/usr/bin/python

import re, subprocess, os
from ctypes import cdll, create_string_buffer, sizeof


# ---------------------------------------------------------------------------

SWIFT_DEMANGLE = "/Applications/Xcode.app/Contents/Developer/Toolchains/XcodeDefault.xctoolchain/usr/bin/swift-demangle"


# ---------------------------------------------------------------------------

def findSwiftDemangle():
	global SWIFT_DEMANGLE
	global swift_demangle_getDemangledName
	
	process = subprocess.Popen( [ "xcrun", "--find", "swift-demangle" ],
								stdout = subprocess.PIPE,
								stderr = subprocess.PIPE)
	
	output, error = process.communicate()
	
	retcode = process.returncode
	if retcode != 0:
		raise Exception(" ".join(cmd), retcode, error.rstrip("\n"))

	SWIFT_DEMANGLE = output.rstrip("\n")

	dylib = os.path.realpath(SWIFT_DEMANGLE + "/../../lib/libswiftDemangle.dylib")
	try:
		swift_demangle_getDemangledName = cdll.LoadLibrary(dylib)["swift_demangle_getDemangledName"]
	except (OSError, AttributeError) as e:
		swift_demangle_getDemangledName = None
		Document.getCurrentDocument().log("swift_demangle_getDemangledName not found in libswiftDemangle.dylib\n" + str(e))


def demangleSwift(name):
	global swift_demangle_getDemangledName
	if (swift_demangle_getDemangledName != None):
		demangled = create_string_buffer(len(name) * 4)
		length = swift_demangle_getDemangledName(name, demangled, sizeof(demangled))
		return demangled.value if length > 0 else name
	else:
		process = subprocess.Popen( [ SWIFT_DEMANGLE ],
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

	rname = re.search(r"_T[\d\w]+", name).group(0)

	output = demangleSwift(rname)

	# fail
	if output in rname:
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

			elif name[0:4] in [ "+[_T", "-[_T" ]:
				demangled = demangleClassName(name)

			elif name[0:4] in [ "objc", "imp_" ] and "__T" in name:
				demangled = demangleIndirect(name)

			else:
				continue

			doc.moveCursorAtAddress(address)

			if name is demangled:
				doc.log("Failed to demangle symbol at address: 0x%08x with name: %s" % (address, name))
				continue

			seg.setNameAtAddress(address, demangled)
			# doc.log("Demangled symbol at address: 0x%08x with name: %s" % (address, demangled))

	doc.moveCursorAtAddress(current)


# ---------------------------------------------------------------------------

if __name__ == "__main__":
	main()

