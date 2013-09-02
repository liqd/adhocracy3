
function endsWith(str, suffix) {
    return str.indexOf(suffix, str.length - suffix.length) !== -1;
}

// Converts an obviel model to an obviel form.
function toForm(obj) {
    subwidgets = [];
    main_data = obj[obj.main_interface];
    for (i in main_data) {
	if (i !== 'iface') {
            subwidgets.push(toWidget(i, main_data[i]));
	}
    };
    form = {
        ifaces: ["viewform"],
        form: {
            widgets: subwidgets,
            controls: [
                {
                    label: "Save",
                    action: "test-action",  // conjecture: server should deliver edited object after persisting it.
                },
            ],
        },
        data: main_data,
    };
    // console.log(obj);
    console.log(form);
    return form;
};

// Converts a model to an obviel widget.
function toWidget(key, model) {
    switch(typeof(model)) {
        case "string":
            return {
                ifaces: ["textlineField"],
                name: key,
                title: "Text",
                validate: {
                    required: true,
                },
            };
        default:
            throw ("NYI " + model + " : " + typeof(model));
    };
};
