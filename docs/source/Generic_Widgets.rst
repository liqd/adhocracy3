
    // a note on heterogenous lists.
    //
    // rationale: on the one hand, we want to be able to restrict element
    // types in the implementation of the listing and row widgets.  this
    // has the benefit of giving concise implementations for specific
    // container and element types, and makes the task of deriving new
    // such types much less complex and much more robust.
    //
    // on the other hand, we want to allow for lists that contain a wide
    // range of different elements in different rows, and we want to
    // dispatch a different widget for each row individually.  this is the
    // idea of hetergenous containers, and it can be easily implemented
    // with a class HeterogenousListingElementAdapter that extends
    // ListingElementAdapter.


