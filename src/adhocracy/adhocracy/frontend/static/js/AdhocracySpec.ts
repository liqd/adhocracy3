import UtilSpec = require("./Adhocracy/UtilSpec");
import WidgetsSpec = require("./Adhocracy/WidgetsSpec");
import ServicesWSSpec = require("./Adhocracy/Services/WSSpec");

/**
 * This module includes all frontend unit tests.
 * It can be used both in browser (compile with amd module system) and
 * with jasmine-node (compile with commonjs module system).
 */

UtilSpec.register();
WidgetsSpec.register();
ServicesWSSpec.register();
