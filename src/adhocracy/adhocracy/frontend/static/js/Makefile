# requirement:
# npm install -g typescript
# more info on tsc at http://www.typescriptlang.org/

compile:
	tsc --module amd --sourcemap --out Adhocracy.js Adhocracy.ts

compile-tests:
	tsc --module amd --sourcemap --out Test/Main.js Test/AdHoc.ts

clean:
	find . -name '*~' -exec rm {} \;
	find . -name '*.js' -exec rm {} \;
	find . -name '*.js.map' -exec rm {} \;
