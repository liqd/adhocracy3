TSC=tsc
# (for more info on tsc, see http://www.typescriptlang.org/)
FIX_TSC_ERROR_FORMAT=perl -ne 'chomp; if (/^(\S+)\((\d+),(\d+)\):(.*)/) { print "$$1:$$2:$$3:\n$$4\n\n"; } else { print "$$_\n"; }'
# (this line makes tsc output work for IDEs that expect gcc error message syntax.)
FIX_TSLINT_ERROR_FORMAT=perl -ne 'chomp; if (/^(\S+)\[(\d+),\s*(\d+)\]:(.*)/) { print "$$1:$$2:$$3:$$4\n"; } else { print "$$_\n"; }'
# (same for tslint)

# make things

compile:
	$(TSC) --module amd --sourcemap --out Adhocracy.js Adhocracy.ts 2>&1 | $(FIX_TSC_ERROR_FORMAT)

AdhocracySpec.ts: .dummy
	./AdhocracySpec.sh > AdhocracySpec.ts

compile_tests_browser: AdhocracySpec.ts
	$(TSC) --module amd --sourcemap Adhocracy*.ts 2>&1 | $(FIX_TSC_ERROR_FORMAT)

test_no_blanket: .dummy
	cat ../test.html | perl -pe 's/(data-cover-flags=".*)(")$$/$$1 engineOnly$$2/' > ../test-no-blanket.html

compile_tests_node: AdhocracySpec.ts
	$(TSC) --module commonjs Adhocracy*.ts 2>&1 | $(FIX_TSC_ERROR_FORMAT)

description:
	$(TSC) -d --module amd --sourcemap --out Adhocracy.js Adhocracy.ts


# run tests

test: tslint compile_tests_node test_node

tslint:
	../../../../../../bin/tslint_check_adhocracy | $(FIX_TSLINT_ERROR_FORMAT)

tslint_fast:
	@echo "\n\n"
	@echo "tslint starts node repeatedly for each file.  there is a pull request that"
	@echo "accepts multiple -f arguments, which reduces the run time from 11.6s to <4s."
	@echo "until the pull request has been accepted and released, this rule is"
	@echo "experimental.  if in doubt, use tslint instead."
	@echo "More info / updates: https://github.com/palantir/tslint/pull/176."
	@echo "\n\n"
	tslint -c ../../../../../../etc/tslint.json \
		-f ./Adhocracy/Resources.ts \
		-f ./Adhocracy/Util.ts \
		-f ./Adhocracy/Pages/DocumentWorkbench.ts \
		-f ./Adhocracy/Widgets.ts \
		-f ./Adhocracy/WidgetsSpec.ts \
		-f ./Adhocracy/Css.ts \
		-f ./Adhocracy/Types.ts \
		-f ./Adhocracy/Services/Http.ts \
		-f ./Adhocracy/Services/WS.ts \
		-f ./Adhocracy/Services/Done.ts \
		-f ./Adhocracy/Services/Config.ts \
		-f ./Adhocracy/Services/User.ts \
		-f ./Adhocracy/UtilSpec.ts \
		-f ./AdhocracySpec.ts \
		-f ./Adhocracy.ts

test_node:
	../../../../../../bin/jasmine-node .
	@echo "NOTE: leaving commonjs modules in place."
	@echo "      'make compile_tests_browser' if you need to run js code in browser again!"


# cleanup, word count, aux

clean:
	find . -name '*~' -exec rm {} \;
	find . -name '*.js' -exec rm {} \;
	find . -name '*.js.map' -exec rm {} \;
	find . -name '[^_]*.d.ts' -exec rm {} \;

wc:
	git ls-files | grep \\.ts$ | wc
	git ls-files | grep \\.ts$ | xargs wc

.dummy:
