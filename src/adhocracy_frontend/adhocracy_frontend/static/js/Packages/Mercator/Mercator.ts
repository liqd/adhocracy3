import AdhResourcesBase = require("../../ResourcesBase");

import AdhConfig = require("../Config/Config");
import AdhHttp = require("../Http/Http");
import AdhPreliminaryNames = require("../PreliminaryNames/PreliminaryNames");
import AdhResourceWidgets = require("../ResourceWidgets/ResourceWidgets");

var pkgLocation = "/Mercator";


export interface IMercatorProposalScope extends AdhResourceWidgets.IResourceWidgetScope {}


export class MercatorProposal<R extends AdhResourcesBase.Resource> extends AdhResourceWidgets.ResourceWidget<R, IMercatorProposalScope> {
    constructor(
        adhConfig : AdhConfig.Type,
        adhHttp : AdhHttp.Service<any>,
        adhPreliminaryNames : AdhPreliminaryNames,
        $q : ng.IQService
    ) {
        super(adhHttp, adhPreliminaryNames, $q);
        this.templateUrl = adhConfig.pkg_path + pkgLocation + "/MercatorProposalDetail.html";
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
        return this.$q.when([]);
    }

    public _edit(instance : AdhResourceWidgets.IResourceWidgetInstance<R, IMercatorProposalScope>, old : R) : ng.IPromise<R[]> {
        return this.$q.when([]);
    }
}
