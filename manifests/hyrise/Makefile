# Copyright (C) 2023 Gramine contributors
# SPDX-License-Identifier: BSD-3-Clause

ARCH_LIBDIR ?= /lib/$(shell $(CC) -dumpmachine)
LOG_FILE ?= gramine.log

ifeq ($(DEBUG),1)
GRAMINE_LOG_LEVEL = warning
else ifeq ($(DEBUG),2)
GRAMINE_LOG_LEVEL = debug
else ifeq ($(DEBUG),3)
GRAMINE_LOG_LEVEL = trace
else
GRAMINE_LOG_LEVEL = error
endif

.PHONY: all
all: tpchbench.manifest
ifeq ($(SGX),1)
all: tpchbench.manifest.sgx tpchbench.sig
endif

tpchbench.manifest: tpch-bench.manifest.template
	gramine-manifest \
		-Dlog_level=$(GRAMINE_LOG_LEVEL) \
		-Darch_libdir=$(ARCH_LIBDIR) \
		-Doptimize=$(OPTIMIZE) \
		-Dstats=$(STATS) \
		-Dlog_file=$(LOG_FILE) \
		-Dprofile=$(PROFILE) \
		$< $@
	gramine-manifest-check $@

# gramine-sgx-sign generates both a .sig file and a .manifest.sgx file. This is somewhat
# hard to express properly in Make. The simple solution would be to use
# "Rules with Grouped Targets" (`&:`), however make on Ubuntu <= 20.04 doesn't support it.
#
# Simply using a normal rule with "two targets" is equivalent to creating separate rules
# for each of the targets, and when using `make -j`, this might cause two instances
# of gramine-sgx-sign to get launched simultaneously, potentially breaking the build.
#
# As a workaround, we use a dummy intermediate target, and mark both files as depending on it, to
# get the dependency graph we want. We mark this dummy target as .INTERMEDIATE, which means
# that make will consider the source tree up-to-date even if the sgx_sign file doesn't exist,
# as long as the other dependencies check out. This is in contrast to .PHONY, which would
# be rebuilt on every invocation of make.
tpchbench.sig tpchbench.manifest.sgx: sgx_sign
	@:

.INTERMEDIATE: sgx_sign
sgx_sign: tpchbench.manifest
	gramine-sgx-sign \
		--manifest $< \
		--output $<.sgx
	gramine-manifest-check $<.sgx

ifeq ($(SGX),)
GRAMINE = gramine-direct
else
GRAMINE = gramine-sgx
endif

.PHONY: clean
clean:
	$(RM) *.token *.sig *.manifest.sgx *.manifest OUTPUT

.PHONY: distclean
distclean: clean
