/// <reference path="../../submodules/DefinitelyTyped/requirejs/require.d.ts"/>
/// <reference path="../../submodules/DefinitelyTyped/angularjs/angular.d.ts"/>
/// <reference path="../../submodules/DefinitelyTyped/underscore/underscore.d.ts"/>
/// <reference path="../_all.d.ts"/>

import _ = require("underscore");

import Util = require("Adhocracy/Util");


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
    content_type : string;
    data : Object;
    constructor(content_type: string) {
        this.content_type = content_type;
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
    addIVersionable(follows: string[], root_version: string[]) {
        this.data["adhocracy.sheets.versions.IVersionable"] = {
            follows: follows,
            root_version: root_version
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
    constructor(title: string, elements: string[], follows: string[], root_version: string[]) {
        super("adhocracy_sample.resources.section.ISectionVersion");
        this.addISection(title, elements)
            .addIVersionable(follows, root_version);
    }
}

export function addParagraph(proposalVersion: PartialIProposalVersion, paragraphPath: string) {
    return proposalVersion.data["adhocracy.sheets.document.IDocument"].elements.push(paragraphPath);
};

// takes an array of URL's to resource versions
// FIXME: backend should have LAST
export function newestVersion(versions: string[]) : string {
    return _.max(versions, (version_path: string) => parseInt(version_path.match(/\d*$/)[0], 10)).toString();
};

export function newestVersionInContainer(container) {
    return newestVersion(container.data.data["adhocracy.sheets.versions.IVersions"].elements);
};

export function getNewestVersion($http, path: string) : ng.IPromise<any> {
    return $http.get(path).then( (container) =>
        $http.get(decodeURIComponent(newestVersionInContainer(container)))
    );
};

export function postProposal($http,
                             $q: ng.IQService,
                             proposalVersion: PartialIProposalVersion,
                             paragraphVersions) {
    var proposalName = proposalVersion.data["adhocracy.sheets.document.IDocument"].title;

    return $http.post("/adhocracy", new Proposal(Util.normalizeName(proposalName))).then( (resp) => {
        var proposalPath = decodeURIComponent(resp.data.path);
        var proposalFirstVersionPath = decodeURIComponent(resp.data.first_version_path);

        var sectionPromiseStupid = $http.post(proposalPath, new Section());

        var paragraphPromises = paragraphVersions.map( (paragraph) =>
            $http.post(proposalPath, new Paragraph()).then( (resp) => {
                var paragraphPath = decodeURIComponent(resp.data.path);
                var paragraphFirstVersionPath = decodeURIComponent(resp.data.first_version_path);

                return $http.post(paragraphPath, paragraph.addIVersionable([paragraphFirstVersionPath], [proposalPath]));
            })
        );

        var sectionVersionPromise = sectionPromiseStupid.then( respSection => {
            return $q.all(paragraphPromises).then( (respParagraphs) => {
                var paths = respParagraphs.map( (resp) => decodeURIComponent(resp.data.path) );

                var sectionVersion = new SectionVersion(undefined, paths, [], [decodeURIComponent(respSection.data.first_version_path)]);

                return $http.post(decodeURIComponent(respSection.data.path), sectionVersion);
            });
        });

        return $q.all(paragraphPromises).then( (respParagraphs) => {
            return sectionVersionPromise.then( (respSectionVersion) => {
                addParagraph(proposalVersion, decodeURIComponent(respSectionVersion.data.path));

                proposalVersion.addIVersionable([], [proposalFirstVersionPath]);

                return $http.post(proposalPath, proposalVersion);
            });
        });
    });
};

export function followNewestVersion($http, resourceVersion) {
    return $http.get(resourceVersion.path).then( (newResourceVersion) => {
        resourceVersion["adhocracy.sheets.versions.IVersionable"].follows = [newResourceVersion.data.path];
        return resourceVersion;
    });
};
