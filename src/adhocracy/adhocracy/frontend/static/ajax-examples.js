    var dummyHandler = function(name) {
      return function(jqxhr, textstatus, errorthrown) {
          console.log(name + ": [" + JSON.stringify(jqxhr, null, 2) + "][" + textstatus + "][" + errorthrown + "]")
      }
    };


    // ***
    console.log("OPTIONS");
    $.ajax("/adhocracy", {
        type: "OPTIONS",
        success: dummyHandler("1/success"),
	error:   dummyHandler("1/error")
      });


    // ***
/*
    console.log("POST");
    var propcontainer = {
      'content_type': 'adhocracy.interfaces.IProposalContainer',
      'data': { 'adhocracy.interfaces.IName': { 'name': 'kommunismus_sofort' } }
    };
    $.ajax("/adhocracy", {
        type: "POST",
        data: propcontainer,
        dataType: "json",
        success: dummyHandler("2/success"),
	error:   dummyHandler("2/error")
      });
*/


    // var prop = { description: "d", title: "t" };



