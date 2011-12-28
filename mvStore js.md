#mvStore Javascript Interface for node.js
The [mvstore-client.js](./sources/mvstore-client_js.html) module defines a simple interface
between node.js and mvStore (via HTTP and the the [mvServer](./terminology.md#mvserver)).
The interface is divided in three parts: [connection creation](#connection-creation),
[mvSQL access with JSON response](#mvsql-access-with-json-response), and
[object-friendly access](#object-friendly-access).

##Connection Creation
To establish a new connection, a client simply needs to do the following:

  var lib_mvstore = require('mvstore-client');
  var lMvStore = lib_mvstore.createConnection("http://user:password@localhost:4560/db/", {keepalive:false});
  ...
  lMvStore.terminate();

This example is assuming that mvServer runs on `localhost` and listens to port `4560`, and that
the `mvstore-client` module for node.js is properly installed. If a `user` is specified,
it determines the owner of the store. For a new store, the `password` is optional, and implies
encryption. It is possible to omit both the `user` and `password` (i.e. `"http://localhost:4560/db/"`),
in which case a default store owner is used.

The resulting `lMvStore` object is the public interface of the connection, providing
[mvSQL](#mvsql-access-with-json-output) access via its `mvsql` and `mvsqlCount` methods, and
[object-friendly](#object-friendly-access) access via the other methods (`mvsqlProto`, `createPINs`, `startTx`
etc.).

The connection can be created with `keepalive` or not. If `keepalive` is enabled,
then the resulting `lMvStore` object represents a physical connection, implying one
stable store session in the server, for the whole lifetime of that connection.
If `keepalive` is disabled, then the resulting `lMvStore` object represents an
abstract connection (which is effectively instantiating shorter physical connections
on demand).

Either way, `lMvStore` represents one logical connection, usable in one
logical execution thread. Concurrent access to the mvStore server requires
multiple instances of a connection.

The connection must be terminated by calling `terminate`.

##mvSQL Access with JSON Response
This access path is self-sufficient and will feel most natural to people with SQL experience.
Simply emit statements such as:

  var lOnResult = function(pError, pResult) { console.log(pResult[0].id); /* ... */ };
  lMvStore.mvsql("INSERT (name, profession) VALUES ('Roger', 'Accountant');", lOnResult);
  /* ... */
  lMvStore.mvsql("SELECT * WHERE EXISTS(name);", lOnResult);

`pResult` is a parsed JSON response produced by mvStore.

Note that this simple access path does not include any ORM or any means of feeding
javascript objects (or JSON) directly to mvStore as input data (for example, it doesn't enable
saving a javascript object with properties `name` and `profession`, nor will it
automatically translate that intention into the `INSERT` statement shown just above).
This is addressed by the [object-friendly access methods](#object-friendly-access).

This is a very powerful access path nonetheless. 
For more information, please refer to the [mvSQL reference](./mvSQL reference.md).

####About Transaction Control with pure mvSQL Access
The [mvSQL](./mvSQL reference.md) language includes transaction control statements
such as `START TRANSACTION` and `COMMIT`. In order for these statements to produce the
desired effect, they must be executed in the context of a connection that spans at least
a whole transaction. Presently this can only be accomplished within a connection
where `keepalive` is enabled.

##Object-friendly Access
This access path complements mvSQL by allowing to create, retrieve and modify
`PIN` objects without any translation to or from a query language.

Our philosophy is different from traditional object-oriented database systems,
and similar to many recent graph and document databases:
distinct data objects are used to interact with the database, with no attempt
to interfere with the application's run-time object model. In other words, we
don't emulate the automatic object mapping of object-oriented databases,
and the developer is not expected to _subclass_ `PIN`, but rather to _use_
`PIN` as an accessor (and in-memory snapshot).

Here are some examples:

  var lOnResult = function(pError, pResult) { /* ... */ };
  lMvStore.createPINs([{name:"Roger", profession:"Accountant"}], lOnResult);
  /* ... */
  lMvStore.mvsqlProto(
    "SELECT * WHERE EXISTS(name);",
    function(pE, pR)
    {
      lMvStore.startTx();
      pR[0].set("profession", "Lawyer");
      lMvStore.commitTx(lOnResult);
    });

####PIN Interface
The `createPINs` and `mvsqlProto` methods return PIN objects. These objects implement
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
mvStore proposes a more comprehensive array of [data types](./mvSQL reference.md#data-types)
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
 * compatibility with non-js mvStore applications:
   some applications, especially those designed natively in javascript, may not care about
   certain details such as the ideal (most compact, or most exact) representation of numeric values,
   but other applications may; in order to support a healthy coexistence, our javascript client library
   preserves the originally stored value types; in the future, more control may be provided

####About Transaction Control with Object-friendly Access
At the level of the mvStore kernel, presently, every protobuf stream is associated with
a topmost transaction. That allows the client library to use transactions without
`keepalive`. Within the protobuf context, transaction control is specified
via the connection's methods: `startTx`, `commitTx`, `rollbackTx`. In the future,
the two methods (pure mvSQL vs protobuf) may be further harmonized.

<p style="color:red">
REVIEW (maxw): expand, link to sample material etc.  
REVIEW (maxw): more on streaming  
</p>
