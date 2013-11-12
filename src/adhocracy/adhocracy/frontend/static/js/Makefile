# requirement:
# npm install -g typescript
# more info on tsc at http://www.typescriptlang.org/
TSC=../../../../../../bin/tsc

compile: compile-lib compile-tests

compile-lib:
	$(TSC) --module amd --sourcemap --out Adhocracy.js Adhocracy.ts

compile-tests:
	$(TSC) --module amd --sourcemap --out Test/Main.js Test/Main.ts

clean:
	find . -name '*~' -exec rm {} \;
	find . -name '*.js' -exec rm {} \;
	find . -name '*.js.map' -exec rm {} \;

wc:
	find . -name '*.ts' | xargs wc
