var root_url = "/adhocracy";

var showjs = function(json) {
    return JSON.stringify(json, null, 2)
};

var dummyHandler = function(name) {
    return function(jqxhr, textstatus, errorthrown) {
        console.log(name + ": [" + showjs(jqxhr) + "][" + textstatus + "][" + errorthrown + "]")
    }
};



// ***
if (false) {
    console.log("OPTIONS");
    $.ajax(root_url, {
        type: "OPTIONS",
        success: dummyHandler("1/success"),
        error:   dummyHandler("1/error")
    });
}

// ***
if (false) {
    console.log("POST");
    var propcontainer = {
      'content_type': 'adhocracy.interfaces.IProposalContainer',
      'data': { 'adhocracy.interfaces.IName': { 'name': 'no_more_mosquitos2' } }
    };
    $.ajax(root_url, {
        type: "POST",
        dataType: "json",
        contentType: "application/json",
        data: showjs(propcontainer),
        success: dummyHandler("2/success"),
	error:   dummyHandler("2/error")
      });
}

// ***
if (true) {
    console.log("GET");
    $.ajax(root_url + "/no_more_mosquitos2/_versions", {
        type: "GET",
        dataType: "json",
        contentType: "application/json",
        success: dummyHandler("3/success"),
	error:   dummyHandler("3/error")
    }).done(function(x) {
        console.log("PUT");

        var pred = x.children[0];
        var name = pred.name;

        pred.workflow_state = '1';

        $.ajax(root_url + "/no_more_mosquitos2/_versions/" + name, {
            type: "PUT",
            dataType: "json",
            contentType: "application/json",
            data: showjs(pred),
            success: dummyHandler("4/success"),
            error:   dummyHandler("4/error")
        });
    });
}
