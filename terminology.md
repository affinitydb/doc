#List of Terms
[ACL](#acl), [action](#action), [BLOB](#blob),
[C++ interface](#c-kernel-interface), [CEP](#cep), [class](#class), [client-side library](#client-side-libraries),
[coercion](#coercion), [collection](#collection), [communication PIN](#communication-pin), [condition](#condition),
[data model](#essentials-data-model),
[element ID (eid)](#element-id-eid), [encryption](#encryption), [enumeration](#enumeration), [family](#family),
[FSM](#fsm), [identity](#identity), [index](#index), [kernel](#kernel),
[loader](#loader), [map](#map), [namespace](#namespace), [notification](#notification),
[page](#page), [parameter](#parameter), [pathSQL](#pathsql), [PIN](#pin),
[PIN ID (PID)](#pin-id-pid), [property](#property), [protocol-buffer](#protocol-buffer), [RDF](#rdf),
[reference](#pin-reference), [replication](#replication), [rule](#rule), [server](#server), [service](#service),
[SSV](#ssv), [structure](#structure), [timer](#timer), [uncommitted PIN](#uncommitted-pin),
[unit of measurement](#unit-of-measurement), [value](#value)

<!-- [snapshot isolation](#snapshot-isolation) -->

#Essentials (Data Model)
The key components of Affinity's data model can be presented on two layers:  

  1. a base layer (plain "passive" data items): [PIN](#pin), [property](#property), [value](#value) (including [references](#pin-reference)),
     [collection](#collection), [class](#class)  
  2. an active layer, <span class='pathsql_new'>NEW in AffinityNG</span> (components of this layer are built upon the base layer): [condition](#condition), [action](#action),
     [rule](#rule), [FSM](#fsm), [CEP](#cep), [timer](#timer), [service](#service), [communication PIN](#communication-pin)  

##Data Model: Basic Components

###PIN
The PIN is Affinity's primary information node. It's the basic unit of data.
It is somewhat analogous to the object of an object-oriented programming language
or database, the row of a relational table, the node of a graph database or of XML's DOM,
the document of a document database etc.
A PIN can live in memory only, and can also be persistent - transitions between these two
states is practically seemless, since the PIN's content access interface is the same in both cases.
A PIN can contain many [properties](#property). Each property of a PIN holds a [value](#value),
which can be a simple scalar, a collection, a map or a complex tree structure. 
Unlike rdbms rows, PINs aren't constrained to any table, and can actually belong to many [classes](#class).
Each PIN can describe its own unique structure (i.e. enumerate its [properties](#property)). 
PINs can [refer](#pin-reference) to each other.
Properties can be added to PINs (or removed) without limitation. Each PIN is 
uniquely identified by a [PIN ID](#pin-id-pid). Also <span class='pathsql_new'>NEW in AffinityNG</span>,
a PIN can be [named](./pathSQL basics [data].md#named-pins).

_Note: the theoretical maximum number of properties per PIN is related with the configured
[page](#page) size - typically, in the order of thousands of properties
on a PIN; this limit only puts a boundary on the structural complexity of a PIN,
not the amount of data that each property can contain_

###Property
Properties are symbolic entities (names) that define the relationship between
a [PIN](#pin) and its [values](#value). Properties
define the structure of a PIN. A property, in Affinity, is somewhat analogous to
the column name of a relational table, to a predicate in [RDF](#rdf), to the field
of a structure in C, or to the property of an object in a standard object-oriented programming language.
Property names can be composed of multiple sections, separated by a slash (/) character,
following the same convention as URIs. This enables a practically infinite, semantically 
coherent [namespace](#namespace) usable across multiple applications (which may not necessarily
be fully aware of each other). The basic data model of Affinity does
not attach any type information to properties: instances
of a property ([values](#value)) can be of any type. Properties are a key component of
[class](#class) definitions, because they establish a semantic relationship
across PINs (two PINs that contain the same property have something
in common, and can be classified accordingly).
Because there is no constraint on any value's type, Affinity may 
perform data type [coercion](#coercion) when required.
Internally, a numeric ID is associated with each property. This ID is only
valid in the scope of one database instance; any reference to a property
outside of that scope must use the textual representation of the property.

In the data modeling process with Affinity, selecting meaninful, stable property names
constitutes an important first step, that can influence the effectiveness of
categorization into [classes](#class) later on. When possible, it is recommended to refer
to an already existing source (ontology). The semantic web 
community uses resources such as the following, to achieve similar goals:

 * [http://sindice.com](http://sindice.com)
 * [http://www.sameas.org](http://www.sameas.org)
 * [DAML](http://www.daml.org/ontologies/)

###Value
Like in any database, values can be numbers, strings, booleans, dates, times,
[BLOBs](#blob) etc. A value can also be a [reference](#pin-reference) to another [PIN](#pin)
(or to another [property](#property) of a PIN, or even to a specific collection [element](#element-id-eid)).
At the programming level, the same value structure is also used to hold a [collection](#collection),
a [structure](#structure) or a [map](#map). As a result, the full addressing model of a standard
programming language is readily available in [pathSQL](#pathsql).
Additionally, Affinity provides a data type attribute allowing to attach a physical [unit of measurement](#unit-of-measurement) to a value.
Data types are described in detail [here](./pathSQL reference.md#data-types).
In Affinity, every instance of a value is free to be of any type;
in some contexts Affinity may perform automatic data type [coercion](#coercion).

###Collection
A collection is an ordered list of scalar [values](#value), held by a [PIN](#pin) via
a [property](#property). The values of a collection can be heterogeneous
(they can have different types). Internally, each element of a collection is uniquely 
identified by an immutable [Element ID (eid)](#element-id-eid). This design enables consistent interactions
in concurrent access scenarios. Note that collections cannot directly contain nested collections, in the current version.
Small collections can be represented as arrays internally, and allow random access, 
whereas very large collections must be traversed with an iterator
(with the option of seeking to any known [eid](#element-id-eid)). 
A collection can hold up to 32-bit worth of distinct addressable elements. Collections can be queried just like
plain values (additional control is provided). Collections also play a key role
in other aspects of the data model, such as [ACLs](#acl).
Collections are represented by VT_COLLECTION in [affinity.h](./sources/affinity_h.html).

###Structure
A structure is a set of labeled [values](#value), aka a set of [properties](#property).
The structure is analogous to an embedded PIN (held "by value" by its owner PIN). Structures may contain
substructures. Structures are represented by VT_STRUCT in [affinity.h](./sources/affinity_h.html).
They are a <span class='pathsql_new'>NEW</span> feature of AffinityNG (even though they were
already a stealth feature in AffinityDB).

<!-- TODO: point to exact section in doc (make sure there is one; make sure to cover insert, update, query, delete) -->

###Map
A map is an associative array (or dictionary) where both the value and the key itself are [values](#value).
Unlike the [property](#property) of a [PIN](#pin), the key of a map is not limited to a symbolic entity:
it can be anything. The map essentially opens up full access to Affinity's internal B-link tree.
Maps are represented by VT_MAP in [affinity.h](./sources/affinity_h.html).
They are a <span class='pathsql_new'>NEW</span> feature of AffinityNG.

<!-- TODO: point to exact section in doc (make sure there is one; make sure to cover insert, update, query, delete) -->

###Class
The class is Affinity's main mechanism of data organization. It is very similar to the
materialized view of some relational databases, in the sense that classification operates
automatically ([PINs](#pin) are not explicitly declared to belong to a class) and synchronously
(in the context of transactions). 
Where a table or a view would be used in the relational model, one could use a class 
in Affinity to achieve a similar organization. A class is a stored query predicate 
(involving any number of [properties](#property)).
It is most often defining an [index](#index), although this is not mandatory.
Classes can be declared at any point in time (both earlier and later than the occurrence of PINs
satisfying the predicate). 
In pathSQL, classes are declared with [CREATE CLASS](./pathSQL reference [definition].md#create-class).
Classes are named according to similar conventions as properties (using URIs).
Unlike the 'classes' of programming languages such as C++ or java, 
Affinity classes don't define static _types_, in the sense that they don't establish a binding
contract with [PINs](#pin): a PIN can belong to a class during a part of its lifetime, 
and stop belonging to it during another period; as long as the PIN satisfies the predicate, 
it's part of the class. A PIN can belong to several classes at once. Classification
triggers [notifications](#notification). Affinity defines a 
generalization of classes called [families](#family), but the term 'class' is often used 
to represent both concepts. 'Category' may also be used
as a synonym for 'class' (to avoid the static type connotation).

##Data Model: Active Components
Most of the material from this section is <span class='pathsql_new'>NEW</span> in AffinityNG.

###Condition
A condition is a predicate, i.e. an expression evaluating to true or false:
"should condition X be met, do Y".  Conditions are of common usage in programming
languages in general, and in SQL.  Those that are of particular interest
in the context of the active layer of pathSQL are:  

  1. the predicates of [classes](#class),
  2. the conditions that define [rules](#rule), and
  3. the conditions that define state transitions in [FSMs](#fsm), and
     constitute building blocks for the regular expressions used in [CEP](#cep)  

In pathSQL most conditions are expressed in a declarative or functional style
(as opposed to imperative), for example by callback: the statements defined in the
`afy:onEnter` property of a class are invoked automatically by Affinity when the class's
`afy:predicate` evaluates to true for a given PIN.  

###Action
An action is a list of [DML](./pathSQL reference.md#dml) statements, invoked upon
the satisfaction of a [condition](#condition). Examples of actions are the `afy:onEnter` property of a [class](#class),
or the `afy:action` property of a [timer](#timer).
Actions usually modify some state, either locally in the database, or externally
via [communication PINs](#communication-pin). Actions can cause new [conditions](#condition)
to evaluate to true, and thus trigger a chain of actions.

<!-- TODO: Event -->

###Rule
A rule is a simple construct that binds a conjunction of [conditions](#condition) to a list of [actions](#action).
Internally, a rule functions very much like a [non-indexed class (aka simple event handler)](#class).
The rule hides implementation details, by presenting to the reader its conditions and actions as named entities,
rather than code. Rules also allow to reuse and share conditions and actions. For more information,
see the [basic example](./pathSQL basics [control].md#rules) and the [reference section](./pathSQL reference [definition].md#rule).

###FSM
A Finite State Machine (FSM) is a very common computational model represented as a graph,
where vertices are states and edges are transitions.  Any instance of a FSM operates on
a specific set of PINs, that define its context.  The transitions are a special type of
[rules](#rule), i.e. pairs of [conditions](#condition) and [actions](#action), that operate in that
local context.  This provides a means of encapsulation, as well as a basis for the
definition and recognition of [complex events](#cep).  Affinity's graph database engine
makes it trivial to represent FSMs internally (and in pathSQL).  

###CEP
Complex Event Processing (CEP) is the ability to express and detect more complex
correlations of events (i.e. [conditions](#condition) encountered at discrete points in time).
In pathSQL, those correlations are described as a regular expression of a [FSM's](#fsm)
transitions. CEP is not readily available in the alpha release of AffinityNG.

<!-- TODO: review when available -->

###Timer
Timers invoke [actions](#action) at regular time intervals, in their own thread.
The [reference](./pathSQL reference [definition].md#create-timer) describes in detail how to declare timers.

###Communication PIN
Communication PINs are special PINs with dual personality.
Their "RAW" form (i.e. their plain and simple set of [properties](#property)
and [values](#value)), defines the configuration of the communication,
including a stack of [services](#service).
In pathSQL, once a communication PIN is inserted, its configuration can be examined or
modified by adding the `RAW` keyword to `SELECT` or `UPDATE`.
The second personality, seen via non-decorated `SELECT` or `UPDATE`, is the active
communication channel itself.  In that context, `SELECT` acts as a read, and
`UPDATE` acts as a write.  The [reference](./pathSQL reference [definition].md#communication-pins)
describes communication PINs in more detail.

#Related Concepts

###PIN ID (PID)
The [PIN](#pin) ID is a globally unique ID, *determined by Affinity* when a
new PIN is first committed to the database. It's composed of two
main sections: an [identity](#identity) ID, and a 64-bit value,
unique in the scope of that identity. Within the scope of one
instance of an Affinity database, PINs created by the owner 
can be designated with the second (64-bit) section only, since
the first section will be 0 (STORE_OWNER) - this elision is common,
for example in pathSQL's [references](./pathSQL reference.md#refid). 
By convention, the text representation of this second section should always be in hex. 
PIDs are immutable, and are usually not recycled (if a PIN is deleted, there is no risk that
dangling references would ever point to a new, unrelated PIN) - unless explicitly
requested (e.g. to store streaming or temporary data).
PIDs can be used to specify fixed sets of PINs in a query, or to hold on
to a PIN, or to create [references](#pin-reference).

###Element ID (eid)
In a [collection](#collection), every value is associated with a unique, immutable
Element ID (a 32-bit unsigned value, *determined by Affinity*). This eid is independent from
the position of the element in the collection. A few special logical eids
are defined in the Affinity [interfaces](#interfaces), to let the client
define an initial ordering for new collection elements:
STORE_COLLECTION_ID, STORE_FIRST_ELEMENT, STORE_LAST_ELEMENT. As soon as
the new elements are inserted in the database, Affinity gives them a new
immutable eid.

###Family
A family (short for "family of [classes](#class)") is a generalization of the concept of
class. It is sometimes referred to as a "parametrized class". It can also be viewed as
a sorted index, by analogy with the relational model. Whereas a simple class only
indexes [references to the PINs](#pin-id-pid) that satisfy its predicate, a family also indexes the values of
those PINs that correspond with free [parameters](#parameter) in the predicate. For example, one could define
an "adult" _class_ (with the predicate "age >= 18"), or an "age_limit" _family_
(with the predicate "age >= :0").

###Enumeration
An enumeration allows to declare inter-related symbolic values, without polluting the global namespace.
This can be useful for managing states, options and conditions based on those.
For a more detailed description, please visit the [reference](./pathSQL reference.md#create-enumeration).

### Parameter
In the context of a class [family](#family), a parameter is an unspecified (free) value in the 
definition of the predicate. It usually implies an [index](#index). Typically, this [value](#value) is provided at
query time. For example, using pathSQL, one could define: <pre>'CREATE CLASS age_limit AS select * where age >= :0;'</pre>
and then query with <pre>'SELECT * FROM age_limit(18);'</pre>

###Uncommitted PIN
This terminology is deprecated. An uncommitted PIN designates a PIN that is not persisted.
In AffinityNG, a large proportion of PINs may never be persisted (e.g. some may represent
sample values of which only an aggregated value will be persisted, others may represent
messages only meant to propagate events between sub-systems). AffinityNG distinguishes
the concept of PINs living in memory only, from the loosely related concept of inserting PINs
by batches (see [`IBatch`](./interface [cplusplus].md#ibatch)).

###PIN Reference
A reference is a special [value](#value) type that allows to create explicit relationships between
[PINs](#pin). It maps naturally to the concept of reference or pointer, in most programming
languages. From a database perspective, it enables a form of navigation that can reduce significantly the number of joins
required by an application. A [property](#property) can contain a [collection](#collection) of references.
All types of references contain at least a [PID](#pin-id-pid), but can also contain a [property](#property) ID,
and even a specific [element ID](#element-id-eid).

###BLOB
BLOBs (also known as streams) are binary large objects, such as documents, pictures, video streams etc.
Affinity provides a special [value](#value) type to store them, along with interfaces
to stream the data in and out.

###SSV
SSV stands for "separately stored value". This is one of the mechanisms that Affinity provides
to control the physical arrangement of [PINs](#pin) and their [values](#value) on [pages](#page). For example,
a certain [class](#class) of PINs could represent information about files on disk.
One property could be a thumbnail representation of the file. To improve data-locality
of query-able properties of those PINs, the application could request that the [values](#value) of
the thumbnail [property](#property) be stored on _separate_ pages.

###Identity
Each instance of an Affinity database is associated with the *identity* of a primary owner. The owner
can authorize guest users (*identities*) to access subsets of the data (using [ACLs](#acl)),
or to create new data (in principle, the owner can also fetch data from another
user's database and cache it locally, but this is not fully exposed in the current version).
Each user is identified by name, and the store associates a numeric ID to each name
(the numeric ID of the database owner is 0 (STORE_OWNER)). Within the context 
of any specific store instance, a fully qualified [PID](#pin-id-pid)
contains the numeric ID of that [PIN](#pin)'s owner. Outside of that context
(e.g. in serialized messages), the identity must be specified in textual
form (there is no guaranty that two database instances will associate the same
numeric ID to the same identities).

###Encryption
The files of a database instance created with a specific [identity](#identity) and password
can be encrypted (using AES encryption, on a per-[page](#page) basis). It is only
possible to decrypt them with those identity and password. Affinity provides no mechanism 
to restore the owner's password, should it be forgotten.

###Namespace
All [properties](#property) defined in Affinity belong to a unique, global namespace.
To augment the semantic value of property names, and reduce the risk of undesired
collisions, property names can be composed of as many particles as required (separated by
the slash (/) character). Some of the Affinity programming interfaces also allow to perform
operations in the context of a current subset of the global namespace (by analogy with
URIs and xml, subsets are themselves designated as "namespaces"). This relieves the application
developer from specifying full names everywhere.

###ACL
ACL stands for "Access Control List". Affinity's data model allows to specify
access rights on a per-[PIN](#pin) basis, for individual [identities](#identity).
However, in the initial release of the Affinity package, multi-user scenarios
are not fully enabled yet. 

###Unit of Measurement
Affinity provides a special [value](#value) attribute that allows to attach a physical
unit to real number values (most of the common units for length, speed, surface, volume, weight etc. are supported,
both in the metric and imperial systems). This enhances the semantic and self-descriptive capabilities of a PIN.
It also enables Affinity to perform automatic conversions, when processing compatible types in expressions.
Units are described in detail in the [pathSQL reference](./pathSQL reference.md#units-of-measurement).

###RDF
Affinity does not yet provide a complete solution for RDF, OWL or SPARQL.
However, the core "subject-predicate-object" model can be easily represented
with [PIN](#pin) as subject, [property](#property) as predicate,
and [value](#value) as object.

###Page
The page is the logical unit most closely related with the physical
layout of data on disk. Every page represents a contiguous segment
of the database file. When an instance of a Affinity database is created,
an immutable page size must be specified (the default is 32768 bytes).
Every element of information ([PINs](#pin), [indexes](#index) etc.) is
stored on one or more pages. Because disk io is typically very time consuming,
and databases typically require more disk storage than memory can hold,
an important task of database systems is to minimize io (by compacting as
much data as possible on a page, by mapping pages in and out of memory
as efficiently and infrequently as possible, by keeping related data on pages that
are near, by organizing indexes to satisfy common queries with as
few pages as possible, etc.). Although Affinity takes care of most
of the complexity, the application developer must be at least minimally
aware of these considerations (e.g. to optimize queries, and use features
like [SSVs](#ssv) when appropriate).

###Index
Affinity can automatically index any text [value](#value) of any [PIN](#pin),
to enable full text search. [Classes](#class) and [families](#family) also
define indexes. All those indexes can be combined in queries for fast information
retrieval and update. Affinity query processing does not infer index usage from generic
query conditions: indexes must be explicitly designated in the queries. Indexes can contain
heterogeneous values (values of different types). The type of an index can also be specified
explicitly. Indexing may imply data type [coercion](#coercion); if coercion fails for a value,
the corresponding PIN won't be indexed for this family.

###Coercion
[Values](#value) of a [PIN](#pin) can have any type. However, there are several
circumstances where Affinity will need to evaluate or compare a [property](#property),
and expect a specific type _(for example, when evaluating a [family](#family)'s predicate for a PIN
containing properties that match the predicate but with values that
do not match the corresponding [parameters](#parameter) or [index](#index))_.
In such cases, Affinity can resort to coercion
to translate values to the required type (e.g. strings to integers and vice versa).

###Notification
Notifications are similar to triggers, and allow to track changes
on specific [PINs](#pin) or [classes](#class). The notification functionality
is exposed in a low-level way in the kernel ([startup.h](./sources/startup_h.html)),
and is also available via the [comet](http://en.wikipedia.org/wiki/Comet_%28programming%29)
pattern in the [server](#server). In the future a highly scalable (asynchronous) messaging infrastructure
will be added. By comparison with triggers and stored procedures, Affinity's notifications
establish a more strict boundary between the kernel and application code. They
enhance application code consistency and maintainability, by concentrating all
the logic in one place, using one language. They can also constitute the
starting point of a messaging system between database instances.

###Replication
Although several elements of Affinity's design take database replication
into consideration, replication is not a part of the AffinityNG release.
Database replication is typically used to increase reliability and
accessibility.

<!--
###Snapshot Isolation
Affinity uses the Read-Only multiversion [ROMV] protocol for read-only transactions,
thus enabling non-blocking reads. This only applies to transactions that are explicitly
specified as read-only by the caller. These transactions read a snapshot that
will correspond to the effect of committed write transactions up to the point
the read-only transaction started (n.b. if the number of snapshots grows very large
at any point in time, an older [already allocated] snapshot may be used).
In contrast, plain read-write or read-only transactions (not explicitly marked as
read-only by the caller) progress according to the 2-phase-locking protocol,
and may in some cases read data items in a "newer" state than the corresponding explicit
read-only transaction would.
-->

###Loader
A loader is a declaration for an external [service](#service) dependency,
in the form of a persistent [PIN](#pin), containing essentially 2 properties:
a user-defined URI to name the loader (this URI is stored in `afy:objectID`), and
a relative or absolute path to the loadable library (stored in `afy:load`).
Note that the loader's name is rarely used.  The name by which a service is referred
to insert it into a [communication PIN's](#communication-pin)
service stack is defined statically (programmatically), by the service itself
(e.g. the XML service is referred to by .srv:XML, aka "http://affinityng.org/service/XML").
Once stored, a loader PIN tells the kernel to reload the library whenever it
starts up.  The pathSQL statement is [CREATE LOADER](./pathSQL reference [definition].md#create-loader).

#Interfaces
The [Affinity kernel library](#kernel) is written in C++, and provides a [C++ interface](#c-kernel-interface)
directly talking to the kernel. The main interface to Affinity is [pathSQL](#pathsql), in which it is possible
to write complete programs, with the benefit of having no data translations between multiple representations
(in memory, persistent, or for specialized procedural interfaces). Additionally, a [protocol-buffer](#protocol-buffer)-based
streaming interface is provided, for efficient data transfers in machine-to-machine scenarios, or for the more traditional
client-server case (either via the [server](#server) or via communication [services](#service)).
[Client-side libraries](#client-side-libraries) are also available.

###C++ Kernel Interface
[affinity.h](./sources/affinity_h.html) (along with a few extensions
in [rc.h](./sources/rc_h.html), [startup.h](./sources/startup_h.html) and
[units.h](./sources/units_h.html)) defines a self-contained, low-level interface directly
connected to the Affinity kernel. It exposes a set of C++ abstract base classes (aka C++ interfaces),
for which implementations are provided by the kernel, plus a few constants and structures.
The IAffinity interface represents a store instance, and allows to create interactive sessions.
The ISession interface represents a logical connection to a store instance, and provides an entry point for every possible interaction. 
It understands the [pathSQL](#pathsql) dialect, as well as the [protocol-buffer](#protocol-buffer) streaming interface. 
At a lower level, query conditions and [class](#class) predicates can be defined using expression trees (IExprTree),
which enable the embedding application to develop any desired query language
(e.g. sql, xquery, sparql, linq etc.), and compile it into this low-level representation.
[PINs](#pin) are mainly represented by the IPIN interface, which allows fine-grained control of the in-memory snapshot
of a PIN and related read-write activity to the store (in the context of one specific session).
Since affinity.h is primarily a kernel integration interface (rather than the client interface in a client-server model), 
most of the design decisions related with memory and reference management were
taken by ranking performance implications with higher importance than ease of use. Here's
a [link](./interface [cplusplus].md) to more information.

###pathSQL
pathSQL is the name of a dialect of SQL defined for Affinity.
pathSQL provides complete, self-contained access to all passive and active
aspects of AffinityNG.
Here's a [link](./pathSQL basics [control].md) to more information.

###Protocol-Buffer
Affinity provides a streaming interface based on Google's protocol-buffers:
[affinity.proto](./sources/affinity_proto.html).
This is one of the interfaces exposed by the [server](#server),
and also useful in machine-to-machine scenarios via [services](#service).
Here's a [link](./interface [protobuf].md) to more information.

###Client-Side Libraries
For the traditional client-server scenario, [pathSQL](#pathsql) still implies a mapping process to translate
structured objects on the client side into DDL & DML statements. The [protocol-buffer](#protocol-buffer) interface
provides a more direct means of expressing those structures to Affinity. The client-side libraries
further facilitate the use of both interfaces, in the context of their specific programming language.
The first release emphasizes [javascript](./sources/affinity-client_js.html) for node.js.
Libraries for [python](./sources/affinity_py.html) and ruby are also available.
Java is soon to be released, and C++ is under development for a future release.

#Software Components
The Affinity package contains the following components: the Affinity [kernel](#kernel) library,
a set of built-in and external [services](#service),
the database [server](#server) with its online console and documentation, 
and some [client-side libraries](#client-side-libraries).

###Kernel
The Affinity kernel library is the core component of the Affinity package. 
Most of the Affinity documentation focuses on various aspects of this component.

###Server
This process is a store access server that embeds the Affinity [kernel](#kernel). It understands the HTTP protocol,
and accepts messages in [pathSQL](#pathsql) as well as [protocol-buffer](#protocol-buffer). It can return
results in json format, or [protocol-buffer](#protocol-buffer) format. It can also act as as a web server, for increased
convenience. For more information, visit this [link](./server.md).
In the near future, this process will be drastically simplified by substituting its custom implementation
with generic [services](#service).

###Service
A service is an OS-level compiled plug-in module (dll/so/dylib), loaded dynamically in Affinity
and providing additional building blocks for [communication PINs](#communication-pin).
Those building blocks conform with the `Afy::IService` interface defined in
[affinity.h](./sources/affinity_h.html).
Affinity comes with a few built-in services (e.g. Bluetooth Low Energy, NFC, and Zigbee communications,
XML and regex parsing, mDNS browsing, a HTTP client and server, etc.). Typically, external services are loaded
via a [loader](#loader) statement.
