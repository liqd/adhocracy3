import RICommentVersion = require("../../Resources_/adhocracy_sample/resources/comment/ICommentVersion");

import AdhComment = require("./Comment");

export class CommentAdapter implements AdhComment.ICommentAdapter<RICommentVersion> {
    create() : RICommentVersion {
        var res = new RICommentVersion();
        res.data["adhocracy_sample.sheets.comment.IComment"] = {
            refers_to: null,
            content: null
        };
        return res;
    }

    content(res : RICommentVersion) : string;
    content(res : RICommentVersion, value : string) : RICommentVersion;
    content(res, value?) {
        if (typeof value !== "undefined") {
            res.data["adhocracy_sample.sheets.comment.IComment"].content = value;
            return res;
        } else {
            return res.data["adhocracy_sample.sheets.comment.IComment"].content;
        }
    }

    refersTo(res : RICommentVersion) : string;
    refersTo(res : RICommentVersion, value : string) : RICommentVersion;
    refersTo(res, value?) {
        if (typeof value !== "undefined") {
            res.data["adhocracy_sample.sheets.comment.IComment"].refers_to = value;
            return res;
        } else {
            return res.data["adhocracy_sample.sheets.comment.IComment"].refers_to;
        }
    }

    creator(res : RICommentVersion) : string {
        // FIXME: For some reason, creator is a list in the backend.
        // We will talk to them and do something better than blindly
        // picking the first item as soon as possible.
        return res.data["adhocracy.sheets.metadata.IMetadata"].creator[0];
    }
}
