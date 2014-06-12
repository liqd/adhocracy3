# requirement:
# npm install -g typescript
# more info on tsc at http://www.typescriptlang.org/
TSC=tsc
FIX_TSC_ERROR_FORMAT=perl -ne 'chomp; if (/^(\S+)\((\d+),(\d+)\):(.*)/) { print "$$1:$$2:$$3:\n$$4\n\n"; } else { print "$$_\n"; }'

compile:
	$(TSC) --module amd --sourcemap --out Adhocracy.js Adhocracy.ts 2>&1 | $(FIX_TSC_ERROR_FORMAT)

description:
	$(TSC) -d --module amd --sourcemap --out Adhocracy.js Adhocracy.ts

clean:
	find . -name '*~' -exec rm {} \;
	find . -name '*.js' -exec rm {} \;
	find . -name '*.js.map' -exec rm {} \;
	find . -name '[^_]*.d.ts' -exec rm {} \;

wc:
	find . -name '*.ts' | xargs wc
