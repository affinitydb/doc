#Affinity Javascript Interface for node.js
The [affinity-client.js](./sources/affinity-client_js.html) module defines a simple interface
between node.js and Affinity (via HTTP and the [server](./terminology.md#server)).
The interface is divided in three parts: [connection creation](#connection-creation),
[pathSQL access with JSON response](#pathsql-access-with-json-response), and
[object-friendly access](#object-friendly-access).

##Connection Creation
To establish a new connection, a client simply needs to do the following:

<pre>
  var lib_affinity = require('affinity-client');
  var lAffinity = lib_affinity.createConnection("http://user:password@localhost:4560/db/", {keepalive:false});
  ...
  lAffinity.terminate();
</pre>

This example is assuming that the server runs on `localhost` and listens to port `4560`, and that
the `affinity-client` module for node.js is properly installed. If a `user` is specified,
it determines the owner of the store. For a new store, the `password` is optional, and implies
encryption of the store. It is possible to omit both the `user` and `password` (i.e. `"http://localhost:4560/db/"`),
in which case a default store owner is used.

The resulting `lAffinity` object is the public interface of the connection, providing
[pathSQL](#pathsql-access-with-json-output) access via its `q` and `qCount` methods, and
[object-friendly](#object-friendly-access) access via the other methods (`qProto`, `createPINs`, `startTx`
etc.).

The connection can be created with `keepalive` or not. If `keepalive` is enabled,
then the resulting `lAffinity` object represents a physical connection, implying one
stable store session in the server, for the whole lifetime of that connection.
If `keepalive` is disabled, then the resulting `lAffinity` object represents an
abstract connection (which is effectively instantiating shorter physical connections
on demand).

Either way, `lAffinity` represents one logical connection, usable in one
logical execution thread. Concurrent access to the Affinity server requires
multiple instances of a connection.

The connection must be terminated by calling `terminate`.

Her's a link to more information [about streaming and pagination](./protobuf.md#about-streaming-and-pagination).

##pathSQL Access with JSON Response
This access path is self-sufficient and will feel most natural to people with SQL experience.
Simply emit statements such as:

<pre>
  var lOnResult = function(pError, pResult) { console.log(pResult[0].id); /* ... */ };
  lAffinity.q("INSERT (name, profession) VALUES ('Roger', 'Accountant');", lOnResult);
  /* ... */
  lAffinity.q("SELECT * WHERE EXISTS(name);", lOnResult);
</pre>

`pResult` is a parsed JSON response produced by Affinity.

Note that this simple access path does not include any ORM or any means of feeding
javascript objects (or JSON) directly to Affinity as input data (for example, it doesn't enable
saving a javascript object with properties `name` and `profession`, nor will it
automatically translate that intention into the `INSERT` statement shown just above).
This is addressed by the [object-friendly access methods](#object-friendly-access).

This is a very powerful access path nonetheless. 
For more information, please refer to the [pathSQL reference](./pathSQL reference.md).

####About Transaction Control with pure pathSQL Access
The [pathSQL](./pathSQL reference.md) language includes transaction control statements
such as `START TRANSACTION` and `COMMIT`. In order for these statements to produce the
desired effect, they must be executed in the context of a connection that spans at least
a whole transaction. Presently this can only be accomplished within a connection
where `keepalive` is enabled.

##Object-friendly Access
This access path complements pathSQL by allowing to create, retrieve and modify
`PIN` objects without any translation to or from a query language.

Our philosophy is different from traditional object-oriented database systems,
and similar to many recent graph and document databases:
distinct data objects are used to interact with the database, with no attempt
to interfere with the application's run-time object model. In other words, we
don't emulate the automatic object mapping of object-oriented databases,
and the developer is not expected to _subclass_ `PIN`, but rather to _use_
`PIN` as an accessor (and in-memory snapshot).

Here are some examples:

<pre>
  var lOnResult = function(pError, pResult) { /* ... */ };
  lAffinity.createPINs([{name:"Roger", profession:"Accountant"}], lOnResult);
  /* ... */
  lAffinity.qProto(
    "SELECT * WHERE EXISTS(name);",
    function(pE, pR)
    {
      lAffinity.startTx();
      pR[0].set("profession", "Lawyer");
      lAffinity.commitTx(lOnResult);
    });
</pre>

####PIN Interface
The `createPINs` and `qProto` methods return PIN objects. These objects implement
explicit property accessors (i.e. set/get methods), as a safe and simple way to track
changes to be effected in the db. Every PIN has the following members: 

 * `pid` _(variable)_:  
   The [PID](./terminology.md#pin-id-pid).
 * `refresh(pCallback)` _(method)_:  
   Fetches a new snapshot from the db, and updates the client-side
   (in-memory) representation accordingly. `pCallback` is a plain method
   of the form function(pError, pResponse){...}.
 * `set(pPropName, pPropValue, pCallbackObj)` _(method)_:  
   Resets `pPropName` to `pPropValue` immediately in
   the in-memory representation, and schedules a physical update in the db, upon completion of the
   current transaction. If no explicit transaction is currently running, then this call
   becomes an implicit transaction, and `pCallbackObj` is required in that case. `pCallbackObj` is expected
   to be of the form `{txend:function(pError, pResponse){...}}`. This method can be used to
   replace a scalar value with a collection (by passing an array as `pPropValue`), or to replace
   a collection with a scalar.
 * `get(pPropName)` _(method)_:  
   Returns the current in-memory value of `pPropName`.
 * `toPropValDict()` _(method [for debugging/introspection])_:  
   Returns a cloned read-only dictionary representation of all properties.
 * `getExtras()` _(method [for debugging/introspection])_:  
   Returns a cloned read-only dictionary representation of all property adornments (VT types, eids etc.).

####Collection Interface
When a PIN's property happens to be a [collection](./terminology.md#collection),
`PIN.get` will return an internal `Collection` object that essentially borrows the javascript
`Array`'s interface: `push`, `pop`, `shift`, `unshift`, `sort`, `reverse`, `splice`, `slice`, `toLocaleString`,
`toString`, `join`, and `concat` _(Note: all updating methods can accept an additional optional `pCallbackObj`
last argument, of the same form and serving the same purpose as in `PIN.set`)_. Javascript's `delete`
operator on elements of the collection is _not_ supported.

####About Special Data Types
Affinity proposes a more comprehensive array of [data types](./pathSQL reference.md#data-types)
than javascript's core native types. This leads to the following special cases:

 * representation of [collections](./terminology.md#collection):
   as described earlier, a javascript `Array` can be passed to `PIN.set` to specify a new
   collection; `PIN.get` always returns an internal `Collection` object (with an `Array`-like
   interface)
 * representation of [references](./terminology.md#pin-reference):
   to create a new reference value, use the connection's `makeRef` method;
   `PIN.get` always returns an internal `Ref` object
 * representation of [blobs](./terminology.md#blob):
   to create a new blob value, use a standard node.js Buffer object;
   `PIN.get` also returns a Buffer object
 * representation of urls:
   to create a `VT_URL` (as opposed to a `VT_STRING`), use the connection's `makeUrl` method;
   `PIN.get` always returns an internal `Url` object
 * compatibility with non-js Affinity applications:
   some applications, especially those designed natively in javascript, may not care about
   certain details such as the ideal (most compact, or most exact) representation of numeric values,
   but other applications may; in order to support a healthy coexistence, our javascript client library
   preserves the originally stored value types; in the future, more control may be provided

####About Transaction Control with Object-friendly Access
At the level of the Affinity kernel, presently, every protobuf stream is associated with
a topmost transaction. That allows the client library to use transactions without
`keepalive`. Within the protobuf context, transaction control is specified
via the connection's methods: `startTx`, `commitTx`, `rollbackTx`. In the future,
the two methods (pure pathSQL vs protobuf) may be further harmonized.
