#*******************************************************************************

# CTA - Cherenkov Telescope Array
#
# "@(#) $Id: Makefile,v 1.20 2014/11/06 17:08:51 mdavid Exp $" 
#
# Makefile of ACS component for the Weather Station at MST
#
#
# Flag to switch on debugging information
# ----------------------------
#
DEBUG=on
VERBOSE=on
#
# Error definition files for exceptions
# and completions
# ----------------------------
#
ACSERRDEF =

#
# Java sources
# ----------------------------
#

COMPONENT_HELPERS=on

JARFILES = CTSArrayControlSystemImpl
CTSArrayControlSystemImpl_DIRS   = cta
CTSArrayControlSystemImpl_EXTRAS =

#
# Configuration database schema Files
# ------------------------------------
CDB_SCHEMAS = CTSArrayControlSystem

#
# IDL FILES
#----------------------------
IDL_FILES = CTSArrayControlSystem
USER_IDL = 

#
# jar files to be installed
#----------------------------
INSTALL_FILES = 

#
# list of all possible C-sources (used to create automatic dependencies)
# ------------------------------
MAKE_VERBOSE=1
CSOURCENAMES = \
	$(foreach exe, $(EXECUTABLES) $(EXECUTABLES_L), $($(exe)_OBJECTS)) \
	$(foreach lib, $(LIBRARIES) $(LIBRARIES_L), $($(lib)_OBJECTS))


MAKEDIRTMP := $(shell searchFile include/acsMakefile)
ifneq ($(MAKEDIRTMP),\#error\#)
   MAKEDIR := $(MAKEDIRTMP)/include
   include $(MAKEDIR)/acsMakefile
endif

#
# TARGETS
# -------
all:	do_all
	@echo " . . . 'all' done" 

clean : clean_all 
	$(RM) *~ ../include/*~ ../idl/*~ ../*~ ../../*~ ../doc/html/* core
	$(RM) tmp.txt 
	@echo " . . . clean done"

clean_dist : clean clean_dist_all 
	@echo " . . . clean_dist done"

man   : do_man 
	@echo " . . . man page(s) done"

install : install_all
	@echo " . . . installation done"

#___oOo___
