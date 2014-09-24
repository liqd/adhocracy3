import _ = require("lodash");

import AdhResource = require("../../Resources");
import ResourcesBase = require("../../ResourcesBase");
import RICommentVersion = require("../../Resources_/adhocracy_core/resources/comment/ICommentVersion");
import RIComment = require("../../Resources_/adhocracy_core/resources/comment/IComment");
import SIVersionable = require("../../Resources_/adhocracy_core/sheets/versions/IVersionable");
import SICommentable = require("../../Resources_/adhocracy_core/sheets/comment/ICommentable");
import SIComment = require("../../Resources_/adhocracy_core/sheets/comment/IComment");

import AdhListing = require("../Listing/Listing");
import Util = require("../Util/Util");

import AdhComment = require("./Comment");


export class ListingCommentableAdapter implements AdhListing.IListingContainerAdapter {
    public elemRefs(container : AdhResource.Content<SICommentable.HasAdhocracyCoreSheetsCommentICommentable>) {
        return Util.latestVersionsOnly(container.data["adhocracy_core.sheets.comment.ICommentable"].comments);
    }

    public poolPath(container : AdhResource.Content<SICommentable.HasAdhocracyCoreSheetsCommentICommentable>) {
        return container.data["adhocracy_core.sheets.comment.ICommentable"].post_pool;
    }
}

export class CommentAdapter extends ListingCommentableAdapter implements AdhComment.ICommentAdapter<RICommentVersion> {
    create(settings) : RICommentVersion {
        var resource = new RICommentVersion(settings);
        resource.data["adhocracy_core.sheets.comment.IComment"] =
            new SIComment.AdhocracyCoreSheetsCommentIComment(settings);
        resource.data["adhocracy_core.sheets.versions.IVersionable"] =
            new SIVersionable.AdhocracyCoreSheetsVersionsIVersionable(settings);
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

        resource.data["adhocracy_core.sheets.versions.IVersionable"] =
            new SIVersionable.AdhocracyCoreSheetsVersionsIVersionable({follows: [oldVersion.path]});

        return resource;
    }

    content(resource : RICommentVersion) : string;
    content(resource : RICommentVersion, value : string) : RICommentVersion;
    content(resource, value?) {
        if (typeof value !== "undefined") {
            resource.data["adhocracy_core.sheets.comment.IComment"].content = value;
            return resource;
        } else {
            return resource.data["adhocracy_core.sheets.comment.IComment"].content;
        }
    }

    refersTo(resource : RICommentVersion) : string;
    refersTo(resource : RICommentVersion, value : string) : RICommentVersion;
    refersTo(resource, value?) {
        if (typeof value !== "undefined") {
            resource.data["adhocracy_core.sheets.comment.IComment"].refers_to = value;
            return resource;
        } else {
            return resource.data["adhocracy_core.sheets.comment.IComment"].refers_to;
        }
    }

    creator(resource : RICommentVersion) : string {
        return resource.data["adhocracy_core.sheets.metadata.IMetadata"].creator;
    }

    creationDate(resource : RICommentVersion) : string {
        return resource.data["adhocracy_core.sheets.metadata.IMetadata"].item_creation_date;
    }

    modificationDate(resource : RICommentVersion) : string {
        return resource.data["adhocracy_core.sheets.metadata.IMetadata"].modification_date;
    }

    commentCount(resource : RICommentVersion) : number {
        return Util.latestVersionsOnly(resource.data["adhocracy_core.sheets.comment.ICommentable"].comments).length;
    }
}
