import AdhResourcesBase = require("../../ResourcesBase");

import AdhConfig = require("../Config/Config");
import AdhHttp = require("../Http/Http");
import AdhPreliminaryNames = require("../PreliminaryNames/PreliminaryNames");
import AdhResourceWidgets = require("../ResourceWidgets/ResourceWidgets");

var pkgLocation = "/Mercator";


export interface IMercatorProposalScope extends AdhResourceWidgets.IResourceWidgetScope {
    data : {
        basic : {
            user : {
                name : string;
                lastname : string;
                email : string;
            };
            organisation : {
                name : string;
                email : string;
                address : string;
                postcode : string;
                city : string;
                country : string;
                status : string;
                statustext : string;
                about : string;
                size : string;
                cooperation : boolean;
                cooperationText? : string;
            };
        };
        introduction : {
            title : string;
            teaser : string;
            picture? : any;
        };
        detail : {
            description : string;
            location : string;
            story : string;
        };
        motivation : {
            success : string;
            plan : string;
            relevance : string;
            partners : string;
        };
        finance : {
            budget : number;
            funding : number;
            granted : boolean;
            document? : any;
        };
        extra : {
            mediaFiles? : any[];
            experience? : string;
            hear : {
                colleague : boolean;
                website : boolean;
                newsletter : boolean;
                facebook : boolean;
                other : boolean;
                otherDescription : string;
            }
        };
    };
}


export class MercatorProposal<R extends AdhResourcesBase.Resource> extends AdhResourceWidgets.ResourceWidget<R, IMercatorProposalScope> {
    constructor(
        adhConfig : AdhConfig.Type,
        adhHttp : AdhHttp.Service<any>,
        adhPreliminaryNames : AdhPreliminaryNames,
        $q : ng.IQService
    ) {
        super(adhHttp, adhPreliminaryNames, $q);
        this.templateUrl = adhConfig.pkg_path + pkgLocation + "/MercatorProposalCreate.html";
    }

    public _handleDelete(
        instance : AdhResourceWidgets.IResourceWidgetInstance<R, IMercatorProposalScope>,
        path : string
    ) : ng.IPromise<void> {
        return this.$q.when();
    }

    public _update(instance : AdhResourceWidgets.IResourceWidgetInstance<R, IMercatorProposalScope>, resource : R) : ng.IPromise<void> {
        return this.$q.when();
    }

    public _create(instance : AdhResourceWidgets.IResourceWidgetInstance<R, IMercatorProposalScope>) : ng.IPromise<R[]> {
        console.log(instance.scope.data);
        return this.$q.when([]);
    }

    public _edit(instance : AdhResourceWidgets.IResourceWidgetInstance<R, IMercatorProposalScope>, old : R) : ng.IPromise<R[]> {
        return this.$q.when([]);
    }
}
