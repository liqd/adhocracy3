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

    // phantom types for easy type parameter reference
    cPhantom: Container;
    ePhantom: Element;
}

export interface Listing<Container, Element> extends ng.IDirective {
    containerAccess: {
        elemRefs: (c: Container) => string[]
    };
    elementAccess: {
        name: (e: Element) => string;
        path: (e: Element) => string;
    };
}

export var Listing = ["$scope", function(path: string, $scope: ListingScope<Resources.HasIPoolSheet, any>)
                                           : Listing<typeof $scope.cPhantom, typeof $scope.ePhantom>
{
    return {
        restrict: "E",
        templateUrl: templatePath + "/Widgets/WgtListing.html",
        controller: function() {

            throw "wef";

        },
        containerAccess: {
            elemRefs: function(c: Resources.HasIPoolSheet) { throw "wef"; return ['wef'] }
        },
        elementAccess: {
            name: function(e: any) {
                return "[unknown to widget: content type " + e.content_type + ", resource " + e.path + "]"
            },
            path: function(e: any) {
                return e.path;
            }
        }
    }
}];


/*

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
