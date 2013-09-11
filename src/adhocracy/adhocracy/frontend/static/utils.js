
// global object to store our functionality
ad = {}

function endsWith(str, suffix) {
    return str.indexOf(suffix, str.length - suffix.length) !== -1;
};

function toForms(obj) {
    var result = [];
    for (i in obj.data) {
        result.push(toForm(obj.data[i]));
    };
    return {
        iface: "formlist",
        elements: result
    };
};

// Converts an obviel model to an obviel form.
function toForm(data) {
    subwidgets = [];
    for (i in data) {
        subwidgets.push(toWidget(i, data[i]));
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
        data: data,
    };
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
                title: key,
                validate: {
                    required: true,
                },
            };
        case "object":
            return {
                ifaces: ["textlineField"],
                name: key,
                title: key,
                validate: {
                    required: true,
                },
            };
        default:
            throw ("NYI " + model + " : " + typeof(model));
    };
};
