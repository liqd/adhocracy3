import AdhResource = require("../../Resources");

import AdhComment = require("./Comment");

// FIXME: use generated type instead
export interface ICommentData {
    "adhocracy_sample.sheets.comment.IComment" : {
        content : string;
        refers_to : string;
    };
    "adhocracy.sheets.metadata.IMetadata"? : {
        creator : string;
    };
}

export class CommentAdapter implements AdhComment.ICommentAdapter<AdhResource.Content<ICommentData>> {
    create() : AdhResource.Content<ICommentData> {
        return {
            content_type: "adhocracy_sample.resources.comment.ICommentVersion",
            data: {
                "adhocracy_sample.sheets.comment.IComment": {
                    content: undefined,
                    refers_to: undefined
                }
            }
        };
    }

    content(res : AdhResource.Content<ICommentData>) : string;
    content(res : AdhResource.Content<ICommentData>, value : string) : AdhResource.Content<ICommentData>;
    content(res, value?) {
        if (typeof value !== "undefined") {
            res.data["adhocracy_sample.sheets.comment.IComment"].content = value;
            return res;
        } else {
            return res.data["adhocracy_sample.sheets.comment.IComment"].content;
        }
    }

    refersTo(res : AdhResource.Content<ICommentData>) : string;
    refersTo(res : AdhResource.Content<ICommentData>, value : string) : AdhResource.Content<ICommentData>;
    refersTo(res, value?) {
        if (typeof value !== "undefined") {
            res.data["adhocracy_sample.sheets.comment.IComment"].refers_to = value;
            return res;
        } else {
            return res.data["adhocracy_sample.sheets.comment.IComment"].refers_to;
        }
    }

    creator(res : AdhResource.Content<ICommentData>) : string {
        return res.data["adhocracy.sheets.metadata.IMetadata"].creator;
    }
}
