Adhocracy Generic Widgets
=========================


Introduction
------------

In the context of the adhocracy software project, a *widget* is an
element of the UI. In the JavaScript frontend, this is implemented
as a class for creating angular directives.  Widgets are called
*generic* because the set of content types and UI contexts they can
be used with can be configured quite flexibly.

This document outlines implementation and usage of widgets.  It
assumes some familiarity with angularjs and typescript.


Adapters Classes
----------------

An adapter class provides a uniform interface to resources of
different content types that share some structure (in the most common
case, property sheets).  It can be considered the *glue* between
widgets and resources.

Example::

    export class AbstractListingContainerAdapter {
        public elemRefs(container : any) : string[] {
            return [];
        }
    }

    export class ListingPoolAdapter extends AbstractListingContainerAdapter {
        public elemRefs(container : Types.Content<Resources.HasIPoolSheet>) {
            return container.data["adhocracy.sheets.pool.IPool"].elements;
        }
    }

Both adapters provide a method ``elemRefs`` that consume a container
resource of a given content type, and return a list of paths to more
resources, namely the elements in the container.

The first class does not expect anything from the container it gets
passed and always returns the empty list.

The second requires the container to have the ``Pool`` sheet and gets
the element paths from there.


Scope Interfaces
----------------

Widget scopes must be typed in the controller.  The concrete type may
depend on type parameters of the generic Widget class type.

Example::

    export interface ListingScope<Container> {
        path: string;
        title: string;
    }

    export class Listing<Container ...>
        [...]
        scope: {
            path: "@",
            title: "@"
        },
        transclude: true,
        controller: [
            "$scope",
            function($scope: ListingScope<Container>) : void
            {
                [...]
            }

.. REVIEW: I do not think this section belongs here. Scope interfaces
   are not specific to widgets

.. REVIEW[mf]: (answer to all REVIEW markers in this file and commit.)
   i want to believe that the documentation has some value,
   independetly of the questions whether it belongs into this
   particular file or whether it is redundant.  i would like to not
   remove anything, but i realized that perhaps we should merge this
   file and the JS_Policy file, and make it a considerably larger
   thing more suitably called "a hacker's guide to the a3 frontend
   code"?  if there are no objections, I propose to (1) merge this PR
   into master, (2) rebase 2014-05-mf-js-guidelines+1 behind it,
   and (3) re-organize both JS_Guidelines.rst and this file into a
   more coherent Frontend_Guide.rst as part of
   2014-05-mf-js-guidelines+1.  (we could also postpone this, and
   leave it as a FIXME in JS_Guidelines for now.)


Widget Classes
--------------

A simple widget class has the following form::

    export class WidgetName<TypeParamters ...>
    {
        public static ...

        constructor(
            injectedService1,
            injectedService2,
            public classParameter
        ) {
            ...
        }

        public createDirective() {
            var _self = this;
            var _class = (<any>_self).constructor;

            return {
                restrict: ...
                templateUrl: ...
                scope: ...
                controller: [
                    "$scope",
                    "adhHttp",
                    (
                        $scope: TypeParameter,
                        ...
                    ) =>
                    {
                        ...
                    }
                ];
            };
        }
    }

The declaration of ``_self`` and ``_class`` should be used like this
in all instance methods that make use of them.  ``this`` with all its
rich semantics can then be used without interfering with the two.

.. REVIEW: I do not think the note about _self and_class belongs here.
   It is not specific to widgets. They should also be removed from the
   code examples.

``createDirective`` is used for registering a new directive::

    app.directive(
        "adhListing",
        [
            "$q",
            ($q) => new Widgets.Listing(new Widgets.ListingElementAdapter($q)).createDirective()
        ]
    );

This makes the directive ``<adh-listing>`` available.  The ``Listing``
constructor (in this example) takes one class parameter, namely an
adapter instance that expects injection of the asynchronicity service
``$q``.  In order to inject the service into the class parameter's
constructor, an extra function call is wrapped around createDirective.

There are several ways in which behavior of existing widgets can be
changed to adapt to new requirements.


Static class attributes and extension
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Example::

    export class SomeWidget
    {
        public static templateUrl: string = "/Widgets/Listing.html";

        ...

        public createDirective() {
            var _self = this;
            var _class = (<any>_self).constructor;

            return {
                templateUrl: _class.templateUrl;
                ...

Directives constructed from ``SomeWidget`` will always use the same
template, no matter where used.  If you want to change the template,
write the following trivial extension class::

    export class SomeWidgetForSomeFancyClient extends SomeWidget
    {
        public static templateUrl: string = "/Widgets/FancyListing.html";
    }


Constructor Params
~~~~~~~~~~~~~~~~~~

If you want to decide on behavior every time you register a directive,
you can add constructor parameters::

    export class SomeWidget
    {
        constructor(public title: string) {
            return;
        }

        public createDirective() {
            var _self = this;
            var _class = (<any>_self).constructor;

            return {
                controller: ($scope) =>
                    {
                        $scope.title = _self.title;
                        ...


Directive element body
~~~~~~~~~~~~~~~~~~~~~~

The angular directive ``ngRepeat`` copies its body once for every
element in an array, and inserts all copies into the DOM tree rendered
from the template.  You can do this with adhocracy widgets as well.
As above and very similar to ``ngRepeat``, assume we have a listing
widget that lists every element in a form outlined in the body.

The listing template will contain::

    <span ng-transclude></span>

(Whether by accident or by design, ``ngTransclude`` is restricted to
``AC``, so it can only occur as an XML attribute, not as an element.)

The object returned by ``createDirective`` in the widget class must
have the following attribute::

    transclude: true

And finally, the widget caller must add something to the element
body::

    <adh-listing path="/adhocracy/Proposals">
        <adh-element></adh-element>
    </adh-listing>

[FIXME: document scope propagation; see FIXME near class
Widget.Listing.  i think in order to get this done, we need to write
our own transclude function and inject it to the directive's link
attribute.]

.. REVIEW: This is described in the angular docu and is not specific to
   adhocracy


Misc Ideas and Remarks
----------------------


Heterogeneous Listings
~~~~~~~~~~~~~~~~~~~~~~

If we wanted to specify search results that contain a range of
heterogeneous objects, writing the adapter is slightly more
challenging: On the one hand, we may want to do something specific
where possible, such as allowing for inline-comments::

    export class ListingElementWithCommentsAdapter extends ... {
        public renderCommentButton: ... = ...
        ...
    }

On the other, we want do not want to insist that it is possible for
all elements.

The solution is to resort to dynamic checks::

    export class ArbitraryListingElementAdapter extends ... {
        public renderItAll(...) {
            ...
            if('comments' in self) {
                ...
            } else {
                ...  // (do some padding where the comment button is missing)
            }
            if('votes' in self) {
                ...
            }
            ...

So the idea of statically typed adapter hierarchies works, but can be
extended to dynamically typed ones that are arbitrarily flexible.
When maintaining and developing adhocracy, you can always pick the
adapter closest to what you need, and you will get less code that is
more robust and easier to read.
