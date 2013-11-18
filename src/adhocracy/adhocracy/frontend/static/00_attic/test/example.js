
console.log("jscheck examples");

// testing this function
function le(a, b) {
    return a <= b;
}

JSC.clear();

//for (i = 0; i < 100; i++) {
//    console.log(JSC.any()());
//}

JSC.test(
    "Less than",
    function (verdict, a, b) {
        return verdict(le(a, b));
    },
    [
        JSC.integer(10),
        JSC.integer(20)
    ],
    function (a, b) {
        if (a < b) {
            return 'lt';
        } else if (a === b) {
            return 'eq';
        } else {
            return 'gt';
        }
    }
);

console.log("hum...  something should have happened by now.  giving up.");
