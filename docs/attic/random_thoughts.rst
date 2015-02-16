Random Thoughts
---------------

object hierarchy
~~~~~~~~~~~~~~~~

must be optional: when posting a new document into a pool, the server
does not consider the structure of the path of the pool, but the type
of the supergraph node denoted by the path.  this way, a user can
decide to install an a3 instance that has transparent rest paths or
not, and someone can implement a new backend that does not support
transparent paths.  rationale: there is a trade-off between data
security requirements ("information must not be leaked through URLs")
and usability requirements ("URLs must be informative").  users should
be able to make different decisions.

authorisation management: a server implementation MAY require an
object hierarchy for authorization management purposes, but the
protocol MUST be independent of this in the sense that it must be
possible to implement a trusting server that that allows full
read/write access to the complete supergraph for everybody under
unstructured paths.


lazy / bulk loading
~~~~~~~~~~~~~~~~~~~

should there be rest machinery for pulling supergraph nodes partially?
no: keeping nodes atomic reduces protocol complexity enormously.  it
is in the responsibility of the data model designer that nodes are
never getting too large.  if there is a list of outgoing edges in a
node and that list is growing too big, the model designer can choose
to replace the list by a reference, and move the actual list into the
list node that reference points to.

bulk get / post: yes, we want that.

should the supergraph structure be kept intact on the client side?
yes!  if the client wants to submit an update, it needs to know where
nodes end and edges start, and cannot have a molten pile of nodes in
one json object.  (the following client implementation approach is
flawed: supergraph node references are path strings, and following a
references is implemented by ajax-getting that path and replacing the
path by it in the object.  this would give the client enough
information to render the GUI, but when the nodes are to be posted
back to the server because they have changed, the client has no way of
knowing which attributes were originally internal to one node, and
which were edges.)


marker vs. property sheet interfaces
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

property sheet interfaces are called e.g.
"adhocracy_core.propertysheet.ILikeable", marker interfaces e.g.
"adhocracy_core.content.IProposal".

backend implementation: the goal is that schemas should be defined in
a maximally concise way.  colander schema, management view, rest view,
etc. are generated automatically, but not magically from that concise
representation.

concise schemas can have the following forms:

 - "propsheet1 = {field1: type1, field2: type2, ...}".

 - "marker1 = [propsheet1, propsheet5, propsheet2, ...]"

 - inheritance for markers: "markerx = markera + markerb + {propsheet12}".

 - inheritance for propsheets: "propsheet12 = propsheet1 + {field18: type18}".

some of this is provided by colander.  ideally, the backend could be
made much less redundant by using colander more masterly.


structure of the json objects communicated over the rest api
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

since substance d is used as backend platform, the data model follows
zope concepts and conventions.  but there is more.

usually, a rest resource corresponds to a supergraph node (there may
be other resources). it has the following structure:

{ content-type: ..., path: ..., data: ... }

content-type is a string that contains the type stored under data.  it
may be "adhocracy_core.content.I*" or the typeof-string-representation of a
javascript primitive type.  in this case, the data attribute will
contain a json literal, not an object or a list of objects.  (what
about 'Object'?  'Function'?)

path is a string that is the key of the resource.

data is everything else.  it may be missing, in which case an ajax
call will be triggered by the client if and when necessary, along the
lines of:

var x = { content-type: ..., path: ... };

// force:
x.data = $.ajax('GET', x.path).data;

once the data attribute is retrieved, it consists of an object that
has one attribute for each property sheet interface implemented by the
resource.  the value of each property sheet interface attribute
depends entirely on the data model, except that it may contain further
lazily fetchable resources.

note now that the content-type may NOT be
"adhocracy_core.propertysheet.I*": a resource (as it's usually a supergraph
node) implements a marker interface, and contains all data required by
all property sheet interfaces subsumed in that marker interface.
marker interfaces can be viewed as property sheet interface sets.
since property sheet interfaces retrieval is never delayed like
retrieval of referenced resources, there is no need to wrap them in an
object containing a content-type, a path, and a data attribute.

"content-type" is a reserved keyword in this api because of the
special way it can be used to control selecting more resources for
transport over the rest api (in either direction).

the meta attribute from the prototype will go away.  some of the
information it contains can move to the data section of resource
objects, some is unnecessary, and content-type and path are already
taken care of.


dynamic content
~~~~~~~~~~~~~~~

a resource / supergraph node is a python object.  the last chapter
explains how to send attributes of those python objects to the client.
what about the methods?

the rest api is indifferent towards where the json object in the GET
response is coming from (specifically whether it is from a database
lookup or some on-demand computation).  for the client, there is
therefore no difference between an attribute and a method: in both
cases, some property sheet interface attribute contains an attribute
with a content object missing the data attribute as value.  in the
first case, if the path is called, a lookup will take place; in the
second, a python method will be called.

only that's not true.  there are at least two differences: methods can
have arguments, but attributes can't.  and there is no way of telling
in general whether invoking a method twice yields the same return
value.

rest apis do not provide any mechanism for sending functions or
function calls to the server for evaluation, so there is no way of
passing arguments to a method to be invoked.  (of course, there are
many obvious ways: the arguments just need to be encoded in the url
somehow.  but that would be rest-ish, not rest.)
