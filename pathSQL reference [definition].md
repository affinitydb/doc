### DDL
Here's a description of pathSQL's Data Definition Language.
Note that for every CREATE statement, there exists an equivalent INSERT statement;
every such statement results in a PIN containing some properties with special meaning,
along with ordinary properties.

#### CREATE CLASS
Synopsis:  

  - CREATE CLASS class_name [OPTIONS( {VIEW|CLUSTERED|SOFT_DELETE} )] AS query_statement
    [SET afy:onEnter={\${qs1}, \${qs2} [, ...]}, afy:onUpdate={\${qs3}, \${qs4} [, ...]}, afy:onLeave={\${qs5}, \${qs6} [, ...]}, property=value [, ...]]  

Equivalent to:  

  - INSERT afy:objectID=.class_name, afy:predicate=\${query_statement},
    afy:onEnter={\${qs1}, \${qs2} [, ...]}, afy:onUpdate={\${qs3}, \${qs4} [, ...]}, afy:onLeave={\${qs5}, \${qs6} [, ...]}, property=value [, ...]  

Where the query_statement is a [SELECT QUERY](./pathSQL reference [manipulation].md#query). Here's a description of the OPTIONS:  

  - DEFAULT: This is the default mode (all [PIDs](./terminology.md#pin-id-pid) will be indexed by this class).  
  - VIEW: Like view in relational db, it is just a query definition for usability.  
  - CLUSTERED: Using clustered index to maintain all [PIDs](./terminology.md#pin-id-pid), for increased performance. Not yet implemented.  
  - SOFT_DELETE: Create an index not only for normal pins, but also for those pins marked as deleted (but not purged).  
  - *Note:* These OPTIONS cannot be specified via the INSERT equivalent form, presently.  

The `afy:onEnter`, `afy:onUpdate` and `afy:onLeave` properties allow to attach actions to classes (similar to "callbacks",
"event handlers", and "triggers" in RDBMSs).  The implementation of those actions is expressed in pathSQL,
either as a single statement (e.g. `SET afy:onEnter=${INSERT originator=@self}`) or as a collection of statements
(e.g. {`${UPDATE @auto SET fheight=(SELECT AVG(height) FROM @self.friends)}`, `${UPDATE @self SET bigfriends=true WHERE @auto.fheight>=6ft}`}).
Whenever a PIN starts to conform with the class predicate, `afy:onEnter` of that class will be invoked, with `@self` pointing to that PIN
(and `@ctx` pointing to the class; the kernel also provides a special transient PIN accessible via `@auto`,
allowing to store local variables for more intricate inner processing). A PIN that is `UPDATE`-d while it is already classified
will produce `afy:onUpdate`, unless this `UPDATE` actually removes this PIN from the class, in which case `afy:onLeave` will be called.
All those actions are optional. The query statements that constitute them (qs1, qs2, qs3 etc.) can be any combinations of
`UPDATE` and `INSERT` statements. Event processing can be reentrant.

<!-- TODO: revisit when final model of sync-transact-async is there -->
<!-- TODO: more on exact execution model, sequence etc. -->
<!-- TODO: something about ${PERSIST} (or upcoming equivalent) -->

Examples: [class.sql](./sources/pathsql/class.html).   

The "IS A" operator can be used to check whether or not a pin belongs to a class. For example, those two statements are equivalent:  
 
        SELECT * WHERE afy:pinID IS A class1;  
        SELECT * FROM class1;  

#### Creating a [class family](./terminology.md#family)  

        CREATE CLASS clsfml11 AS select * where prop1 = :0 and prop2 = :1;    
        select * from clsfml11(*, 2);    

Here * indicates all values, including NULL. In this case, the [index](./terminology.md#index) is created with the composite key(prop1 and prop2)  

**Limitation 1**: The kernel uses a BTree to store indexes, and can't store a PIN whose properties are all NULL. 
NULL can be passed as a parameter to a class family only when the index for this class family is a multi-segment index.
Single-property indexex cannot support NULL parameters.
For performance reasons, it is recommended not to create a class family with only one parameter passed to the where clause, such as: `WHERE :0 is NULL`.

**Limitation 2**: There's a sytactic restriction on the order of parameters in class predicates. For example, Affinity cannot create an index for `:0 = value`,
but `value = :0` is fine.

*Note*: Affinity can ignore superfluous parameters, i.e. the user can pass more parameters than used in the predicate.

Please refer to the [class](./terminology.md#class), [family](./terminology.md#family) and [indexing](./terminology.md#index) descriptions for
a brief comparison with the relational DDL. Note that it is possible to declare multiple families with the same predicate, and different
type specifications:

        CREATE CLASS clsfml21 AS select * where prop1 = :0(int);  
        CREATE CLASS clsfml22 AS select * where prop1 = :0(String); 

In this case, if a PIN's prop1 is a string which cannot be converted into a number, then it won't be part of clsfml21.

If the parameter type is not specified, then the class family index is created with a typeless index, preserving
the original type of data items, and performing implicit coercions at evaluation time.  

All class options work for class families as well, except SOFT_DELETE. 

##### Indexing Of Collections 
For single-property indexes, all elements will be added to the index.  
For multi-segment indexes, all combinations will be added to the index (Cartesian product of all values of the indexed properties).  

##### How To Specify Key Value Order For Index
The available options are:  

  - ASC:  Sort keys in ascending order.  
  - DESC: Sort keys in descending order.  
  - NULLS FIRST: Order the null values (e.g. absent property) before any non-null value.  
  - NULLS LAST: Order the null values after any non-null value.  

Example:  

        CREATE CLASS clsfml5 AS select * where prop1 = :0(int, desc, nulls first)and prop2=:1(int);  

#### RULE
[Rules](./terminology.md#rule) form a higher-level programming layer, intended to help summarize and present a system's
key logical decision points to non-programmer professionals (for example), and to let them
customize and control some finer aspects. The programmer defines conditions, actions,
internal implementations (e.g. [FSMs](./terminology.md#fsm)) etc., and then expresses
rules, using those lower-level building blocks. The non-programmer can review and modify
those rules, without getting involved in their implementation.

Synopsis:

  - RULE rule_name : condition1(parameters) AND condition2(parameters) [AND ...] -> action1(parameters), action2(parameters) [, ...]  

Where conditionN and actionN refer to the name (`afy:objectID`) of corresponding PINs defining those conditions and actions.  

A condition is defined by a PIN with `afy:objectID` and `afy:condition`, e.g.  

      INSERT afy:objectID=.condition1, afy:condition=$(SIN(:0) > :1)  

An action is defined by a PIN with `afy:objectID` and `afy:action`, e.g.  

      INSERT afy:objectID=.action, afy:action={${INSERT x=@ctx.xL}, {UPDATE @self SET t=CURRENT_TIMESTAMP}}  

Please refer to this [example](./pathSQL basics [control].md#rules) for more information.

<!-- TODO: explain in more detail, give examples -->

#### CREATE ENUMERATION
Synopsis:  

  - CREATE ENUMERATION enum_name AS {'symbol1', 'symbol2', 'symbol3' [, ...]}  

Note that this is equivalent to:  

  - INSERT afy:objectID=.enum_name, afy:enum={'symbol1', 'symbol2', 'symbol3' [, ...]}  
 
These symbols can then be used as special unique values in queries, such as  

  - INSERT v1=enum_name#symbol1  
  - SELECT * WHERE v1=enum_name#symbol1  

Examples: [enum.sql](./sources/pathsql/enum.html).   

#### CREATE TIMER
Synopsis:  

  - CREATE TIMER timer_name INTERVAL '00:00:05' AS query_statement [SET property=expression [, ...]]  

This is equivalent to:  

  - INSERT afy:objectID=.timer_name, afy:timerInterval=INTERVAL'00:00:05', afy:action=\${query_statement} [, property=expression [, ...]]  

Timers run as active loops (or threads), executing the specified query_statement at the specified interval.  
Timer PINs can contain properties that link them to other sub-systems.  

Examples: [timer.sql](./sources/pathsql/timer.html).   

#### CREATE LOADER
Synopsis:  

  - CREATE LOADER myservice AS 'platform_independent_path'  

Equivalent to:  

  - INSERT afy:objectID=.srv:webapp, afy:load='platform_independent_path';  

This statement allows to extend the set of available services, with additional external libraries.
The platform_independent_path points to a .dll / .so / .dylib module that publishes components that conform
with the Afy::IService interface.

#### CREATE LISTENER
Synopsis:  

  - CREATE LISTENER mylistener ON '127.0.0.1:4567' AS {.srv:sockets, .srv:pathSQL, .srv:affinity, .srv:protobuf, .srv:sockets} [SET property=expression [, ...]]  

Equivalent to:  

  - INSERT afy:objectID=.mylistener, afy:address='127.0.0.1:4567', afy:listen={.srv:sockets, .srv:pathSQL, .srv:affinity, .srv:protobuf, .srv:sockets} [, property=expression [, ...]]  

This statement creates a socket listener on host '127.0.0.1', port 4567.  The service stack defined in afy:listen
could be any meaningful combination of services, as described more in detail in the next section.
Each entry of this collection can be a simple service type (like in the example above), or a reference to communication PIN, or
a VT_STRUCT describing a communication channel.  Each service (or communication channel) can be configured independently,
but for brevity it's also possible to do simple configurations via the master PIN (e.g. here, the afy:address configures
the socket of this listener).

#### Communication PINs
<!-- TODO: review in detail, make sure nothing is obsolete etc. -->
<!-- TODO: document in detail the configuration parameters of each service -->

Communication with external world (reading data from sensors, sending commands to actuators,
sending and receiving network requests, exchanging information with other instances of Affinity, etc.)
is done by reading or writing to special communication PINs.  

A PIN is a "special communication PIN" (aka CPIN) if it contains property `PROP_SPEC_SERVICE` (`afy:service`) or `PROP_SPEC_LISTEN` (`afy:listen`).

When a CPIN is encountered in a SELECT statement stream, Affinity reads information from the source described by the CPIN.
When an UPDATE is applied to CPIN, the Affinity kernel performs a write operation.

Writing to a CPIN inserted with OPTIONS(TRANSIENT) will result in a write operation to the CPIN destination before the CPIN is discarded.
The transient UPDATE operation applies modifications specified in UPDATE to an in-memory copy of the CPIN (the persisted CPIN is not modified)
and then uses the resulting CPIN for communication (see below).

The value of afy:service or `afy:listen` property can be:

  - a VT_URIID: a service with this URIID is invoked; other properties of CPIN serve as parameters (e.g. `afy:service=.srv:XML`)

  - a VT_STRUCT: the struct must contain an `afy:service` field (afy:listen for a listener CPIN); other fields serve as additional parameters of the service invocation (e.g. afy:service={afy:service=.srv:IO, afy:address='c:\\affinity\\tests\\testfile.txt'})

  - a VT_REFID: the referred PIN must be a CPIN, properties of which are used for the operation

  - a VT_ARRAY: contains more than one element with the above types; defines a communication stack (e.g. `afy:service={.srv:XML, srv:IO}`)

A communication stack is a linear sequence of services which are called sequentially to perform i/o
and transformations of the data, where output of one service is passed as the input to the next one in the stack.

Services in a stack can be of 3 types: endpoints, servers and transformations. Endpoints perform actual i/o.
Servers reverse the flow of communication (they expect a request as their input, and they produce a response as their output).
Transformations transform data to the desired format, e.g. performing parsing (pathSQL, JSON, XML, protobuf, etc.) or rendering.

There 4 types of stacks.

  1. Read stack:

      <read endpoint> -> <transform1> -> ... -> <transformN> -> kernel (SELECT or read())

  2. Write stack:

      kernel -> <transform1> -> ... -> <transformN> -> <write endpoint>

  3. Request stack:

      kernel -> <transform1> -> ... -> <transformN> -> <request (read/write) endpoint> -> <transformN+1> -> ... -> <transformM> -> kernel

  4. Server stack:

      <listener endpoint> -> <transform1> -> ... -> <transformN> -> kernel -> <transformN+1> -> ... -> <transformM> -> <write endpoint, usually associated with the originating listener endpoint>

Related transformations (e.g. protobuf encoding and decoding) have the same service name and ID and are distinguished
by the type of stack they're used in and their position. Therefore, the same protobuf service can be invoked for read and for write.
In the first case it should decode protobuf stream, and in the second, encode structured information into protobuf stream.
Some services (e.g. RegExp service) can be used only in the read part of stack, others - only in the write.

The kernel determines the type of stack automatically, based on type of the operation, services specified in the stack by CPIN
and valid uses of specific services (is it endpoint? can it be used for read? for write? for request? can it listen? etc.)

The result of CPIN communication in `SELECT` is a PIN or a stream of PINs returned by the services used in the communication stack.
If the last service in stack returns `VT_REF` (reference to a newly created uncommitted PIN) - that's what `SELECT` would return
(or use for further transformation). If it's a `VT_STRUCT` - a PIN with corresponding properties is created 'on-the-fly' and 
passed to the `SELECT` statement for further processing. In all other cases a PIN with a single property afy:value is returned.

`UPDATE` doesn't return anything. It's used to send data (or commands) to the external recipient.

Services in a stack are called in the order they are specified in the array. There is one exception to this rule: a CPIN
describing a read stack can be used for a write operation. In this case the sequence of service calls is automatically reversed.

An example:

  - Here is a read stack:

         afy:service={srv:sockets, srv:HTTP, srv:protobuf}

  - A normal write stack would be:

         afy:service={srv:protobuf, srv:HTTP, srv:sockets}.

Still, in order to prevent CPIN duplication, it's possible to use the first CPIN for a write operation.

A list of built-in services:

  - srv:affinity      - process pathSQL requests; server  
  - srv:regex         - parse input using a regular expression; transform  
  - srv:pathSQL       - parse/render pathSQL; transform  
  - srv:JSON          - render JSON; transform  
  - srv:protobuf      - parse/render protobuf; transform  
  - srv:sockets       - read/write/listen sockets; endpoint  
  - srv:IO            - read/write using OS i/o; endpoint  

External services:

  - srv:serial        - read/write (RS232); endpoint  
  - srv:HTTP          - HTTP server; server  
  - srv:HTTPRequest   - HTTP request; transform  
  - srv:HTTPResponse  - HTTP response; transform  
  - srv:REST          - REST interface to the server (for direct JSON/protobuf access to the store); transform  
  - srv:webapp        - static content server; server  
  - srv:XML           - XML<->PIN parser/renderer; transform  
  - srv:NFC           - NFC listener, reader and writer

Future services:

  - srv:SSL  
  - srv:JSON (parsing)  
  - srv:RDF  
  - etc.  

The `.srv:affinity` service typically accepts 2 types of inputs: `.srv:pathSQL`, and `.srv:protobuf` (n.b. a protobuf
payload will often be a plain set of PINs, but it could also contain pathSQL statements [although that aspect of the implementation
is incomplete at the moment]; in that sense `.srv:protobuf` could be considered more general than `.srv:pathSQL`).
In cases where a response is not expected from the `.srv:affinity` service,
a truncated stack should be used: `{.srv:sockets, .srv:protobuf, .srv:affinity}` would suffice for an insert (or message passing),
whereas `{.srv:sockets, .srv:pathSQL, .srv:affinity, .srv:XML, .srv:sockets}` would be typical for a query.

Listeners that don't contain a server in their service stack can define a terminal `afy:action` to
process the resulting PINs at the tail of the stack.

Note that most services are incomplete in the alpha release. Also, service-specific configuration is
not yet systematically documented. To properly assess the state and functionality of each service, we advise that
you review the corresponding source code at this stage, until more explicit documentation is provided in
a next update.
