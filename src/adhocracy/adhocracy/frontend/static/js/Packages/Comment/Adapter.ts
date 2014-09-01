import _ = require("lodash");

import AdhResource = require("../../Resources");
import ResourcesBase = require("../../ResourcesBase");
import RICommentVersion = require("../../Resources_/adhocracy_sample/resources/comment/ICommentVersion");
import RIComment = require("../../Resources_/adhocracy_sample/resources/comment/IComment");
import SIVersionable = require("../../Resources_/adhocracy/sheets/versions/IVersionable");
import SICommentable = require("../../Resources_/adhocracy_sample/sheets/comment/ICommentable");
import SIComment = require("../../Resources_/adhocracy_sample/sheets/comment/IComment");

import AdhListing = require("../Listing/Listing");
import Util = require("../Util/Util");

import AdhComment = require("./Comment");


export class ListingCommentableAdapter implements AdhListing.IListingContainerAdapter {
    public elemRefs(container : AdhResource.Content<SICommentable.HasAdhocracySampleSheetsCommentICommentable>) {
        return Util.latestVersionsOnly(container.data["adhocracy_sample.sheets.comment.ICommentable"].comments);
    }

    public poolPath(container : AdhResource.Content<SICommentable.HasAdhocracySampleSheetsCommentICommentable>) {
        // NOTE: If poolPath is defined like this, answers to comments are placed
        // inside other comment. This should be changed if we prefer to flatten
        // the hierarchy.
        return Util.parentPath(container.path);
    }
}

export class CommentAdapter extends ListingCommentableAdapter implements AdhComment.ICommentAdapter<RICommentVersion> {
    create(settings) : RICommentVersion {
        var resource = new RICommentVersion(settings);
        resource.data["adhocracy_sample.sheets.comment.IComment"] =
            new SIComment.AdhocracySampleSheetsCommentIComment(settings);
        resource.data["adhocracy.sheets.versions.IVersionable"] =
            new SIVersionable.AdhocracySheetsVersionsIVersionable(settings);
        return resource;
    }

    createItem(settings) : RIComment {
        return new RIComment(settings);
    }

    // FIXME: move to a service
    derive<R extends ResourcesBase.Resource>(oldVersion : R, settings) : R {
        var resource = new (<any>oldVersion).constructor(settings);

        _.forOwn(oldVersion.data, (sheet, key) => {
            resource.data[key] = new sheet.constructor(settings);

            _.forOwn(sheet, (value, field) => {
                resource.data[key][field] = _.cloneDeep(value);
            });
        });

        resource.data["adhocracy.sheets.versions.IVersionable"] =
            new SIVersionable.AdhocracySheetsVersionsIVersionable({follows: [oldVersion.path]});

        return resource;
    }

    content(resource : RICommentVersion) : string;
    content(resource : RICommentVersion, value : string) : RICommentVersion;
    content(resource, value?) {
        if (typeof value !== "undefined") {
            resource.data["adhocracy_sample.sheets.comment.IComment"].content = value;
            return resource;
        } else {
            return resource.data["adhocracy_sample.sheets.comment.IComment"].content;
        }
    }

    refersTo(resource : RICommentVersion) : string;
    refersTo(resource : RICommentVersion, value : string) : RICommentVersion;
    refersTo(resource, value?) {
        if (typeof value !== "undefined") {
            resource.data["adhocracy_sample.sheets.comment.IComment"].refers_to = value;
            return resource;
        } else {
            return resource.data["adhocracy_sample.sheets.comment.IComment"].refers_to;
        }
    }

    creator(resource : RICommentVersion) : string {
        return resource.data["adhocracy.sheets.metadata.IMetadata"].creator;
    }

    creationDate(resource : RICommentVersion) : string {
        return resource.data["adhocracy.sheets.metadata.IMetadata"].item_creation_date;
    }

    modificationDate(resource : RICommentVersion) : string {
        return resource.data["adhocracy.sheets.metadata.IMetadata"].modification_date;
    }

    commentCount(resource : RICommentVersion) : number {
        return Util.latestVersionsOnly(resource.data["adhocracy_sample.sheets.comment.ICommentable"].comments).length;
    }
}
