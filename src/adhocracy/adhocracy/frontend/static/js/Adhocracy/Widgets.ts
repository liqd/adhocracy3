/// <reference path="../../submodules/DefinitelyTyped/requirejs/require.d.ts"/>
/// <reference path="../../submodules/DefinitelyTyped/angularjs/angular.d.ts"/>
/// <reference path="../../submodules/DefinitelyTyped/underscore/underscore.d.ts"/>
/// <reference path="../_all.d.ts"/>

import angular = require("angular");
import _ = require("underscore");

import Types = require("Adhocracy/Types");
import Util = require("Adhocracy/Util");
import Css = require("Adhocracy/Css");
import AdhHttp = require("Adhocracy/Services/Http");
import AdhWS = require("Adhocracy/Services/WS");
import AdhCache = require("Adhocracy/Services/Cache");

import Resources = require("Adhocracy/Resources");

var templatePath : string = "/frontend_static/templates";



/*

  widgets are directive factories.  sort of...

  in:
     path to pool
       easy
  out:
     directive object
       also  contains accessor methods for content.  then those could be
       overloaded.

i think i like that idea good enough to implement it for listing.

*/

   // ok, type system trouble.  but it's clear why: the controller
   // must not see the content types, but call the accessor methods
   // and put whatever it finds there into a scope that always has the
   // same type.
   //
   // if, the widget is cloned and should change acceptable content
   // types, only the accessor methods need to be overloaded.  if the
   // behaviour should be changed, only controller and/or templateUrl
   // need to be overloaded.  (what if i want to recycle most of the
   // controller, but still extend it?)
   //
   // how can the type system be used to elegantly require a certain
   // set of mandatory (and, ideally, a certain set of optional)
   // property sheets?


export interface ListingScope<Container, Element> {
    container: Container;
    elements: Element[];
}

export interface ListingContainer extends Types.Content<any>, Resources.HasIPoolSheet {};

export interface ListingElement extends Types.Content<any> {};

export interface Listing<Container, Element> extends ng.IDirective {
    containerAccess: {
        elemRefs: (c: Container) => string[]
    };
    elementAccess: {
        name: (e: Element) => string;
        path: (e: Element) => string;
    };
}

export function listing(containerPath : string) {
    function factory() : Listing<ListingContainer, ListingElement>
    {
        return {
            restrict: "E",
            templateUrl: templatePath + "/Widgets/Listing.html",
            controller: ["$scope",
                         "adhHttp",
                         "adhHttp",
                         function($scope: ListingScope<ListingContainer, ListingElement>,
                                  adhHttpC: AdhHttp.IService<ListingContainer>,
                                  adhHttpE: AdhHttp.IService<ListingElement>
                                 ) : void
                {
                    adhHttpC.get(containerPath).then((pool) => {
                        $scope.container = pool;
                        $scope.elements = [];

                        var elemRefs : string[] = this.containerAccess.elemRefs($scope.container);
                        for (var x in elemRefs) {
                            (function(x : number) {
                                adhHttpE.get(elemRefs[x]).then((element : ListingElement) => $scope.elements[x] = element);
                            })(x);
                        }
                    })
                }
            ],
            containerAccess: {
                elemRefs: function(c: ListingContainer) {
                    return c.data["adhocracy.sheets.pool.IPool"].elements;
                }
            },
            elementAccess: {
                name: function(e: ListingElement) {
                    return "[content type " + e.content_type + ", resource " + e.path + "]"
                },
                path: function(e: ListingElement) {
                    return e.path;
                }
            }
        }
    }

    return factory;
}


/*


next: introduce Proposals in Listing clone, and replace
elementAccess.name.

next: introduce Proposal detail view in clone of the above, factor out
shared code from controller into helper attribute, and replace
controller.



export function wgtListingDocument(path:       string,
                            container:  Content<HasIDocumentSheet>,
                            element:    Content<HasIDocumentSheet>
                           ) : Directive
{
    return {
        restrict: "E"
        templateUrl: templatePath + "/Widgets/Listing.html",
        controller: ["$scope",
                     function($scope : IDocumentWorkbenchScope<Resources.HasIDocumentSheet>)



                     {
                     }]
    }
}

*/
