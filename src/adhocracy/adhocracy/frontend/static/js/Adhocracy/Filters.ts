import Types = require("./Types");
import Resources = require("./Resources");

export var filterDocumentTitle = () => {
    return (resource : Types.Content<Resources.HasIDocumentSheet>) : string => {
        return resource.data["adhocracy.sheets.document.IDocument"].title;
    };
};
