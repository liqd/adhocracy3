TSC=tsc
# (for more info on tsc, see http://www.typescriptlang.org/)
FIX_TSC_ERROR_FORMAT=perl -ne 'chomp; if (/^(\S+)\((\d+),(\d+)\):(.*)/) { print "$$1:$$2:$$3:\n$$4\n\n"; } else { print "$$_\n"; }'
# (this line makes tsc output work for IDEs that expect gcc error message syntax.)

compile:
	$(TSC) --module amd --sourcemap --out Adhocracy.js Adhocracy.ts 2>&1 | $(FIX_TSC_ERROR_FORMAT)

AdhocracySpec.ts: .dummy
	./AdhocracySpec.sh > AdhocracySpec.ts

compile_tests_browser: AdhocracySpec.ts
	$(TSC) --module amd --sourcemap AdhocracySpec.ts 2>&1 | $(FIX_TSC_ERROR_FORMAT)

test_no_blanket: .dummy
	cat ../test.html | perl -pe 's/(data-cover-flags=".*)(")$$/$$1 engineOnly$$2/' > ../test-no-blanket.html

compile_tests_node: AdhocracySpec.ts
	$(TSC) --module commonjs AdhocracySpec.ts 2>&1 | $(FIX_TSC_ERROR_FORMAT)

description:
	$(TSC) -d --module amd --sourcemap --out Adhocracy.js Adhocracy.ts

clean:
	find . -name '*~' -exec rm {} \;
	find . -name '*.js' -exec rm {} \;
	find . -name '*.js.map' -exec rm {} \;
	find . -name '[^_]*.d.ts' -exec rm {} \;

wc:
	find . -name '*.ts' | xargs wc

.dummy:
