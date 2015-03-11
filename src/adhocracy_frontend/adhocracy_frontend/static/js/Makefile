SHELL=/bin/bash --login
MAKE_ROOT=$(realpath $(dir $(lastword $(MAKEFILE_LIST))))
A3_ROOT=$(shell cat ${MAKE_ROOT}/../../../../../source_env | grep A3_ROOT | egrep -o '[^=]+$$')
LD_LIBRARY_PATH=$(shell cat ${MAKE_ROOT}/../../../../../source_env | grep LD_LIBRARY_PATH | egrep -o '[^=]+$$')
TSC=$(A3_ROOT)/bin/tsc
TSLINT=$(A3_ROOT)/bin/tslint
NODE=$(A3_ROOT)/bin/node
# (for more info on tsc, see http://www.typescriptlang.org/)
FIX_TSC_ERROR_FORMAT=perl -ne 'chomp; if (/^(\S+)\((\d+),(\d+)\):(.*)/) { print "$$1:$$2:$$3:\n$$4\n\n"; } else { print "$$_\n"; }'
# (this line makes tsc output work for IDEs that expect gcc error message syntax.)
FIX_TSLINT_ERROR_FORMAT=perl -ne 'chomp; if (/^(\S+)\[(\d+),\s*(\d+)\]:(.*)/) { print "$$1:$$2:$$3:$$4\n"; } else { print "$$_\n"; }'
# (same for tslint)

# make things

compile: compile_tests_browser

AdhocracySpec.ts: .phony
	./AdhocracySpec.sh > AdhocracySpec.ts

AdhocracyIg.ts: .phony
	./AdhocracyIg.sh > AdhocracyIg.ts

compile_tests_browser: AdhocracySpec.ts AdhocracyIg.ts
	$(TSC) --module amd --sourcemap Adhocracy*.ts 2>&1 | $(FIX_TSC_ERROR_FORMAT)

test-no-blanket: .phony
	cat ../test.html | perl -pe 's/(data-cover-flags=".*)(")$$/$$1 engineOnly$$2/' > ../test-no-blanket.html

compile_tests_node: AdhocracySpec.ts
	$(TSC) --module commonjs Adhocracy*.ts 2>&1 | $(FIX_TSC_ERROR_FORMAT)

description:
	$(TSC) -d --module amd --sourcemap --out Adhocracy.js Adhocracy.ts


# run tests

warn_orphan_js:
	@for i in `find . -name '*.js'`; do \
	    if [ ! -e `echo $$i | sed s/.js$$/.ts/` ]; then \
		echo -ne "\n\nWARNING: orphan js file $$i.  you might want to make clean.\n\n"; \
	    fi; \
	done

test: warn_orphan_js tslint compile_tests_node test_node

tslint:
	$(A3_ROOT)/bin/tslint_check_adhocracy | $(FIX_TSLINT_ERROR_FORMAT)

test_node:
	../../../../../bin/jasmine-node .
	@echo "NOTE: leaving commonjs modules in place."
	@echo "      'make compile_tests_browser' if you need to run js code in browser again!"

test_py:
	../../../../../bin/py.test ../../tests/unit


# cleanup, word count, aux

clean:
	rm -rf Resources_/
	find . -name '*~' -exec rm {} \;
	find . -name '*.js' -exec rm {} \;
	find . -name '*.js.map' -exec rm {} \;
	find . -name '[^_]*.d.ts' -exec rm {} \;

wc:
	git ls-files | grep \\.ts$$ | wc
	git ls-files | grep \\.ts$$ | xargs wc

tags: .phony
	@echo
	@echo "for emacs tag files, include '-e' in CTAGS in your shell env."
	@echo "(note that ctags 5.9 seems to have a bug that keeps it from"
	@echo "reading either of ~/.[ce]tags if called as 'ctags -e'!  not"
	@echo "sure whether this has been reported yet.  use --verbose=1 if"
	@echo "you want to investigate.)"
	@echo
	find . -name '*.ts' | xargs ctags \
		--langdef=typescript \
		--langmap=typescript:.ts \
		--regex-typescript='/^[ \t]*(export)?[ \t]*class[ \t]+([a-zA-Z0-9_]+)/\2/c,classes/' \
		--regex-typescript='/^[ \t]*(export)?[ \t]*module[ \t]+([a-zA-Z0-9_]+)/\2/n,modules/' \
		--regex-typescript='/^[ \t]*(export)?[ \t]*function[ \t]+([a-zA-Z0-9_]+)/\2/f,functions/' \
		--regex-typescript='/^[ \t]*export[ \t]+var[ \t]+([a-zA-Z0-9_]+)/\1/v,variables/' \
		--regex-typescript='/^[ \t]*var[ \t]+([a-zA-Z0-9_]+)[ \t]*=[ \t]*function[ \t]*\(\)/\1/v,varlambdas/' \
		--regex-typescript='/^[ \t]*(export)?[ \t]*(public|private)[ \t]+([a-zA-Z0-9_]+)/\3/m,members/' \
		--regex-typescript='/^[ \t]*(export)?[ \t]*interface[ \t]+([a-zA-Z0-9_]+)/\2/i,interfaces/' \
		--regex-typescript='/^[ \t]*(export)?[ \t]*enum[ \t]+([a-zA-Z0-9_]+)/\2/e,enums/' \
	        --language-force=typescript

.phony:


mkResources: .phony
	git ls-files --other Resources_ | xargs rm -f
	$(TSC) --module commonjs --sourcemap mkResources.ts 2>&1 | $(FIX_TSC_ERROR_FORMAT)
#	$(TSLINT) -c ../../../../../etc/tslint.json -f mkResources.ts 2>&1 | $(FIX_TSLINT_ERROR_FORMAT)
	$(NODE) mkResources.js


testMkResources: .phony
	$(TSC) --module commonjs --sourcemap mkResources/Util.ts 2>&1 | $(FIX_TSC_ERROR_FORMAT)
	cd mkResources && ../$(NODE) Util.js
