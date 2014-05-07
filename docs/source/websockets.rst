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

  * NO notification is sent if one of the children of the resource is changed.
    FIXME Maybe we need a *recursive* mode that sends notifications in this
    case as well?  If so, do we need this now (definitely) or later (maybe)?

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
    FIXME Maybe we need a *recursive* mode that sends notifications in this
    case as well? If so, do we need this now (definitely) or later (maybe)?

* If resource is an ItemVersion:

  * If a direct successor version is created (whose "follows" link points to
    this version)::

        { "event": "new_successor",
          "resource": "RESOURCE_PATH",
          "successor": "SUCCESSOR_RESOURCE_PATH" }

  * NO notification is sent if an indirect successor is created (a successor of
    a successor).


FIXME How should we handle the case if the WS connection got accidentally
closed (e.g. due to timeout, temporary loss of Internet connection)? Most
simple case would be treat this just like a regular close and just remove the
lost client from the list of subscribers. (Meaning that afterwards it'll have
to issue new subscribe requests for all resources it's interested about, and it
won't know what happened in the meantime.) Or you we need a queuing mechanism
and later (after reconnect) sent all the missed events to the client? If so,
how does the client identify itself so it will be recognized as the same? Also,
what to do if the client didn't show up again after 15 min/1 hour/24 hours?


Error Messages Sent by the Server
---------------------------------

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
