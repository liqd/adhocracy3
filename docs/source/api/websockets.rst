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

Responses to Client Messages
++++++++++++++++++++++++++++

Status Confirmations
~~~~~~~~~~~~~~~~~~~~

If a client request was processed successfully by the server, it sends a status
confirmation::

    { "status": "STATUS", "action": "ACTION", "resource": "RESOURCE_PATH" }

STATUS is either:

* "ok" if the request was processed successfully and changed the internal state
  of the server.
* "redundant" if the request was unnecessary since it already corresponded to
  internal state of the server (the client tried to subscribe to a resource it
  has already subscribed or to unsubscribe from a resource it hasn't
  subscribed).

The "action" and "resource" fields repeat the corresponding values from the
client request.

Error Messages
~~~~~~~~~~~~~~

Otherwise, if the server didn't understand a request sent by the client or
could not handle it, it responds with an error message::

    { "error": "ERROR_CODE", "details": "DETAILS" }

ERROR_CODE will be one of the following:

* "unknown_action" if the client asked for an action that the server doesn't
  understand (neither "subscribe" nor "unsubscribe"). DETAILS contains the
  unknown action.
* "unknown_resource" if a client specified a resource path that is unknown to
  the server. DETAILS contains the unknown resource path.
* "malformed_message" if the client sent a message that cannot be parsed as
  JSON. DETAILS contains a parsing error message.
* "invalid_json" if the client sent a message that is JSON but doesn't contain
  the expected information (for example, if it's a JSON array instead of a JSON
  object or if "action" or "resource" keys are missing or their values aren't
  strings). DETAILS contains a short description of the problem.
* "internal_error" if an internal error occurred at the server. DETAILS
  contains a short description of the problem. In an ideal world,
  this will never happen.

Note that it is not always possible to provide action and resource of
the respective request (e.g. with "invalid_jason").  The client needs
to keep track of the order in which it sends the requests, and has to
associate the responses with that list.  Responses (errors or not) are
guaranteed to be sent to the frontend in the same order as requests
are sent to the backend.

Notifications
+++++++++++++

Whenever one of the subscribed resources is changed, the server sends a message
to the client.  Which messages are sent depends on the type of the resource
that has been subscribed.

* If resource is a Simple (e.g. a Tag):

  * If the value of the Simple has changed::

        { "event": "modified", "resource": "RESOURCE_PATH" }

  * If the Simple has been removed::

        { "event": "removed", "resource": "RESOURCE_PATH" }

    In practice this usually means that the resource has been marked as deleted
    or hidden (see :ref:`deletion`).

* If resource is a Pool:

  * If some of the Pool's metadata has changed (e.g. its title)::

        { "event": "modified", "resource": "RESOURCE_PATH" }

    (Same as with Simples.)

  * If the Pool has been removed::

        { "event": "removed", "resource": "RESOURCE_PATH" }

    (Same as with Simples.)

  * If a new child (sub-Pool or Item) is added to the Pool::

        { "event": "new_child",
          "resource": "RESOURCE_PATH",
          "child": "CHILD_RESOURCE_PATH" }

  * If a child (sub-Pool or Item) is removed from the Pool::

        { "event": "removed_child",
          "resource": "RESOURCE_PATH",
          "child": "CHILD_RESOURCE_PATH" }

    In practice this usually means that the resource has been marked as deleted
    or hidden (see :ref:`deletion`).

  * If a child (sub-Pool or Item) in the Pool is modified::

        { "event": "modified_child",
          "resource": "RESOURCE_PATH",
          "child": "CHILD_RESOURCE_PATH" }

    (Rationale for modify: a pool is probably rendered as a table of
    contents, and if the title of an object changes, the table of contents
    must be re-rendered.)

  * If anything that lies below the pool (children, grandchildren etc.) has
    been added, removed, or modified:

        { "event": "changed_descendant", "resource": "RESOURCE_PATH" }

    This event is sent only once per transaction and pool, even if multiple
    of its descendants have been modified. It tells the frontend that any
    *queries* previously sent to the pool should now be considered outdated,
    as query results can refer to grandchildren and other resources that lie
    below the pool, but aren't its direct children.

* If resource is an Item (e.g. a Proposal):

  * If a new sub-Item is added to the Item (e.g. a Section)::

        { "event": "new_child",
          "resource": "RESOURCE_PATH",
          "child": "CHILD_RESOURCE_PATH" }

    (Same as with Pool.)

  * If a new ItemVersion is added to the Item::

        { "event": "new_version",
          "resource": "RESOURCE_PATH",
          "version": "VERSION_RESOURCE_PATH" }

  * The other events sent as the same as for Pools, since all Items are also
    pools: "modified", "removed", "removed_child", "modified_child",
    "changed_descendant". The "modified_child" and "removed_child" events
    don't distinguish between sub-Items and ItemVersions -- both are
    considered children.

* If resource is an ItemVersion:

  * If a backreference in the version has changed::

        { "event": "modified", "resource": "RESOURCE_PATH" }

    This happens e.g. if a successor version has been created that refers to
    the subscribed version as its predecessor.

    Otherwise, versions are immutable, so updated backreferences (the
    reverse direction for a reference from another resource to this one) are
    the only thing that can trigger a "modified" event.

A note about resource removal: if a resource is removed (deleted or hidden),
any subscribers to it will automatically be unsubscribed, so they won't
receive further updates about this resource, even if it later "revealed"
(unhidden or undeleted) again. Subscribers to the parent pool will receive a
"new_child" or "new_version" message notifying them about the revealed
resource just as if it had been newly created.


Re-Connects
-----------

There is no way to recover the state of a broken connection.  The backend
handles every disconnect by discarding all subscriptions.

Therefore, if the WS connection ends for any reason, the frontend must
re-connect, flush its cache, and reload and re-subscribe to every resource that
is still relevant.

(POSSIBLE FUTURE WORK: If WS connections prove to be unstable enough to make
the above approach cause too much overhead, the backend may maintain the
session for a configurable amount of time.  If the frontend re-connects in
that time window and presents a session key, it will receive a list of change
notifications that it missed during the broken connection, and it won't have to
flush its cache.  The session key could either be negotiated over the WS, or
there may be some token provided by substance_d / angular / somebody that can
be used for this.)
