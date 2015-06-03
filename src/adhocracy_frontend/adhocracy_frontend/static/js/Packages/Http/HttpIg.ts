/// <reference path="../../../lib/DefinitelyTyped/jasmine/jasmine.d.ts"/>
/// <reference path="../../../lib/DefinitelyTyped/angularjs/angular.d.ts"/>
/// <reference path="../../_all.d.ts"/>

import AdhPreliminaryNames = require("../PreliminaryNames/PreliminaryNames");

import ResourcesBase = require("../../ResourcesBase");

import RIDocument = require("../../Resources_/adhocracy_core/resources/document/IDocument");
import RIDocumentVersion = require("../../Resources_/adhocracy_core/resources/document/IDocumentVersion");
import RITag = require("../../Resources_/adhocracy_core/interfaces/ITag");
import SIDocument = require("../../Resources_/adhocracy_core/sheets/document/IDocument");
import SITag = require("../../Resources_/adhocracy_core/sheets/tags/ITag");
import SIVersionable = require("../../Resources_/adhocracy_core/sheets/versions/IVersionable");

import AdhHttp = require("./Http");
import AdhMetaApi = require("./MetaApi");

export var register = (angular, config, meta_api) => {
    var factory = ($http, $q, $timeout) => {
        $http.defaults.headers.common["X-User-Token"] = "SECRET_GOD";
        $http.defaults.headers.common["X-User-Path"] = "/principals/users/0000000";

        var preliminaryNames = new AdhPreliminaryNames.Service();
        var adhMetaApi = new AdhMetaApi.MetaApiQuery(meta_api);

        var adhCredentialsMock = <any>{
            ready: $q.when(true)
        };

        return (new AdhHttp.Service($http, $q, $timeout, adhCredentialsMock, adhMetaApi, preliminaryNames, config));
    };
    factory.$inject = ["$http", "$q", "$timeout"];

    describe("$http.get and AdhHttp.getRaw", () => {
        var adhHttp : AdhHttp.Service<any> = angular.injector(["ng"]).invoke(factory)();

        // FIXME: there is a work-around for this problem in Error.ts
        // in function logBackendError.  if this test is re-enabled
        // and the underlying issue is fixed, remove the work-around.
        xit("do not lose error response status and body.", (done) => {
            adhHttp.getRaw("/does/not/exist").then(
                (response) => {
                    expect("should not succeed").toBe(true);
                    done();
                },
                (error) => {
                    expect(error.status).not.toBe(0);
                    expect(error.data).not.toBe(null);
                    done();
                }
            );
        });
    });

    var documentName = "Against_Curtains_" + Math.random();
        // (we don't have a way yet to repeat this test without having
        // to come up with new names every time, so we just
        // randomise.)

    describe("withTransaction", () => {
        var adhHttp : AdhHttp.Service<any> = angular.injector(["ng"]).invoke(factory)();
        var adhPreliminaryNames = new AdhPreliminaryNames.Service();

        it("Deep-rewrites preliminary resource paths.", (done) => {
            var poolPath = "/adhocracy";
            var cb = (transaction : any) : angular.IPromise<void> => {
                var document : AdhHttp.ITransactionResult =
                    transaction.post(poolPath, new RIDocument({preliminaryNames: adhPreliminaryNames, name: documentName}));
                var documentVersionResource = new RIDocumentVersion({preliminaryNames: adhPreliminaryNames});
                documentVersionResource.data[SIDocument.nick] =
                    new SIDocument.Sheet({
                        title: documentName,
                        description: "whoof",
                        picture: undefined,
                        elements: [sectionVersion.path]
                    });
                documentVersionResource.data[SIVersionable.nick] =
                    new SIVersionable.Sheet({
                        follows: [document.first_version_path]
                    });
                transaction.post(document.path, documentVersionResource);

                return transaction.commit()
                    .then((responses) : angular.IPromise<ResourcesBase.Resource> => {
                        var lastTagPath : string = responses[document.index].path + "LAST";
                        return adhHttp.get(lastTagPath);
                    })
                    .then((lastTag : RITag) => {
                        var lastVersionPaths : string[] = lastTag.data[SITag.nick].elements;
                        expect(lastVersionPaths.length).toBe(1);
                        expect(lastVersionPaths[0].substring(lastVersionPaths[0].length - 4)).toBe("001/");
                    })
                    .then(() => {
                        done();
                    }, (error) => {
                        expect(error).toBe(true);
                        done();
                    });
            };

            adhHttp.withTransaction(cb);
        });
    });

    describe("postNewVersionNoFork", () => {
        var adhHttp : AdhHttp.Service<any> = angular.injector(["ng"]).invoke(factory)();
        var adhPreliminaryNames = new AdhPreliminaryNames.Service();

        it("Identifies backend 'no fork allowed' error message properly.", (done) => {
            var firstVersionPath = "/adhocracy/" + documentName + "/VERSION_0000000/";
            var documentVersionResource = new RIDocumentVersion({preliminaryNames: adhPreliminaryNames});
            documentVersionResource.data[SIDocument.nick] = new SIDocument.Sheet({
                title: documentName,
                description: "whoof",
                picture: undefined,
                elements: []
            });

            adhHttp.postNewVersionNoFork(firstVersionPath, documentVersionResource).then(
                (response) => {
                    expect(true).toBe(true);
                    done();
                },
                (error) => {
                    expect(error).toBe(false);
                    done();
                }
            );
        });
    });
};
