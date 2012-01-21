#List of Terms (in Alphabetical Order)
[ACL](#acl), [BLOB](#blob),
[C++ interface](#c-interface), [class](#class), [client-side library](#client-side-libraries),
[coercion](#coercion), [collection](#collection), [data model](#essential-concepts-data-model),
[element ID (eid)](#element-id-eid), [encryption](#encryption), [family](#family), [identity](#identity), [index](#index),
[server](#server), [pathSQL](#pathsql), [ChaosDB](#chaosdb),
[namespace](#namespace), [notification](#notification), [page](#page), [parameter](#parameter), [PIN](#pin),
[PIN ID (PID)](#pin-id-pid), [property](#property), [protocol-buffer](#protocol-buffer), [RDF](#rdf),
[reference](#pin-reference), [replication](#replication), [snapshot isolation](#snapshot-isolation),
[soft deletion](#soft-deletion-vs-purge), [SSV](#ssv), [uncommitted PIN](#uncommitted-pin),
[unit of measurement](#unit-of-measurement), [value](#value)

#Essential Concepts (Data Model)
The key components of ChaosDB's data model are the following:
[PIN](#pin), [property](#property), [value](#value) (including [references](#pin-reference)), [collection](#collection), [class](#class).

###PIN
The PIN is ChaosDB's primary information node. It's the basic unit of data.
It is somewhat analogous to the row of a relational table, the
object of an object-oriented database, the node of a graph database or of XML's DOM,
the document of a document database etc.
A PIN can contain many [properties](#property). Each property of a PIN can either hold a single (scalar) [value](#value),
or an arbitrarily large [collection](#collection) of values. Unlike rdbms rows,
PINs aren't constrained to any table, and can actually belong to many [classes](#class).
Each PIN can describe its own unique structure (i.e. enumerate its [properties](#property)). 
PINs can [refer](#pin-reference) to each other.
Properties can be added to PINs (or removed) without limitation. Each PIN is 
uniquely identified by a [PIN ID](#pin-id-pid).

_Note: the theoretical maximum number of properties per PIN is related with the configured
[page](#page) size - typically, in the order of thousands of properties
on a PIN; this limit only puts a boundary on the structural complexity of a PIN,
not the amount of data that each property can contain_

###Property
Properties are symbolic entities (names) that define the relationship between
a [PIN](#pin) and its [values](#value). Properties
define the structure of a PIN. A ChaosDB property is somewhat analogous to
the column name of a relational table, or to a predicate in [RDF](#rdf).
Property names can be composed of multiple sections, separated by a slash (/) character,
following the same convention as URIs. This enables a practically infinite, semantically 
coherent [namespace](#namespace) usable across multiple applications (which may not necessarily
be fully aware of each other). The basic data model of ChaosDB does
not attach any type information to properties: instances
of a property ([values](#value)) can be of any type. Properties are a key component of
[class](#class) definitions, because they establish a semantic relationship
across PINs (two PINs that contain the same property have something
in common, and can be classified accordingly).
Because there is no constraint on any value's type, ChaosDB may 
perform data type [coercion](#coercion) when required.
Internally, a numeric ID is associated with each property. This ID is only
valid in the scope of one database instance; any reference to a property
outside of that scope must use the textual representation of the property.

In the data modeling process with ChaosDB, selecting meaninful, stable property names
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
(or to another [property](#property) of a PIN, or even to a specific collection [element](#element-id-eid)). There's also a
data type attribute allowing to attach a physical [unit of measurement](#unit-of-measurement) to a value.
In a future release, it will also be possible to define customized sub-structures (as values embedded in a PIN).
Data types are described in detail [here](./pathSQL reference.md#data-types).
At the programming level, the same value structure is also used to hold a [collection](#collection).
In ChaosDB, every instance of a value is free to be of any type;
ChaosDB may perform data type [coercion](#coercion).

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

###Class
The class is ChaosDB's main mechanism of data organization. It is very similar to the
materialized view of some relational databases, in the sense that classification operates
automatically ([PINs](#pin) are not explicitly declared to belong to a class) and synchronously
(in the context of transactions). 
Where a table or a view would be used in the relational model, one could use a class 
in ChaosDB to achieve a similar organization. A class is a stored query predicate 
(involving any number of [properties](#property)).
It is most often defining an [index](#index), although this is not mandatory.
Classes can be declared at any point in time (both earlier and later than the occurrence of PINs
satisfying the predicate). Classes are named according to similar conventions as properties (using URIs).
Unlike the 'classes' of programming languages such as C++ or java, 
ChaosDB classes don't define static _types_, in the sense that they don't establish a binding
contract with [PINs](#pin): a PIN can belong to a class during a part of its lifetime, 
and stop belonging to it during another period; as long as the PIN satisfies the predicate, 
it's part of the class. A PIN can belong to several classes at once. Classification
triggers [notifications](#notification). ChaosDB defines a 
generalization of classes called [families](#family), but the term 'class' is often used 
to represent both concepts. 'Category' may also be used
as a synonym for 'class' (to avoid the static type connotation).

#Related Concepts

###PIN ID (PID)
The [PIN](#pin) ID is a globally unique ID, *determined by ChaosDB* when a
new PIN is first committed to the database. It's composed of two
main sections: an [identity](#identity) ID, and a 64-bit value,
unique in the scope of that identity. Within the scope of one
instance of a ChaosDB database, PINs created by the owner 
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
Element ID (a 32-bit unsigned value, *determined by ChaosDB*). This eid is independent from
the position of the element in the collection. A few special logical eids
are defined in the ChaosDB [interfaces](#interfaces), to let the client
define an initial ordering for new collection elements:
STORE_COLLECTION_ID, STORE_FIRST_ELEMENT, STORE_LAST_ELEMENT. As soon as
the new elements are inserted in the database, ChaosDB gives them a new
immutable eid.

###Family
A family (short for "family of [classes](#class)") is a generalization of the concept of
class. It is sometimes referred to as a "parametrized class". It can also be viewed as
a sorted index, by analogy with the relational model. Whereas a simple class only
indexes [references to the PINs](#pin-id-pid) that satisfy its predicate, a family also indexes the values of
those PINs that correspond with free [parameters](#parameter) in the predicate. For example, one could define
an "adult" _class_ (with the predicate "age >= 18"), or an "age_limit" _family_
(with the predicate "age >= :0").

### Parameter
In the context of a class [family](#family), a parameter is an unspecified (free) value in the 
definition of the predicate. It usually implies an [index](#index). Typically, this [value](#value) is provided at
query time. For example, using pathSQL, one could define: <pre>'CREATE CLASS age_limit AS select * where age >= :0;'</pre>
and then query with <pre>'SELECT * FROM age_limit(18);'</pre>

###Uncommitted PIN
This concept is more or less invisible, depending on the interface used to talk to ChaosDB.
An uncommitted [PIN](#pin) is a representation that is not yet stored in the database.
The C++ interface allows to create uncommitted PINs in memory, that can be inter-connected
(and form any number of graphs). These PINs can be committed very efficiently in a single-operation transaction
(thus minimizing the amount of disk io required, and maximizing opportunities for
data compaction on [pages](#page)). The implementations supporting the [protocol-buffer](#protocol-buffer) streaming interface
and [pathSQL](#pathsql) both create uncommitted PINs automatically, whenever possible.

###PIN Reference
A reference is a special [value](#value) type that allows to create explicit relationships between
[PINs](#pin). It maps naturally to the concept of reference or pointer, in most programming
languages. From a database perspective, it enables a form of navigation that can reduce significantly the number of joins
required by an application. A [property](#property) can contain a [collection](#collection) of references.
All types of references contain at least a [PID](#pin-id-pid), but can also contain a [property](#property) ID,
and even a specific [element ID](#element-id-eid).

###BLOB
BLOBs (also known as streams) are binary large objects, such as documents, pictures, video streams etc.
ChaosDB provides a special [value](#value) type to store them, along with interfaces
to stream the data in and out.

###SSV
SSV stands for "separately stored value". This is one of the mechanisms that ChaosDB provides
to control the physical arrangement of [PINs](#pin) and their [values](#value) on [pages](#page). For example,
a certain [class](#class) of PINs could represent information about files on disk.
One property could be a thumbnail representation of the file. To improve data-locality
of query-able properties of those PINs, the application could request that the [values](#value) of
the thumbnail [property](#property) be stored on _separate_ pages.

###Identity
Each instance of a ChaosDB database is associated with the *identity* of a primary owner. The owner
can authorize guest users (*identities*) to access subsets of the data (using [ACLs](#acl)),
or to create new data (in principle, the owner can also fetch data from another
user's database and cache it locally, but this is not fully exposed in the current version).
Each user is identified by name, and the store associates a numeric ID to each name
(the numeric ID of the database owner is 0 (STORE_OWNER)). Within the context 
of any specific database instance, a fully qualified [PID](#pin-id-pid)
contains the numeric ID of that [PIN](#pin)'s owner. Outside of that context
(e.g. in serialized messages), the identity must be specified in textual
form (there is no guaranty that two database instances will associate the same
numeric ID to the same identities).

###Encryption
The files of a database instance created with a specific [identity](#identity) and password
can be encrypted (using AES encryption, on a per-[page](#page) basis). It is only
possible to decrypt them with those identity and password. ChaosDB provides no mechanism 
to restore the owner's password, should it be forgotten.

###Namespace
All [properties](#property) defined in ChaosDB belong to a unique, global namespace.
To augment the semantic value of property names, and reduce the risk of undesired
collisions, property names can be composed of as many particles as required (separated by
the slash (/) character). Some of the ChaosDB programming interfaces also allow to perform
operations in the context of a current subset of the global namespace (by analogy with
URIs and xml, subsets are themselves designated as "namespaces"). This relieves the application
developer from specifying full names everywhere.

###ACL
ACL stands for "Access Control List". ChaosDB's data model allows to specify
access rights on a per-[PIN](#pin) basis, for individual [identities](#identity).
However, in the initial release of the ChaosDB package, multi-user scenarios
are not fully enabled yet. 

###Soft Deletion vs Purge
[PINs](#pin) can be marked for deletion, while being preserved in the database.
This reduces their accessibility through querying, while providing an opportunity to
restore them later on. Note that deleted PINs can be retrieved with queries, 
provided that MODE_DELETED is specified. Irreversible deletion is called "purge".

###Unit of Measurement
ChaosDB provides a special [value](#value) attribute that allows to attach a physical
unit to real number values (most of the common units for length, speed, surface, volume, weight etc. are supported,
both in the metric and imperial systems). This enhances the semantic and self-descriptive capabilities of a PIN.
It also enables ChaosDB to perform automatic conversions, when processing compatible types in expressions.
Units are described in detail in the [pathSQL reference](./pathSQL reference.md#units-of-measurement).

###RDF
ChaosDB does not yet provide a complete solution for RDF, OWL or SPARQL.
However, the core "subject-predicate-object" model can be easily represented
with [PIN](#pin) as subject, [property](#property) as predicate,
and [value](#value) as object.

###Page
The page is the logical unit most closely related with the physical
layout of data on disk. Every page represents a contiguous segment
of the database file. When an instance of a ChaosDB database is created,
an immutable page size must be specified (the default is 32768 bytes).
Every element of information ([PINs](#pin), [indexes](#index) etc.) is
stored on one or more pages. Because disk io is typically very time consuming,
and databases typically require more disk storage than memory can hold,
an important task of database systems is to minimize io (by compacting as
much data as possible on a page, by mapping pages in and out of memory
as efficiently and infrequently as possible, by keeping related data on pages that
are near, by organizing indexes to satisfy common queries with as
few pages as possible, etc.). Although ChaosDB takes care of most
of the complexity, the application developer must be at least minimally
aware of these considerations (e.g. to optimize queries, and use features
like [SSVs](#ssv) when appropriate).

###Index
ChaosDB can automatically index any text [value](#value) of any [PIN](#pin),
to enable full text search. [Classes](#class) and [families](#family) also
define indexes. All those indexes can be combined in queries for fast information
retrieval and update. ChaosDB query processing does not infer index usage from generic
query conditions: indexes must be explicitly designated in the queries. Indexes can contain
heterogeneous values (values of different types). The type of an index can also be specified
explicitly. Indexing may imply data type [coercion](#coercion); if coercion fails for a value,
the corresponding PIN won't be indexed for this family.

###Coercion
[Values](#value) of a [PIN](#pin) can have any type. However, there are several
circumstances where ChaosDB will need to evaluate or compare a [property](#property),
and expect a specific type _(for example, when evaluating a [family](#family)'s predicate for a PIN
containing properties that match the predicate but with values that
do not match the corresponding [parameters](#parameter) or [index](#index))_.
In such cases, ChaosDB can resort to coercion
to translate values to the required type (e.g. strings to integers and vice versa).
Note that [indexes](#index) are homogeneous and therefore may imply data coercion.

###Notification
Notifications are similar to triggers, and allow to track changes
on specific [PINs](#pin) or [classes](#class). The notification functionality
is exposed in a low-level way in the kernel ([startup.h](./sources/startup_h.html)),
and is also available via the [comet](http://en.wikipedia.org/wiki/Comet_%28programming%29)
pattern in the [server](#server). In the future a highly scalable (asynchronous) messaging infrastructure
will be added. By comparison with triggers and stored procedures, ChaosDB's notifications
establish a more strict boundary between the kernel and application code. They
enhance application code consistency and maintainability, by concentrating all
the logic in one place, using one language. They can also constitute the
starting point of a messaging system between database instances.

###Replication
Although several elements of ChaosDB's design take database replication
into consideration, replication is not part of the initial release of ChaosDB.
Database replication is typically used to increase reliability and
accessibility.

###Snapshot Isolation
ChaosDB uses the Read-Only multiversion [ROMV] protocol for read-only transactions,
thus enabling non-blocking reads. This only applies to transactions that are explicitly
specified as read-only by the caller. These transactions read a snapshot that
will correspond to the effect of committed write transactions up to the point
the read-only transaction started (n.b. if the number of snapshots grows very large
at any point in time, an older [already allocated] snapshot may be used).
In contrast, plain read-write or read-only transactions (not explicitly marked as
read-only by the caller) progress according to the 2-phase-locking protocol,
and may in some cases read data items in a "newer" state than the corresponding explicit
read-only transaction would.

#Interfaces
The [ChaosDB](#chaosdb) kernel library is written in C++, and provides a [C++ interface](#c-interface)
directly talking to the kernel. In addition, it also proposes [pathSQL](#pathsql), and a [protocol-buffer](#protocol-buffer)-based
streaming interface, both of which are better suited as client interfaces for remote access (e.g. through
a [server](#server)). [Client-side libraries](#client-side-libraries) are also available.

###C++ interface
[chaosdb.h](./sources/chaosdb_h.html) (along with a few extensions
in [rc.h](./sources/rc_h.html), [startup.h](./sources/startup_h.html) and
[units.h](./sources/units_h.html)) defines a self-contained, low-level interface directly
connected to the ChaosDB kernel. It exposes a set of C++ abstract base classes (aka C++ interfaces), 
plus a few constants and structures. The ISession interface represents a logical connection to 
a database instance, and provides an entry point for every possible interaction. 
It exposes the [pathSQL](#pathSQL) dialect, as well as the [protocol-buffer](#protocol-buffer) streaming interface. 
At a lower level, query conditions and [class](#class) predicates can be defined using expression trees (IExprTree),
which enable the embedding application to develop any desired query language
(e.g. sql, xquery, sparql, linq etc.), and compile it into this low-level representation.
[PINs](#pin) are mainly represented by the IPIN interface, which allows fine-grained control of the in-memory snapshot
of a PIN and related read-write activity to the database (in the context of one specific session).
Since chaosdb.h is primarily a kernel integration interface (rather than a client interface), 
most of the design decisions related with memory and reference management were
taken by ranking performance implications with higher importance than ease of use. Here's
a [link](./ChaosDB cpp.md) to more information.

###pathSQL
pathSQL is the name of a dialect of SQL defined for ChaosDB.
Here's a [link](./pathSQL primer.md) to more information.

###Protocol-Buffer
ChaosDB provides a streaming interface based on Google's protocol-buffers:
[chaosdb.proto](./sources/chaosdb_proto.html).
This is one of the interfaces exposed by the [server](#server).
Here's a [link](./ChaosDB protobuf.md) to more information.

###Client-Side Libraries
Although the [server](#server) makes it easy to talk to the store using [pathSQL](#pathsql),
this traditional approach still implies a mapping process to translate
structured objects on the client side into DML statements. The [protocol-buffer](#protocol-buffer) interface
provides a more direct means of expressing those structures to ChaosDB. The client-side libraries
further facilitate the use of both interfaces, in the context of their specific programming language.
The first release emphasizes [javascript](./sources/chaosdb-client_js.html) for node.js.
Libraries for [python](./sources/chaosdb_py.html) and ruby are also available,
and java and C++ are under development.

#Software Components
The ChaosDB package contains the following components: the [ChaosDB](#chaosdb) kernel library,
the [database server](#server) with its online console and documentation, 
and some [client-side libraries](#client-side-libraries).

###ChaosDB
The ChaosDB library is the core component of the ChaosDB package. 
It provides a comprehensive database engine that proposes a new, powerful, object-friendly
[data model](#essential-concepts-data-model), while preserving many of the precious properties of relational database systems,
such as a [SQL interface (pathSQL)](#pathsql), ACID transactions, logging and recovery, efficient [page](#page) management and
B-link tree [indexing](#index), full-text indexing, etc.
It is written in C++, and provides a number of [interfaces](#interfaces).
This library could be embedded directly into an application.
Most of the ChaosDB documentation focuses on various aspects of this component.

###server
This process is a database server that embeds [ChaosDB](#chaosdb). It understands the HTTP protocol,
and accepts messages in [pathSQL](#pathsql) as well as [protocol-buffer](#protocol-buffer). It can return
results in json format, or [protocol-buffer](#protocol-buffer) format. It is primarily
a database server, but its HTTP interface allows it to act as a web server, for increased
convenience. For more information, visit this [link](./ChaosDB server.md).
