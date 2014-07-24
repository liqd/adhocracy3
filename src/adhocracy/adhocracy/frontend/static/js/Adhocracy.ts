import DWB = require("./DocumentWorkbench");

export var init = (config) : void => {
    "use strict";

    // detect wheter we are running in iframe
    config.embedded = (window !== top);
    if (config.embedded) {
        window.document.body.className += " is-embedded";
    }

    DWB.run(config);
};
