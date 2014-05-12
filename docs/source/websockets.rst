Asynchronous Backend-Frontend Communication Via Web Sockets
===========================================================

The basic idea is very simple: clients need to be able to subscribe and
unsubscribe to (changes of) a given object.  If an object changes and a client
is subscribed to it, that client will receive a notification.

We implement this by opening one web-socket per client (= frontend) at the
beginning of a session.  Subscribe and unsubscribe requests are sent from
client to server (= backend), and change notifications are sent from server to
client.  The client is responsible to handle and dispatch each particular
change to the parts of the GUI that care about it.


Client Messages
---------------

Both client and server send messages in JSON format.

Client messages have the following structure::

    { "action": "ACTION", "resource": "RESOURCE_PATH" }

ACTION is one of:

* "subscribe" to start receiving updates about a resource. If the client has
  already sent an earlier subscribe request for that resource, the new request
  is silently ignored.
* "unsubscribe" to stop receiving updates about a resource. If the client
  is not currently subscribed to that resource, the request is silently
  ignored.

For example::

    { "action": "subscribe", "resource": "/adhocracy/prop1/" }

And later::

    { "action": "unsubscribe", "resource": "/adhocracy/prop1/" }


Server Messages
---------------

Whenever one of the subscribed resources is changed, the server sends a message
to the client.  Which messages are sent depends on the type of the resource
that has been subscribed.

* If resource is a Simple (e.g. a Tag):

  * If the value of the Simple has changed::

        { "event": "modified", "resource": "RESOURCE_PATH" }

* If resource is a Pool:

  * If some of the Pool's metadata has changed (e.g. its title)::

        { "event": "modified", "resource": "RESOURCE_PATH" }

    (Same as with Simples.)

  * If a new child (sub-Pool or Item) is added to the Pool::

        { "event": "new_child",
          "resource": "RESOURCE_PATH",
          "child": "CHILD_RESOURCE_PATH" }

  * If a child (sub-Pool or Item) is removed from the Pool::

        { "event": "removed_child",
          "resource": "RESOURCE_PATH",
          "child": "CHILD_RESOURCE_PATH" }

  * If a child (sub-Pool or Item) in the Pool is modified::

        { "event": "modified_child",
          "resource": "RESOURCE_PATH",
          "child": "CHILD_RESOURCE_PATH" }

  (rationale: remove and modify messages are interesting: a pool is
  probably rendered as a table of contents, and if the title of an
  object changes, or if an object is removed, the table of contents
  must be re-rendered.)

* If resource is an Item (e.g. a Proposal):

  * If a new sub-Item is added to the Item (e.g. a Section)::

        { "event": "new_child",
          "resource": "RESOURCE_PATH",
          "child": "CHILD_RESOURCE_PATH" }

    (Same as with Pool:.)

  * If a new ItemVersion is added to the Item::

        { "event": "new_version",
          "resource": "RESOURCE_PATH",
          "version": "VERSION_RESOURCE_PATH" }

  * NO notification is sent if one of the sub-Items is changed, e.g. if a new
    sub-Section or SectionVersion is added to a Section within this Item.
    (Usually, the top-level Item (e.g. a Proposal) will be changed every time
    a sub-Item is changed.  If the frontend wants to keep track of isolated
    changes in a sub-Item, it needs to subscribe to it explicitly.)

* If resource is an ItemVersion:  FIXME: not sure if this is needed.

  * If a direct successor version is created (whose "follows" link points to
    this version)::

        { "event": "new_successor",
          "resource": "RESOURCE_PATH",
          "successor": "SUCCESSOR_RESOURCE_PATH" }

  * NO notification is sent if an indirect successor is created (a successor of
    a successor).


Error Messages Sent by the Server
---------------------------------

FIXME: should the server also respond with an "OK" to each subscribe /
unsubscribe?  then the server could complain about duplicates without
having to interrupt anything (the client will still be free to ignore
the message).

FIXME: if we don't allow subscription to ItemVersions, should there be
a "not-ok" message?

If the server doesn't understand a request sent by the server, is responds with
an error message::

    { "error": "ERROR_CODE", "details:" "DETAILS" }

ERROR_CODE will be one of the following:

* "unknown_action" if the client asked for an action that the server doesn't
  understand (neither "subscribe" nor "unsubscribe"). DETAILS contains the
  unknown action.
* "unknown_resource" if a client specified a resource path that is unknown to
  the server. DETAILS contains the unknown resource path.
* "malformed_message" if the client sent a message that cannot be parsed as
  JSON. DETAILS contains a parsing error message.
* "invalid_json" if the client sent a message this is JSON but doesn't contain
  the expected information (for example, if it's a JSON array instead of a JSON
  object or if "action" or "resource" keys are missing or their values aren't
  strings). DETAILS contains a short description of the problem.


Re-Connects
-----------

There is no way to recover the state of a broken connection.  The
backend handles every disconnect by discarding all subscriptions.

Therefore, if the WS connection ends for any reason, the frontend must
re-connect, flush its cache, and reload and re-subscribe to every
resource that are still relevant.

(FUTURE WORK: If WS connections prove to be unstable enough to make
the above aproach cause too much overhead, the backend may maintain
the session for a configurable amount of time.  If the frontend
re-connects in that time window and presents a session key, it will
receive a list of change notifications that it missed during the
broken connection, and it won't have to flush its cache.  The session
key could either be negotiated over the WS, or there may be some token
provided by substance_d / angular / somebody that can be used for
this.)


Implicit Notifications
----------------------

FIXME See the FIXME's above and decide how to handle such additional/indirect
changes. Consider the YAGNI principle: we don't want to implement anything
unless we're sure we'll need it.

there will probably be requirements about subscribing to constellations of
objects (e.g. a proposal and all its paragraphs). for the first
implementation, the client should do all of these by hand.

that means that if i subscribe to a proposal, i will be notified if a new
paragraph is added, but not if an old paragraph is changed.

actually, this may not be what we want.  an alternative would be to always
implicitly notify the client about changes of all sub-items (for documents:
sections, sub-...-sections, paragraphs).

i think which is better depends on how large the sub-item-structures will
get.  the client can be implemented either way, and it would cost little to
change from one implementation to the other later.
