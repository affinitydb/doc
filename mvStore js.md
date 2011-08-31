#mvStore Javascript Interface for node.js
The [mvstore-client.js](../nodejs/mvstore-client/lib/mvstore-client.js) module defines a simple interface
between node.js and mvStore (via HTTP and the the [mvServer](./terminology.md#mvserver)).
The interface is divided in three parts: [connection creation](#connection-creation),
[mvSQL access with JSON response](#mvsql-access-with-json-response), and
[object-friendly access](#object-friendly-access).

##Connection Creation
To establish a new connection, a client simply needs to do the following:

  var lib_mvstore = require('mvstore-client');
  var lMvStore = lib_mvstore.createConnection("http://localhost:4560/db/");

This is assuming that mvServer runs on localhost and listens to port 4560, and that
the `mvstore-client` module for node.js is properly installed.

The resulting lMvStore object is the public interface of the connection, providing
[mvSQL](#mvsql-access-with-json-output) access via its `mvsql` and `mvsqlCount` methods, and
[object-friendly](#object-friendly-access) access via its `mvsqlProto`, `createPINs` and `txCtx` methods.

##mvSQL Access with JSON Response
This access path is self-sufficient and will feel most natural to people with SQL experience.
Simply emit statements such as:

  var lOnResult = function(pError, pResult) { ... };
  lMvStore.mvsql("INSERT (name, profession) VALUES ('Roger', 'Accountant');", lOnResult);
  lMvStore.mvsql("SELECT * WHERE EXISTS(name);", lOnResult);

pResult is a parsed JSON response produced by mvStore.

Note that this simple access path does not include any ORM or any means of feeding
javascript objects (or JSON) directly to mvStore as input data (for example, it doesn't enable
saving a javascript object with properties `name` and `profession`, nor will it
automatically translate that intention into the `INSERT` statement shown just above).
This is addressed by the [object-friendly access methods](#object-friendly-access).

This is a very powerful access path nonetheless. 
For more information, please refer to the [mvSQL reference](./mvSQL reference.md).

##Object-friendly Access
This access path complements mvSQL by allowing to create, retrieve and modify
`PIN` objects without any translation to or from a query language.

Our philosophy is similar to that of many recent graph and document databases,
where distinct data objects are used to interact with the database, with no attempt
to interfere with the application's run-time object model. In other words, we
don't emulate the automatic object mapping of object-oriented databases,
and the developer is not expected to subclass `PIN`.

Here are some examples:

  var lOnResult = function(pError, pResult) { ... };
  lMvStore.createPINs([{name:"Roger", profession:"Accountant"}], lOnResult);
  lMvStore.mvsqlProto("SELECT * WHERE EXISTS(name);", function(pE, pR) { var lTxCtx = lMvStore.txCtx(); pR[0].set("profession", "Lawyer", lTxCtx); lTxCtx.commit(lOnResult); });

<p style="color:red">
REVIEW (maxw): provide the complete PIN, Collection and TxCtx interfaces  
REVIEW (maxw): expand, link to sample material etc.  
REVIEW (maxw): more on transactions, once this is completed in the library and stabilized in the server  
REVIEW (maxw): more on streaming  
</p>
