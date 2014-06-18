/// <reference path="../../submodules/DefinitelyTyped/requirejs/require.d.ts"/>
/// <reference path="../../submodules/DefinitelyTyped/angularjs/angular.d.ts"/>
/// <reference path="../../submodules/DefinitelyTyped/underscore/underscore.d.ts"/>
/// <reference path="../_all.d.ts"/>

import _ = require("underscore");

import Util = require("./Util");
import Http = require("./Services/Http");


export interface HasIPoolSheet {
    "adhocracy.sheets.pool.IPool": IPoolSheet;
}

export interface HasIDocumentSheet {
    "adhocracy.sheets.document.IDocument": IDocumentSheet;
}

export interface HasISectionSheet {
    "adhocracy.sheets.document.ISection": ISectionSheet;
}

export interface HasIParagraphSheet {
    "adhocracy.sheets.document.IParagraph": IParagraphSheet;
}

export interface HasIVersionsSheet {
    "adhocracy.sheets.versions.IVersions": IVersionsSheet;
}

export interface IPoolSheet {
    elements: string[];
}

export interface IDocumentSheet {
    title: string;
    description: string;
    elements: string[];
}

export interface ISectionSheet {
    title: string;
    elements: string[];
    subsections: string[];
}

export interface IParagraphSheet {
    content: string;
}

export interface IVersionsSheet {
    elements: string[];
}

export interface PartialIProposalVersion extends Resource, HasIDocumentSheet {}

export class Resource {
    contentType : string;
    data : Object;
    constructor(contentType: string) {
        this.contentType = contentType;
        this.data = {};
    }
    addISection(title: string, elements: string[]) {
        this.data["adhocracy.sheets.document.ISection"] = {
            title: title,
            elements: elements
        };
        return this;
    }
    addIDocument(title: string, description: string, elements: string[]) {
        this.data["adhocracy.sheets.document.IDocument"] = {
            title: title,
            description: description,
            elements: elements
        };
        return this;
    }
    addIVersionable(follows: string[], rootVersion: string[]) {
        this.data["adhocracy.sheets.versions.IVersionable"] = {
            follows: follows,
            root_version: rootVersion
        };
        return this;
    }
    addIName(name: string) {
        this.data["adhocracy.sheets.name.IName"] = {
            name: name
        };
        return this;
    }
    addIParagraph(content: string) {
        this.data["adhocracy.sheets.document.IParagraph"] = {
            content: content
        };
        return this;
    }
}

export class Proposal extends Resource {
    constructor(name?: string) {
        super("adhocracy_sample.resources.proposal.IProposal");
        if (name !== undefined) {
            this.addIName(name);
        }
    }
}

export class Paragraph extends Resource {
    constructor(name?: string) {
        super("adhocracy_sample.resources.paragraph.IParagraph");
        if (name !== undefined) {
            this.addIName(name);
        }
    }
}

export class Section extends Resource {
    constructor(name?: string) {
        super("adhocracy_sample.resources.section.ISection");
        if (name !== undefined) {
            this.addIName(name);
        }
    }
}

export class SectionVersion extends Resource {
    constructor(title: string, elements: string[], follows: string[], rootVersion: string[]) {
        super("adhocracy_sample.resources.section.ISectionVersion");
        this.addISection(title, elements)
            .addIVersionable(follows, rootVersion);
    }
}

export var addParagraph = (proposalVersion: PartialIProposalVersion, paragraphPath: string) => {
    "use strict";
    return proposalVersion.data["adhocracy.sheets.document.IDocument"].elements.push(paragraphPath);
};

// FIXME: backend should have LAST
/**
 * takes an array of URL's to resource versions
 */
export var newestVersion = (versions: string[]) : string => {
    "use strict";
    return _.max(versions, (versionPath: string) => parseInt(versionPath.match(/\d*$/)[0], 10)).toString();
};

export var newestVersionInContainer = (container) => {
    "use strict";
    return newestVersion(container.data.data["adhocracy.sheets.versions.IVersions"].elements);
};

export var getNewestVersion = ($http, path: string) : ng.IPromise<any> => {
    "use strict";
    return $http.get(path).then((container) =>
        $http.get(decodeURIComponent(newestVersionInContainer(container)))
    );
};

export var postProposal = (
    $http,
    $q: ng.IQService,
    proposalVersion: PartialIProposalVersion,
    paragraphVersions
) => {
    "use strict";
    var proposalName = proposalVersion.data["adhocracy.sheets.document.IDocument"].title;

    return $http.post("/adhocracy", new Proposal(Util.normalizeName(proposalName))).success((resp) => {
        var proposalPath = decodeURIComponent(resp.data.path);
        var proposalFirstVersionPath = decodeURIComponent(resp.data.first_version_path);

        var sectionPromiseStupid = $http.post(proposalPath, new Section());

        var paragraphPromises = paragraphVersions.map((paragraph) =>
            $http.post(proposalPath, new Paragraph()).success((resp) => {
                var paragraphPath = decodeURIComponent(resp.data.path);
                var paragraphFirstVersionPath = decodeURIComponent(resp.data.first_version_path);

                return $http.post(paragraphPath, paragraph.addIVersionable([paragraphFirstVersionPath], [proposalPath]));
            }).error(Http.logBackendError)
        );

        var sectionVersionPromise = sectionPromiseStupid.success(respSection => {
            return $q.all(paragraphPromises).then((respParagraphs) => {
                var paths = respParagraphs.map((resp) => decodeURIComponent(resp.data.path) );

                var sectionVersion = new SectionVersion(undefined, paths, [], [decodeURIComponent(respSection.data.first_version_path)]);

                return $http.post(decodeURIComponent(respSection.data.path), sectionVersion);
            });
        }).error(Http.logBackendError);

        return $q.all(paragraphPromises).then((respParagraphs) => {
            return sectionVersionPromise.success((respSectionVersion) => {
                addParagraph(proposalVersion, decodeURIComponent(respSectionVersion.data.path));

                proposalVersion.addIVersionable([], [proposalFirstVersionPath]);

                return $http.post(proposalPath, proposalVersion);
            }).error(Http.logBackendError);
        });
    }).error(Http.logBackendError);
};

export var followNewestVersion = ($http, resourceVersion) => {
    "use strict";
    return $http.get(resourceVersion.path).then((newResourceVersion) => {
        resourceVersion["adhocracy.sheets.versions.IVersionable"].follows = [newResourceVersion.data.path];
        return resourceVersion;
    });
};
