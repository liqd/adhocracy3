import DWB = require("./Adhocracy/Pages/DocumentWorkbench");

export var init = (config) : void => {
    "use strict";

    // detect wheter we are running in iframe
    config.embedded = (window !== top);

    DWB.run(config);
};
