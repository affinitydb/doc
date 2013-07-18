#Release Notes
AffinityNG is a major evolution of its ancestor (AffinityDB), having the graph database grow into
a universal embedded information-processing, control and communication platform.  In the process,
in addition to all the new functionality added, some syntactic and semantic changes were made.
Most of these changes would be invisible from an ordinary application (for example, the whole online
tutorial of AffinityDB is still valid in AffinityNG, unchanged). We'll enumerate those changes briefly here.

##Changes

 * The default store file name in AffinityNG is `affinity.store` (as opposed to `affinity.db`).
   Note that AffinityNG is not binary-compatible with AffinityDB, and thus won't read `affinity.db` files.
   We are considering to provide an upgrade path from AffinityDB to AffinityNG.  Should you be in that situation,
   please let us know, either via an issue in github or a message in our discussion forum.
<!-- TODO: enable when it's there (e.g. beta, or maybe before)
 * The functionality of the `server` process evolved into a service of the kernel, and the process itself moved to
   the `daemons` project. The REST interface exposed by AffinityDB's server has not changed and remains fully supported
   in AffinityNG.  
-->
 * `createServerInputStream` and `IConnection`: These elements of the single-threaded server interface were removed
   (asynchronous request handling migrated to the new communication stack).
 * Several minor and major security improvements were made, including an upgrade to AES256, SHA256 etc.
 * The URI prefix for built-in properties and other primitives in AffinityNG is
   `http://affinityng.org/builtin/` (as opposed to `http://affinitydb.org/builtin/` in AffinityDB).
 * The SPARQL-style comment (`# comment`) is no longer supported in pathSQL.
 * `PREFIX`, `SET BASE` and `SET PREFIX`: The per-statement `PREFIX` was removed, and
   `SET PREFIX` and `SET BASE` now operate like a compiler directive (analogous to #define in C)
   rather than a statement, and can be prepended to any statement or group of statements (separated with a semicolon).
   Their scope is one interaction with AffinityNG (i.e. one REST request, one `q` call from a
   client library, or one `IStmt::execute` or `ISession::execute` call in C++). These changes
   participate in an effort to reduce per-session state to an absolute minimum.
 * `SELECT @ FROM ...`: This form no longer selects a PIN's ID, but rather has the same effect as `SELECT * FROM ...`;
   to select the PIN's ID, one must now do `SELECT afy:pinID FROM ...`.  Note also that `SELECT afy:pinID`
   no longer produces a reference in the JSON output (`['afy:pinID']['$ref']`), but rather a simple `id`.
 * `afy:ClassOfClasses`: This special class was renamed to `afy:Classes`.
 * `afy:classID`: This special property (aka `PROP_SPEC_CLASSID`) was replaced by the more general `afy:objectID`.
 * `afy:URI`: This special property (aka `PROP_SPEC_URI`) was replaced by the more general `afy:objectID`.
 * `UPDATE ... FROM x`: This form is no longer supported; it was replaced with `UPDATE x ...`.
 * Full text indexing is no longer enabled by default; to reflect this, the `META_PROP_NOFTINDEX` flag
   was replaced by its opposite, `META_PROP_FTINDEX`.
   <!-- TODO: augment this when it also becomes true of class indexing... -->
 * `PIN_NO_INDEX` no longer exists; PINs to be hidden from normal queries can be marked as `PIN_HIDDEN`,
   but they may still be indexed.
 * `OP_REGEX` no longer exists and was replaced by `OP_SIMILAR`, which now fully implements regular expressions,
   with conditions of this form: `SELECT WHERE myproperty SIMILAR TO /.*something$/`.
<!-- TODO: activate when fully implemented
 * Notifications have been formalized in such way that they are now sent only upon fully committed (i.e. topmost)
   transactions, as opposed to leaking information during ongoing transactions. For the same reason,
   the C++ method `IStoreNotification::txNotify` was removed.
-->
 * In the C++ interface, `openStore` and `createStore` no longer return an opaque context pointer,
   but rather a pointer to a new interface named `IAffinity`.  The `shutdownStore` function became
   `IAffinity::shutdown`, and a few new global methods were introduced for new functionality
   (e.g. service registration).
 * In the C++ interface, `createPIN` and `createUncommittedPIN` changed names, for `createPINAndCommit`
   and `createPIN` (this is to reflect AffinityNG's preference for in-memory processing by default).
 * The PIN's update stamp is now represented by an optional built-in property (`afy:stamp` aka PROP_SPEC_STAMP),
   and is no longer accessible via the C++ `IPIN::getStamp`. The `afy:stamp` property must be added explicitly
   at PIN creation, in the same manner as `afy:updated`, `afy:created` etc.
 * In the C++ interface, `Value::setPart` is no longer available. A PIN can still be referenced as a "part"
   by setting the `META_PROP_PART` flag on that referencing property.  Alternatively, `VT_STRUCT`
   (expressed in pathSQL with `INSERT mystruct={field1='Value1', field2='Value2', ...}`) can be used
   to hold structured parts even closer to the owning PIN.
 * The output of `SELECT HISTOGRAM(property) FROM ...` changed slightly, and now contains an `afy:aggregate` property.
 * The old `ACL_READ` and `ACL_WRITE` have become standard `META_PROP_READ` and `META_PROP_WRITE`.
 * `CLASS_CLUSTERED` and `CLASS_UNIQUE` are no longer available.
 * A few other rarely or never used `META_PROP_*` and `PIN_*` flags were removed.
 * The usage of referencing (\&) and dereferencing (\*) operators in pathSQL was simplified.
<!-- TODO: review in detail the changes in path expressions, if the sum of them justifies it
 * a.{*}.b -> a.*.b (?)
-->

##Additions
<!-- TODO: make sure all these things are linked to the sections that fully document them -->

 * Event-handlers (written in pathSQL) can be attached to [classes](./terminology.md#class).  These handlers execute operations
   in response to events concerning the class they're attached to.  For example, when a PIN becomes a member of a class,
   the statements contained by an `afy:onEnter` property  will be executed.  The handlers, through the statements
   that define them, have access to special context properties
   (e.g. `@self` and `@class`), referencing the PINs involved in the event.
<!-- TODO: enable when exists
 * A higher-level packaging framework allows to organize and compose [rules](./terminology.md#rule) from a directory of
   [conditions](./terminology.md#condition) and [actions](./terminology.md#action), as commonly seen in business rule
   engines and production systems.
-->
 * A simple data and execution model is defined for [finite-state machines (FSMs)](./terminology.md#fsm),
   proposed as an intuitive programming model to work with inter-related states and events
   (at practically any level of abstraction).  FSMs provide precise scopes for the evaluation
   of events and conditions, as well as for the definition of complex events (CEP).
   <!-- TODO: finalize when ready... -->
 * [Timer](./terminology.md#timer) PINs can trigger events at regular time intervals.
 * [Communication PINs](./terminology.md#communication-pin) allow to send data to (and receive from) external entities,
   such as other stores, devices, sensors, actuators etc.  Communication PINs declare and configure the service stacks
   that correspond with the desired communication channels (e.g. socket, file, serial, zigbee, REST endpoints;
   various data transformations like URL or XML or JSON parsing). 
 * Loadable [services](./terminology.md#service) allow to augment AffinityNG with customized software components
   (for processing and messaging), that can participate in a communication PIN's service stack.
 * Built-in services use the `srv` URI prefix, defined as `http://affinityng.org/service/`.
 * A number of new options allow to `INSERT` multiple PINs in one statement:  
    - `INSERT (a,b,c) VALUES (10,11,12), (20,21,22), ('30', '31', '32')`  
    - `INSERT @{a=10, b=11, c=12}, @{a=20, b=21, c=22}, @{a='30', b='31', c='32'}`  
    - `INSERT @:1 @{a=10, b=11, c=12, refs={@:3, @:2}}, @:2 @{a=20, b=21, c=22, refs={@:1, @:3}}, @:3 @{a='30', b='31', c='32', refs={@:1, @:2}}`  
    - `INSERT @:1 mylist={(INSERT @:2 mymember=1, myparent=@:1, mysibling=@:3), (INSERT @:3 mymember=2, myparent=@:1, mysibling=@:2)}`  
 * The [`VT_STRUCT`](./terminology.md#structure) data type, introduced in AffinityDB though incomplete, is now fully operational and provides finer control for data modeling.
 * A new `VT_ENUM` data type allows to declare symbolic enumerations of inter-related values, and then use them
   instead of literal constants (for better expressiveness and control):  
    - `CREATE ENUMERATION PAINT_COLORS AS {'RED', 'GREEN', 'BLUE', 'ORANGE'}`  
    - `INSERT car_color=PAINT_COLORS#ORANGE`  
    - `UPDATE * SET repaint=PAINT_COLORS#RED WHERE car_color=PAINT_COLORS#ORANGE`  
 * A new [`VT_MAP`](./terminology.md#map) data type allows to store dictionaries (associative arrays) as properties of a PIN
   (keys are not limited to symbolic values, can be of any data type, and can be much more numerous than
   the number of properties on a PIN)
 * `SELECT MEMBERSHIP(@) FROM ...` returns all the class memberships of selected PINs in one go.
   It can be considered as a complement of the `IS A` condition (already available in AffinityDB).
 * It is now possible to perform constraint checks at insertion, with the form
   `INSERT INTO myclass myproperty1='a', myproperty2='b', ...`.  This will only insert the
   new specified PIN if it complies with the predicate of `myclass`.
 * The `CREATE` syntax now supports an additional `SET` clause, allowing to add additional
   properties beyond the standard templates for classes, timers, listeners etc.
 * The `createPIN` 
<!-- TODO: something about in-memory classes etc. (all non-persistent active stuff) -->
<!-- TODO: something about UNIQUE and IDEMPOTENT, when ready -->
<!-- TODO: aggregate, sliding window etc. -->
<!-- TODO: undo feature, when available -->
 * It's now possible to `INSERT SELECT ...`, e.g. to insert a result obtained via communication
   PINs, or to duplicate and transform existing PINs.
 * The HMAC computations on pages were made optional, due to their computational cost and
   lesser relevance in some contexts.
 * Reflecting all the new functionality, a blank AffinityNG store comes with more built-in classes
   (not only `afy:Classes`, but also `afy:Timers`, `afy:Listeners` etc.)
 * `PIN_IMMUTABLE` and `META_PROP_IMMUTABLE`: It is now possible to create PINs and properties
   that cannot be modified. This is useful for recurrent measurements (e.g. sensor readings).
   By relieving the kernel from watching changes on those values, AffinityNG can
   handle a higher volume and flow rate of incoming data.
 * It's now possible to extract the fractional part of timestamps with `EXTRACT(FRACTIONAL FROM myprop)`.
 * `GROUP BY` can now be used in combination with `SELECT HISTOGRAM`, thus providing complex data summaries
   at the tip of the programmer's fingers; e.g. `SELECT HISTOGRAM(age) FROM ... GROUP BY age/10`.
 * Trigonometric functions were added to the set of core operators (e.g. `INSERT y=SIN(3.14159265 / 4)`).
 * The pathSQL parser now accepts multiple `WHERE` clauses in `SELECT`.
 * More hardware platforms and operating systems are now supported (including older versions of ARM
   processors, android, iOS etc.)
 * XCode projects were added for OSX, as a convenient alternative for cmake projects.

##Limitations
The following limitations are part of the alpha release of AffinityNG.

 * Most of the [services](./terminology.md#service) are incomplete and not yet fully documented.
 * The security & privacy models for communications are not yet available.
 * [FSMs](./terminology.md#fsm), [communication](./terminology.md#communication-pin), and the synergy
   between them are still young and may expose bugs. Your contribution in reporting issues (via github)
   would be very appreciated.
 * Pre-built platform-specific packages are not yet polished or readily available.
 * Path expressions in pathSQL have important limitations (e.g. mostly available in FROM,
   limitations related to [structures](./terminology.md#structure) and [maps](./terminology.md#map), etc.
 * AffinityNG is moving toward a transient-first approach (as opposed to its ancestor AffinityDB,
   which favored the more traditional database approach with persistent-first objects); this evolution
   may not be completely accomplished in the alpha release.
 * JSON parsing is not yet supported.
 * Dump&load and replication not fully implemented.
 * There are limitations with projections in JOIN.
 * Support for uniqueness during insert is not yet complete.
 * The current implementation of the [server](./terminology.md#server) is phasing
   out and will soon be replaced with tiny platform-specific daemons
   using generic [services](./terminology.md#service).
