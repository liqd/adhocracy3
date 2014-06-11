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


Transclusion
~~~~~~~~~~~~~

You can use angular's `transclusion
<https://docs.angularjs.org/guide/directive#creating-a-directive-that-wraps-other-elements>`_
feature to pass a template snippet to the widget::

    <adh-listing path="/adhocracy/Proposals">
        <adh-element path="{{element}}"></adh-element>
    </adh-listing>

[FIXME: document scope propagation; see FIXME near class
Widget.Listing.  i think in order to get this done, we need to write
our own transclude function and inject it to the directive's link
attribute.]


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
