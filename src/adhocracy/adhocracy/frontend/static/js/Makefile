# requirement:
# npm install -g typescript
# more info on tsc at http://www.typescriptlang.org/
TSC=../../../../../../bin/tsc

compile:
	$(TSC) --module amd --sourcemap --out Adhocracy.js Adhocracy.ts

clean:
	find . -name '*~' -exec rm {} \;
	find . -name '*.js' -exec rm {} \;
	find . -name '*.js.map' -exec rm {} \;

wc:
	find . -name '*.ts' | xargs wc
