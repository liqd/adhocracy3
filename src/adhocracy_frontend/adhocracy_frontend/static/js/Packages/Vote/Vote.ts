import AdhConfig = require("../Config/Config");

var pkgLocation = "/Vote";


export enum VoteValue {
    pro,
    contra,
    neutral
};


export interface IVoteScope extends ng.IScope {
    refersTo : string;
    votes : {
        pro : number;
        contra : number;
        neutral : number;
    };
    active : VoteValue;
    isActive : (VoteValue) => string;  // css class name if VoteValue is active, or "" otherwise.
    cast(value : VoteValue) : void;
    update() : void;
}


export var createDirective = (adhConfig : AdhConfig.Type) => {
    return {
        restrict: "E",
        templateUrl: adhConfig.pkg_path + pkgLocation + "/Vote.html",
        scope: {
            refersTo: "@"
        },
        link: (scope : IVoteScope) => {
            scope.cast = (value : VoteValue) : void => {
                if (scope.isActive(value)) {
                    scope.votes[VoteValue[value]] -= 1;
                    delete scope.active;
                } else {
                    // decrease old value
                    if (scope.hasOwnProperty("active")) {
                        scope.votes[VoteValue[scope.active]] -= 1;
                    }
                    // increase new value
                    scope.votes[VoteValue[value]] += 1;
                    scope.active = value;
                }
            };

            delete scope.active;
            scope.isActive = (value : VoteValue) => (value === scope.active) ? "vote-button-active" : "";

            scope.update = () : void => {
                // FIXME: This sets some arbitrary data for now.
                // Instead, this should get the data from the server.
                scope.votes = {
                    pro: 10,
                    contra: 5,
                    neutral: 3
                };
            };

            scope.update();
        }
    };
};
