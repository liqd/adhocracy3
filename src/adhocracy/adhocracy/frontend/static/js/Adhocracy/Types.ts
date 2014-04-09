export interface Content<Data> {
    content_type: string;
    path?: string;
    first_version_path?: string;
    data: Data;
    reference_colour?: string;
}

export interface Reference {
    content_type: string;
    path: string;
}

export function addParagraph(proposalVersion: MeineHeine, paragraphPath: string) {
    return proposalVersion.data["adhocracy.sheets.document.IDocument"].elements.push(paragraphPath);
};


export interface HasIDocumentSheet {
    "adhocracy.sheets.document.IDocument": IDocumentSheet;
}

export interface IDocumentSheet {
    title: string;
    description: string;
    elements: string[];
}

export interface MeineHeine extends Resource, HasIDocumentSheet {}

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
            elements: elements,
        };
        return this;
    }
    addIDocument(title: string, description: string, elements: string[]) {
        this.data["adhocracy.sheets.document.IDocument"] = {
            title: title,
            description: description,
            elements: elements,
        };
        return this;
    }
    addIVersionable(follows: string[], root_version: string[]) {
        this.data["adhocracy.sheets.versions.IVersionable"] = {
            follows: follows,
            root_version: root_version,
        };
        return this;
    }
    addIName(name: string) {
        this.data["adhocracy.sheets.name.IName"] = {
            name: name,
        };
        return this;
    }
    addIParagraph(content: string) {
        this.data["adhocracy.sheets.document.IParagraph"] = {
            content: content,
        };
        return this;
    }
}

export class Proposal extends Resource {
    constructor(name?: string) {
        super("adhocracy.resources.proposal.IProposal");
        if (name !== undefined) {
            this.addIName(name);
        }
    }
}

export class Paragraph extends Resource {
    constructor(name?: string) {
        super("adhocracy.resources.paragraph.IParagraph");
        if (name !== undefined) {
            this.addIName(name);
        }
    }
}

export class Section extends Resource {
    constructor(name?: string) {
        super("adhocracy.resources.section.ISection");
        if (name !== undefined) {
            this.addIName(name);
        }
    }
}

export class SectionVersion extends Resource {
    constructor(title: string, elements: string[], follows: string[], root_version: string[]) {
        super("adhocracy.resources.section.ISectionVersion");
        this.addISection(title, elements)
            .addIVersionable(follows, root_version);
    }
}

