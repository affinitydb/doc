#ChaosDB C++ Interface
Please read the brief [introduction](./terminology.md#c-interface). The
bulk of the interface is defined in [chaosdb.h](./sources/chaosdb_h.html).

The main purpose of ChaosDB's C++ interface is to provide a means of
integrating the ChaosDB database kernel into an embedding application, such as a
database server or an embedded system. The "bare-metal" nature of the interface
is meant to introduce no artificial overhead in those cases.

An essential part of the C++ interface is to give access to
[pathSQL](./terminology.md#pathsql) and [protocol-buffers](./terminology.md#protocol-buffer).
These two entry points are self-sufficient, and enable the writing of "normal" database client code.

However, the bulk of the C++ interface contains elements (such as [PIN creation](#isession::createpin-isession::createuncommittedpin)
and [modification](#ipin) methods, [expression building](#isession::createstmt-isession::expr) methods etc.) that overlap with the functionality 
exposed via pathSQL and protocol-buffers. As a rule of thumb, all these elements
should be avoided unless necessary (being in C++, and being inseparable 
from the kernel itself, they'd make the client code inseparable from the kernel,
which is undesirable for normal database client code).
Even an embedding process such as the [server](./terminology.md#server) only uses a tiny fraction 
of the C++ interface (all in storecmd.cpp).
A justification for using more of the C++ interface could be, for example,
to implement additional query languages for ChaosDB.

Without documenting each and every function (or parameter) of the C++ interface, this page 
presents enough information to use it successfully. The following interfaces and structures are covered:
[ISession](#isession), [IPIN](#ipin), [Value](#value), [IExprTree](#iexprtree),
[IStmt](#istmt), [ICursor](#icursor), [INav](#inav), [IStream](#istream).
Please refer to the SDK, samples and source code for a complement of information.

#rc.h
[rc.h](./sources/rc_h.html) defines (and documents summarily) the basic
error codes returned by most of the functions and methods of the C++ interface.
In some cases, these error codes may be accompanied with more explicit messages
sent to stderr or syslog. `RC_OK` is the success code used throughout the interface.

#startup.h
[startup.h](./sources/startup_h.html) defines the initial entry point to ChaosDB.
It provides functions to create, open and shutdown one or more instances of databases.
`openStore` and `createStore` produce an opaque `ChaosDBCtx` token, 
used to initiate [sessions](#isession).

The `StoreCreationParameters` structure implies a few important decisions
(note: some of the immutable fields can be modified via a complete dump & load of the database):

1. `pageSize`: the ideal [page](./terminology.md#page) size can be influenced by
   operating-system and hardware characteristics, performance requirements, and possibly
   special dataset characteristics. This configuration is immutable, and irreversible.
2. `identity`: the owner [identity](./terminology.md#identity) of this database. 
   Although it can be changed via `ISession::changeStoreIdentity`, ChaosDB provides 
   no mechanism to propagate this change to other databases that may have stored [references](./terminology.md#pin-reference) 
   and may assume that the name didn't change.  
3. `storeId`: this is essentially a replica ID. Until replication is officially released,
   it is recommended to use the default value 0. This is immutable.  
4. `password`: the password protects access to the data. It can be changed via
   `ISession::changePassword` (both for `STORE_OWNER` and guest
   [identities](./terminology.md#identity)). When encryption is enabled,
   ChaosDB provides no mechanism to recover a forgotten password.  
5. `fEncrypted`: to enable [encryption](./terminology.md#encryption). This is immutable.  
6. `maxSize`: to restrict the database file size to a quota (in bytes). This is immutable.  
7. `pctFree`: to control the percentage of free space left on pages during insertion. This is immutable.  

The `StartupParameters` is self-explanatory and won't be documented in detail in this release. A few notes:

1. `nBuffers` determines the amount of memory reserved by ChaosDB for its page buffer.  
2. `network`, `notification` and `io` are not fully supported in this release.  
3. `mode` is related with all the STARTUP_* constants defined in startup.h.  

The kernel shares a single page buffer across all open database instances and sessions. The maximum value of all
`StartupParameters::nBuffers` open so far is used as the amount of buffers. In a multi-store environment all stores 
must have exactly the same page size (`StoreCreationParameters::pageSize`).

#ISession
The session represents a logical connection to an already opened database instance (please
refer to [startup.h](#startup-h)). A session must be attached to a thread determined by the client. 
A new session attaches itself to the calling thread by default.
The client can use `detachFromCurrentThread` and `attachToCurrentThread` to unmap 
and remap sessions to threads (e.g. to use a pool of physical connections).

ISession gives access to [pathSQL](#isession::execute-isession::createstmt-pathsql) and
[protocol-buffers](#isession::createinputstream-protocol-buffers). These interfaces
are self-sufficient (all major interactions can go through them exclusively).

ISession also opens a more direct door to all major functions of the database: [PIN](./terminology.md#pin) creation, retrieval, update and deletion.
It allows to declare [properties](./terminology.md#property) and create [IStmt](#istmt) objects, which are used both to query and to 
define [classes](./terminology.md#class). It exposes the transaction control methods. It also provides other per-session controls, 
as well as some controls global to a database instance.

###ISession::execute, ISession::createStmt [pathSQL]
These methods let you execute [pathSQL](./terminology.md#pathsql) statements (more precisely,
the overloads of these methods that accept a query as string). The `execute` method
produces json output. The `createStmt` method lets you choose between raw PINs and protocol-buffer outputs
(via the resulting [IStmt](#istmt)). _The rest of the documentation on this page is mostly unnecessary, when
using pathSQL._

###ISession::createInputStream [protocol-buffers]
This is the synchronous way of executing [protocol-buffers](./terminology.md#protocol-buffer) streams.
There is also a more optimized, asynchronous way, through startup.h's `createServerInputStream`.
_The rest of the documentation on this page is mostly unnecessary, when using protocol-buffers._

###ISession::mapURIs
This is how new [properties](./terminology.md#property) are declared. Note that the pathSQL and protocol-buffer
interfaces do this implicitly, so one should only need to call `mapURIs` when going through
the lower-level methods ([createPIN etc.](#isession::createpin-isession::createuncommittedpin)).
`mapURIs` is one of the only places in the interface where the textual form
of property names (URIs) is used. In most other places, it's the numeric IDs resulting from `mapURIs` that
represent properties. This design is driven by obvious efficiency motivations. When calling `mapURIs`,
the `URIMap::uid` field is typically initialized by the caller to `STORE_INVALID_PROPID`,
and then the resulting value is stored by the caller (e.g. in some evaluation context variable) upon confirmation of success (`RC_OK`).
Property IDs are identical across all sessions of a store, but not necessarily identical across different stores.
A property ID is meaningless outside of the scope of a specific database instance, and should never be serialized alone
(without its textual counterpart). `ISession::getURI` retrieves the name bound to a property ID.
`ISession::setURIAlias` is considered incomplete in the current release.

###ISession::createPIN, ISession::createUncommittedPIN
This is how new [PINs](./terminology.md#pin) are created. `createPIN` creates the new PIN directly in the database, whereas
`createUncommittedPIN` creates [uncommitted PINs](./terminology.md#uncommitted-pin), which don't exist in the database
until `ISession::commitPINs` is called. In either case, the typical flow is to create [Value](#value)-s
and pass them to these methods. As soon as the PINs become real in the database, ChaosDB assigns a [PID](./terminology.md#pin-id-pid)
to each of them. PINs can be easily retrieved by their PID, using `ISession::getPIN`.

When passing data into the store, the store almost always copies the data, and hence the caller retains ownership 
of the original data. For example when calling `createPIN` it is perfectly valid to pass in an array of `Value`-s
that have been declared on the stack. One exception is `createUncommittedPIN`, where the store takes ownership 
of the values passed. With this method, one must either use `ISession::alloc` to allocate the `Value`-s, or
use `mode=MODE_COPY_VALUES` to avoid this behavior and force a copy.

One optimizing effect of `createUncommittedPIN` is to reduce disk io related with transaction logging
(especially when creating a lot of PINs at once). From that perspective, it is somewhat equivalent to calling
`createPIN` repeatedly inside a transaction.

The `AllocCtrl` parameter is optional. It provides some degree of control over the [page](./terminology.md#page) layout
of newly inserted PINs. For example, this can be very useful for multi-pass PIN creation processes (where multiple software components
add layers of information to an existing PIN), to reserve space for upcoming related inserts, thus preserving
better data locality. This includes a user-defined, per-PIN-insert threshold for [SSVs](./terminology.md#ssv).

###ISession::createStmt, ISession::expr
There are various flavors of `createStmt` (one of which was already covered earlier in this page,
for [pathSQL](#isession::execute-isession::createstmt-pathsql)). The simplest flavor requires no explicit argument,
and creates an empty statement. It is used in combination with `expr`, which allows to build an expression
tree piece by piece, and finally add the root of that tree to the empty statement. This can also be used in combination
with built-in conditions (see [IStmt](#istmt) for details). Statements can be executed directly (using one of the
`IStmt::exec*` methods), can be stored as properties of PINs (`ValueType::VT_STMT`), and
can define classes.

####Defining Classes
The low-level mechanism to define a [class](./terminology.md#class) or [family](./terminology.md#family)
is to [create a PIN](#isession::createpin-isession::createuncommittedpin) with
properties `PROP_SPEC_URI` (the name of the class) and 
`PROP_SPEC_PREDICATE` (a [IStmt](#istmt) object defining the predicate of the class).
Class definitions are considered immutable, because once a class definition is published,
it can be reused by any other application - it is not desirable to "pull the rug" under
other applications' feet. To upgrade a published definition, a new class must be
declared. There exists a `ISession::setURIALias` method that lets an application
use a logical name in place of the actual class name, to minimize code changes in case of
class definition upgrades. This is considered a temporary solution (a better design
will be published in a future release).

Here's an example building a multi-segment class index:

<pre>
  IExprTree * lExpr1 = NULL, * lExpr2 = NULL;
  Value lV[2];
  lV[0].setVarRef(0, 1, &mProps[0]);
  lV[1].setParam(0);
  lExpr1 = mSession->expr(OP_LT, 2, lV);  
  lV[0].setVarRef(0, 1, &mProps[1]);
  lV[1].setParam(1);
  lExpr2 = mSession->expr(OP_GT, 2, lV);

  IStmt * const lQ = mSession->createStmt();
  QVarID const lVar = lQ->addVariable();
  lQ->addCondition(lVar, lExpr1);
  lQ->addCondition(lVar, lExpr2);

  lExpr1->destroy();
  lExpr2->destroy();

  RC rc = RC_OK;
  lV[0].set(className); lV[0].setPropID(PROP_SPEC_URI);
  lV[1].set(lQ); lV[1].setPropID(PROP_SPEC_PREDICATE);
  IPIN * lClass = mSession->createUncommittedPIN(lV, 2, MODE_COPY_VALUES);
  rc = mSession->commitPINs(&lClass, 1);
  if (rc==RC_OK || rc==RC_ALREADYEXISTS)
  {
    ClassID lCLSID = lClass->getValue(PROP_SPEC_CLASSID)->uid;
    lClass->destroy();
    ...
  }
</pre>

###ISession::startTransaction
Transactions are bound to sessions. For a good discussion on all available options,
including isolation modes and read-only transactions,
please refer to [pathSQL's description](./pathSQL reference.md#transactions).
Note that operations (such as `ISession::createPIN` or `IPIN::modify`)
can be invoked outside of the explicit scope of a transaction,
in which case they implicitly declare their own transaction internally.

#IPIN
`IPIN` represents the in-memory snapshot of a [PIN](./terminology.md#pin).
An instance of IPIN is always bound to the `ISession` that created it,
and should only be used (and destroyed) in that session. All reading from and
writing to the database is done explicitly only (e.g. via IPIN's `refresh` and
`modify` methods).

One of the most frequent interactions with `IPIN` is to traverse or retrieve
its [values](./terminology.md#value), using `getValue, getValueByIndex and
getNumberOfProperties`. Note that `ISession::getPIN`
must load all properties of the PIN, whereas `ISession::getValue*`
allows to retrieve only individual properties.

The other major interaction is to `modify` the PIN. Similar to 
[PIN creation](#isession::createpin-isession::createuncommittedpin),
it involves filling in [Value](#value) structures and passing them to `modify`.
Alternatively, one can use `ISession::modifyPIN` to avoid
loading the IPIN object.

The same `IPIN` is used to represent pure in-memory objects ([uncommitted PINs](./terminology.md#uncommitted-pin))
and objects in the database. The main difference is that instances of the former don't have a [PID](./terminology.md#pin-id-pid).

The PIN's stamp allows to determine if a PIN has changed since the stamp was last grabbed.
To obtain the most recent stamp, it is still necessary to load (or `refresh`) the PIN from the database,
so this is not a panacea for reducing disk io, but it can be useful.

#Value
The `Value` structure defined in [chaosdb.h](./sources/chaosdb_h.html) can represent any of the
[data types](./pathSQL reference.md#data-types) supported by ChaosDB. `Value` is used both as
an input value (to create or modify PINs) and as an output value (to read the contents of PINs).

###As Input (modify)
In this context, an instance of `Value` is considered initialized if and only if one of its `set` methods is invoked.

The fields `length`, `type` and the related member of the union are initialized by the
chosen `set` method. The `flags` field is for internal use only and should
not be interpreted or modified.

The `property` field determines the [property](./terminology.md#property) to which this value
belongs. It can be one of the `PROP\_SPEC\_*` values (documented in detail in [chaosdb.proto](./sources/chaosdb_proto.html)).
Or it can be a property ID obtained via [mapURIs](#isession::mapuris), described earlier.

The `op` field defines how the value is intended to be used. For a relatively thorough
description of possibilities, please refer to line 198 in [chaosdb.proto](./sources/chaosdb_proto.html).

The `eid` field is used depending on the context. For new elements of a [collection](./terminology.md#collection),
it defines their logical position (either by using `STORE_LAST_ELEMENT, STORE_FIRST_ELEMENT etc.`,
or by specifying the eid of an already existing element [see the comments about `OP_ADD` and `OP_ADD_BEFORE` in 
[chaosdb.proto](./sources/chaosdb_proto.html)]). For existing elements, `eid` can be used in conjunction with
`OP_MOVE` and `OP_MOVE_BEFORE`. For all other `op`, the `eid`
simply designates the element being modified.

The `meta` field allows fine-grained (per-property) control of things such as indexing,
[SSV](./terminology.md#ssv) etc. The `META\_PROP\_*` flags are documented in
[chaosdb.h](./sources/chaosdb_h.html).

###As Output (read)
Most of the fields have the same meaning as in the input case. However, `op` and `meta`
are unused in this case. Also, `length` can be uninteresting when large objects are returned ([INav](#inav)
or [IStream](#istream)). This is done to delay expensive length computations until requested. 

#IExprTree
`IExprTree` represents a node of an expression tree. Every instance is created with
`ISession::expr` (or `ISession::createExprTree`). The `op`
parameter determines the logical relation between the `operands` (which are instances of
[Value](#value)).

Via `VT_EXPRTREE`, a [Value](#value) can hold an `IExprTree`, and thus `ISession::expr`
can be used not only to build leaf nodes but also complete trees (in combination with logical
operators such as `OP_AND, OP_OR etc.`). Here's an example:

<pre>
  CmvautoPtr<IStmt> lQ(mSession->createStmt());  
  unsigned const char lVar = lQ->addVariable();  
  Value lV[2];  
  lV[0].setVarRef(0, 1, &mFilePathPropID);  
  lV[1].setParam(0);  
  IExprTree *lET1 = mSession->expr(OP_EQ, 2, lV);  
  lV[0].setVarRef(0, 1, &mPIFSAttrPropID);  
  IExprTree *lET2 = mSession->expr(OP_EXISTS, 1, lV);  
  lV[0].set(lET1);  
  lV[1].set(lET2);  
  CmvautoPtr<IExprTree> lET(mSession->expr(OP_LAND, 2, lV));  
  TVERIFYRC(lQ->addCondition(lVar,lET));  
</pre>

Usually, the root node of an expression is passed to `IStmt::addCondition`. Internally,
ChaosDB compiles the expression into a representation optimized for execution (`IExpr`).
The methods of `IExprTree` are rarely used.

_Note: When freeing an expression tree composed of multiple sub-trees, `destroy` should only be
called on the topmost `IExprTree` object. In the example pasted here, notice how only `lET` is
destroyed explicitly (not `lET1` nor `lET2`)._

#IStmt
`IStmt` brings together all the pieces involved in querying the database:
query conditions, [classes](#defining-classes) and [indexes](./terminology.md#index), joins,
ordering, projections and PIN transformations, query plan analysis etc.

To use an existing class as a condition of a query:

<pre>
  ClassSpec lCS1;  
  lCS1.classID = lTheCLSID1;  
  lCS1.nParams = 0; lCS1.params = NULL;  
  lQ->addVariable(&lCS1, 1);  
</pre>

To merge two classes:

<pre>
  ClassSpec lCS1, lCS2;  
  lCS1.classID = lTheCLSID1;  
  lCS2.classID = lTheCLSID2;  
  lCS1.nParams = 0; lCS1.params = NULL;  
  lCS2.nParams = 0; lCS2.params = NULL;  
  unsigned char lVars[2];  
  lVars[0] = lQ->addVariable(&lCS1, 1);  
  lVars[1] = lQ->addVariable(&lCS2, 1);  
  lQ->setOp(lVars, 2, QRY_INTERSECT);
</pre>

To do a join:

<pre>
  // same thing as merge, except replace setOp with:
  lQ->join(lVars[0], lVars[1], NULL, QRY_JOIN);
</pre>

To use a family instead:

<pre>
  Value lVParam;
  lVParam.set(...); lVParam.setPropID(...);
  ClassSpec lCS1;
  lCS1.classID = lTheFamilyID1;
  lCS1.params = &lVParam;
  lCS1.nParams = 1;
  lQ->addVariable(&lCS1, 1);
</pre>

To use a full-text condition with ordered results:

<pre>
  TVERIFYRC(lQ->addConditionFT(lQ->addVariable(), "whatever", 0, &mProps[0], 1));
  OrderSeg const lOrder = {NULL, mProps[0], ORD_NCASE};
  TVERIFYRC(lQ->setOrder(&lOrder, 1));
</pre>

_Note: In the present release, output transformations are not yet considered ready._

#ICursor
`ICursor` is the result of some of the `IStmt::exec*` methods,
and allows to walk a query result, in one of three possible ways:

1. by IPIN*: every next pin is loaded and returned
2. by PID: only the PID of every next PIN is returned
3. by IPIN**: for joins, to obtain all pins involved in the join (one result at a time, same as 1 and 2)

By default, `ICursor` is bound to (and should not outlive [i.e. be destroyed after])
the `IStmt` that generated it. This restriction can be removed with `MODE_COPY_VALUES`, 
at the risk of paying a performance penalty.

`ICursor` may fail to return results if the transaction in which it runs is closed
prematurely.

#INav
Large [collections](./terminology.md#collection) are represented with `INav`.
In that case, the `Value::length` becomes 1 and the actual collection length is obtained
procedurally (and on demand only), via `INav::count` (keep in mind that a B-tree implementation takes over when a collection
becomes large; this also implies that seeks and certain queries are fast).

Because the point at which a small collection becomes large (and vice versa) is not controlled
explicitly by the client, it is recommended to always use code that handles both cases, such as
the `CollectionIterator` defined at line 249 in serialization.h.

#IStream
This interface is used both to push [BLOBs](./terminology.md#blob) into the store (by implementing
a client IStream-derived class), and to read BLOBs from the store. Via `IStream::dataType`,
BLOBs can be marked as text-only (ascii or unicode), or binary. Note that BLOBs, like strings, can
be modified via `OP_EDIT`, described in detail in [chaosdb.proto's StrEdit](./sources/chaosdb_proto.html)
(but in the current state of the implementation, this is not fully optimized for blobs). 
Note also that text BLOBs can participate to full-text indexes, just like any text property. 
It is possible to build [collections](./terminology.md#collection) of BLOBs.
