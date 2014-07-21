/// <reference path="../../lib/DefinitelyTyped/requirejs/require.d.ts"/>
/// <reference path="../../lib/DefinitelyTyped/angularjs/angular.d.ts"/>
/// <reference path="../../lib/DefinitelyTyped/underscore/underscore.d.ts"/>
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
    /* This data will be sent directly to the server. So we need
     * to ignore some formatting conventions here. */
    /* tslint:disable:variable-name */
    content_type : string;
    data : Object;
    /* tslint:enable:variable-name */

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
    constructor(name: string) {
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

export class Service {
    constructor(public adhHttp : Http.IService<any>, public $q: ng.IQService) {}

    getNewestVersionPath(path: string) : ng.IPromise<any> {
        // FIXME conceptually, there is no single newest version.  Versions have a tree
        // structure and there can be many leafs to that tree.  This is not a technical
        // issue but a concept issue.  For now, we use the first leaf.
        return this.adhHttp.get(path + "/LAST")
            .then((tag) => tag.data["adhocracy.sheets.tags.ITag"].elements[0]);
    }

    postProposal(path: string, name: string, scope: {proposal?: any}) : ng.IPromise<void> {
        return this.adhHttp.postToPool(path, new Proposal(name))
            .then((ret) => { scope.proposal = ret; });
    }

    postSection(path: string, name: string, scope: {section?: any}) : ng.IPromise<void> {
        return this.adhHttp.postToPool(path, new Section(name))
            .then((ret) => { scope.section = ret; });
    }

    postParagraph(path: string, name: string, scope: {paragraphs}) : ng.IPromise<void> {
        return this.adhHttp.postToPool(path, new Paragraph(name))
            .then((ret) => { scope.paragraphs[name] = ret; });
    }

    postParagraphs(path: string, names: string[], scope) : ng.IPromise<void> {
        var _self = this;

        // we need to post the paragraph versions one after another in order to guarantee
        // the right order
        if (names.length > 0) {
            return _self.postParagraph(path, names[0], scope)
                .then(() => _self.postParagraphs(path, names.slice(1), scope));
        } else {
            return Util.mkPromise(_self.$q, undefined);
        }
    }

    postVersion(path: string, data) : ng.IPromise<any> {
        var _self = this;
        return _self.getNewestVersionPath(path)
            .then((versionPath) => _self.adhHttp.postNewVersion(versionPath, data));
    }

    postProposalVersion(proposal, data, sections, scope) : ng.IPromise<void> {
        var _self = this;
        return _self.$q.all(sections.map((section) => _self.getNewestVersionPath(section.path)))
            .then((sectionVersionPaths) => {
                var _data = Util.deepcp(data);
                _data.data["adhocracy.sheets.document.IDocument"].elements = sectionVersionPaths;
                return _self.postVersion(proposal.path, _data);
            });
    }

    postSectionVersion(section, data, paragraphs, scope) : ng.IPromise<void> {
        var _self = this;
        return _self.$q.all(paragraphs.map((paragraph) => _self.getNewestVersionPath(paragraph.path)))
            .then((paragraphVersionPaths) => {
                var _data = Util.deepcp(data);
                _data.data["adhocracy.sheets.document.ISection"].elements = paragraphVersionPaths;
                return _self.postVersion(section.path, _data);
            });
    }

    postParagraphVersion(paragraph, data, scope: {proposal: any}) : ng.IPromise<void> {
        var _self = this;
        return _self.getNewestVersionPath(scope.proposal.path)
            .then((proposalVersionPath) => {
                var _data = Util.deepcp(data);
                _data.root_versions = [proposalVersionPath];
                return _self.postVersion(paragraph.path, _data);
            });
    }

    postParagraphVersions(paragraphs: any[], datas: any[], scope) : ng.IPromise<void> {
        var _self = this;

        // we need to post the paragraph versions one after another in order to guarantee
        // that the final section version contains all new proposal versions
        if (paragraphs.length > 0) {
            return _self.postParagraphVersion(paragraphs[0], datas[0], scope)
                .then(() => _self.postParagraphVersions(paragraphs.slice(1), datas.slice(1), scope));
        } else {
            return Util.mkPromise(_self.$q, undefined);
        }
    }

    public postProposalWithParagraphs(proposalVersion: PartialIProposalVersion, paragraphVersions) {
        var _self = this;

        var sectionVersion = new Resource("adhocracy_sample.resources.section.ISectionVersion");
        sectionVersion.addISection("single section", []);

        var name = proposalVersion.data["adhocracy.sheets.document.IDocument"].title;
        name = Util.normalizeName(name);

        var scope : {proposal?: any; section?: any; paragraphs: {}} = {
            paragraphs: {}
        };

        return _self.postProposal("/adhocracy", name, scope)
            .then(() => _self.postSection(
                scope.proposal.path,
                "section",
                scope
            ))
            .then(() => _self.postParagraphs(
                scope.proposal.path,
                paragraphVersions.map((paragraphVersion, i) => "paragraph" + i),
                scope
            ))
            .then(() => _self.postProposalVersion(
                scope.proposal,
                proposalVersion,
                [scope.section],
                scope
            ))
            .then(() => _self.postSectionVersion(
                scope.section,
                sectionVersion,
                _.values(scope.paragraphs),
                scope
            ))
            .then(() => _self.postParagraphVersions(
                paragraphVersions.map((paragraphVersion, i) => scope.paragraphs["paragraph" + i]),
                paragraphVersions,
                scope
            ))

            // return the latest proposal Version
            .then(() => _self.getNewestVersionPath(scope.proposal.path))
            .then((proposalVersionPath) => _self.adhHttp.get(proposalVersionPath));
    }
};
