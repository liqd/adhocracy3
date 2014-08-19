import RICommentVersion = require("../../Resources_/adhocracy_sample/resources/comment/ICommentVersion");

import AdhComment = require("./Comment");

export class CommentAdapter implements AdhComment.ICommentAdapter<RICommentVersion> {
    create() : RICommentVersion {
        var resource = new RICommentVersion();
        resource.data["adhocracy_sample.sheets.comment.IComment"] = {
            refers_to: null,
            content: null
        };
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
        // FIXME: For some reason, creator is a list in the backend.
        // We will talk to them and do something better than blindly
        // picking the first item as soon as possible.
        return resource.data["adhocracy.sheets.metadata.IMetadata"].creator[0];
    }
}
