#Strengths
The [features](./features.md) in AffinityNG are designed to lower the barrier of entry for systems targeting
the Internet of Things (IoT), Wireless Sensor Networks (WSNs), ubiquitous computing, control systems
and robotics.  The emphasis is on maximizing the efficiency of writing, executing, tuning and maintaining applications
for those contexts.  Within a declarative, compact, fully introspectable programming environment,
set up in one line of code a fully-configured communication channel, a parametrized data conversion filter,
an event handler, a finite-state machine or a customizable rule.

##Flexible Communication Channels
By representing any communication channel with a PIN, and accessing channels
via one simple uniform syntax (`SELECT` to read and `UPDATE` to write), AffinityNG's
interface to the physical world becomes as simple as reading and writing
memory locations or registers. Whether it's reading from or writing to a sensor, an actuator,
a peer node or a web service, AffinityNG makes it look all the same to the programmer.
The db kernel's native ability to [transform](#easy-data-transformations) data
further facilitates integration. [Services](./terminology.md#service) complete
the picture by taking care of the complexities inherent to each physical situation
(e.g. the NFC service's job is to make it easy to read various models of NFC tags,
on various types of readers). The kernel's service infrastructure also facilitates
writing services, by taking care of several aspects such as buffering, configuration etc.
The service infrastructure is designed to cover the whole spectrum from
low-level network protocols all the way to high-level patterns such as
store&forward or publish&subscribe, for example. The kernel favors
on-the-fly reconfigurability (e.g. `UPDATE` a configuration property
on a communication PIN, and expect the following communications to
adapt immediately).

##Mobile Ad-Hoc Networks
In a context where an increasing number of devices in the network are not
handled or monitored by a human, it is crucial to simplify as much as possible
all aspects of making those devices come together, 
in order to realize their full potential. Security and privacy also expose different
challenges, in that context. With its use of mDNS, its support for [FSMs](./terminology.md#fsm)
and path expressions to traverse graphs, we believe AffinityNG has a lot to offer
to help programmers tame the IoT.

##Customizable Rules And Multi-Level Programming
AffinityNG aims at offering the right tools for the right people involved
with small programmable devices. For example, AffinityNG's [rules](./terminology.md#rule)
open a door for the participation of non-programmer professionals or technicians,
to fine-tune their system. [FSMs](./terminology.md#fsm) may be more familiar
to people already involved with control systems or network protocols.
SQL should facilitate access to yet another set of people.

##Extendable Services Library
External services provide another way of augmenting the capabilities of the
platform. Be it for platform-dependent considerations, performance,
portability or any other reason, the kernel's service infrastructure
and compact service interface make it easy to integrate lower-level
programming languages (e.g. C/C++).

<!--
##Synergy
provide a few scenarios; sharing of info across systems, config, etc.
-->

##Easy Data Transformations
Many of the [strengths](#strengths-of-the-database-core) of the database core
contribute to making data transformations very natural in AffinityNG. In an environment
with unbounded numbers of devices and formats, data transformations
are of paramount importance to building sucessful networks of things.

<!-- TODO: expand with concrete examples -->

##Full Introspection
Everything in AffinitiNG is stored as a [PIN](./terminology.md#pin),
meaning that everything can be queried, correllated, joined etc.
That includes code, conditions, actions, rules, states, transitions,
data, logs etc.

##Debugging and Maintenance
In complex networked systems, traceability is usually a requirement, and
failure tracking a core activity. It only makes sense for configurations
and logs to be first-class citizens of the system. In AffinityNG,
logs can refer to the configurations or graphs that caused events to happen,
by reference or by value. Logs can then be inspected via the same query
engine, within the same rich context.

##Strengths Of the Database Core
The database [features](./features.md) in Affinity aim at providing a solid foundation, for
a seemless and efficient integration of programs. Affinity brings together concepts from several
existing database technologies (including relational, object-oriented,
graph-oriented, document-based and RDF systems).

<!-- Note: presented as '##'-level on purpose, to reduce the relative importance of pure-db stuff compared to above -->
<!-- TODO: review, filter, improve, update -->

<!-- 
Note: seems less relevant to emphasize this in AffinityNG, so commenting it out for the time being...

Capability                                                                                        Relational DB   Object DB       Graph DB        Document DB     Affinity    
------------------------------------------------------------------------------------------------  --------------  --------------  --------------  --------------  ------------
1. [SQL for non-relational data](#sql-for-non-relational-data)                                    nk (1)          some            nk              some            YES
2. [Path expressions](#path-expressions-for-compact-set-navigation)                               uncommon        nk              YES             nk              YES
3. [References and easy graph navigation](#references-and-easy-graph-navigation)                  nk (2)          YES             YES             nk (3)          YES
4. [Automatic, continuous, agile categorization of objects](#agile-categorization)                uncommon (4)    nk              nk              some (5)        YES
5. [Rich queries with joins](#rich-queries-with-joins)                                            YES             some            some            nk              YES
6. [Super-types as first-class citizens](#super-types-as-first-class-citizens)                    nk              YES             nk              nk              YES
7. [Ordered collections](#ordered-collections-to-retain-sequential-information)                   nk              YES             nk              YES             YES
8. [Transactional, automatic full-text indexing](#transactional-automatic-full-text-indexing)     some            some            nk              some            YES
9. [Notifications for unified programming](#uniform-programming-environment-with-notifications)   nk              nk              YES             nk              YES
10. [Small, portable, embeddable c++ kernel](#small-portable-embeddable)                          some            nk              nk              nk              YES
11. Easy scalability, both in terms of replication and partitioning                               hard            nk              nk              YES             no (6)

<!--
10. [Snapshot isolation for high concurrency](#snapshot-isolation-for-high-concurrency)           some            nk              nk              nk              YES
--

<sub>
1- nk stands for "Not to our Knowledge"
2- while it seems possible to emulate a graph db efficiently with a relational db, it's not trivial, and graph db are usually considered a better fit for that use case
3- to our knowledge it's practically impossible to emulate a graph db within a document db, without major compromises
4- some of the more powerful relational db offer synchronously-updated materialized views that can select from multiple tables
5- we know of one document db that offers a similar feature
6- replication is part of our short-term plans, and partitioning is in our mid-term plans
</sub>

-->

###Entities evolving freely over time
In Affinity, each instance of an entity (aka _[PIN](./terminology.md#pin)_ or _object_ or _instance_) is free to contain any attribute
at any time. An entity is not bound to any table (or _type_ or _[class](./terminology.md#class)_ or _category_).
Instances evolve independently from the categories to which they may belong at any point in time.
This is accomplished without any compromise with respect to transactional integrity or performance:
PINs and their classification change in the context of transactions, and rely on indexes.
A transaction can involve any number of PINs.

###Discoverability, information re-use, and information sharing
While objects can evolve freely in Affinity, it remains possible to discover and track them
at any moment. Affinity provides several mechanisms: [classification](./terminology.md#class),
full-scan queries (not recommended for deployed applications but convenient during development),
and [notifications](./terminology.md#notification).

The ability to query the store is essential for mutli-user collaboration and for inter-application 
interoperability. Objects created or modified by one agent can be discovered by other agents 
without explicit transmission of data between agents. The agents simply monitor 
(or wait for notifications from) the database, which serves as a common intermediary, similar 
to "publish and subscribe" messaging systems. 

Information re-use is the idea that the information in a persisted object should not be locked up by 
the application which created the object. If the information is valuable to its owner, the owner should be able to 
manipulate that information using a variety of applications (of the owners choice).

Information sharing is the idea that if information is represented with sufficient "semantics", then it can 
be shared and interpreted by other systems. Note that even a partial shared understanding of some of the properties 
in an object between systems is sufficient for this kind of interoperability.

###Self-descriptiveness
Objects in Affinity are naturally serializable as dictionaries that fully describe their contents.
Therefore, it's trivial to export or transport objects.

###Data before structure (a two-step modeling process)
Affinity makes it possible for data to exist before structures (or schema) are defined, refined or modified.
This capability rests in part on the definition (by applications) of a globally meaningful,
consistent and stable vocabulary of [property names](./terminology.md#property).
The selection (or creation) of such a vocabulary represents 
the first step of data modeling with Affinity, and suffices to enable the creation of data. 
The second step is categorization, and it happens independently and dynamically.
Affinity recognizes that pre-defined structures and schema are essential for most computer programs.
This separation between pure (intrinsic) data structure and application-enabling schema is designed to
facilitate the coexistence of applications, and their sharing of data. Affinity also allows
to transform data at query time.

###Property names as URIs: avoiding confusion
By requiring a global vocabulary of [property names](./terminology.md#property), and emphasizing the importance of selecting
universal, high-quality definitions from the start (that will last throughout the life-cycle and
at every level of the modeling process), Affinity reduces the chances of confusion related to imprecise terminology.

###Agile categorization
The relational approach implies a water-fall modeling process: an a-priori, all-or-nothing exercise of categorization 
(one cannot insert rows in a table that is not yet defined). This often crystallizes into rigid 
physical models (tables, views, indexes), where objects can only be represented in one state of their
potentially evolving structure (for example, in real life a merchandise item may be moved or modified;
depending on where the merchandise is located, more or less attributes may be required to track it;
it's not possible in a relational database to just move that row across various tables).
Also, it is difficult to 'correct' pitfalls once the database contains data. Incomplete or extendable
models (such as plug-in architectures) require awkward modeling strategies. Integration with external 
data sources can be painful. In contrast, Affinity proposes a much more agile approach, where 
[categories](./terminology.md#class) can be created and modified iteratively, without affecting the data. Categories and 
structures can be known to (or defined by) some software components (e.g. plug-ins), and ignored by others.

###Super-types as first-class citizens
With Affinity, the identity of objects is automatically secured (by their [PID](./terminology.md#pin-id-pid)),
and the type hierarchy is free to evolve independently from instances.
Super-types can pre-exist sub-types, and when sub-types are declared they don't modify, invalidate or
hide super-types, or force any manual reorganization of the data. Types can be specialized and combined.
Objects can match multiple types (aka [classes](./terminology.md#class) or categories). Use-cases
that imply a proliferation of sub-types are not a problem for Affinity. Software components are free to
interact with super-types or sub-types, at their convenience.

###No need to model attributes as entities
In the relational model, when it becomes too difficult to model complex problems
due to unstable or unpredictable structures, a last-resort solution involves a method sometimes
referred to as "very high level of attribute generalization", which consists in
modeling attributes as entities, such that arbitrary sets of attributes can be
combined to represent a wider variety of things. Affinity's [PIN](./terminology.md#pin) does that
implicitly.

###No need to create unnecessary structures
Not all structures require the same level of detail in modeling, or the same accessibility. For example,
applications that handle catalogs of components will be primarily interested in organizing common aspects of these
components, and would gladly leave out the minute details of each component (plug-ins can
take care of these details; or generic introspective methods can walk the complementary information).
The exercise of fitting all this component-specific data into a relational model
becomes a waste of time, justified mainly by the need for a unified storage infrastructure.
Affinity allows these structures to coexist (without the pain of rigid modeling), and to 
evolve into their ideal usage in due time (with the help of dynamic classification).

###Temporary data in-place, and implicitly indexed
Another consequence of Affinity's data model is that temporary data can be
attached directly to already existing [PINs](./terminology.md#pin). All pre-existing 
indexes on those PINs remain valid access paths to the temporary data, and come at no extra cost.
The same holds for references. Compared with temporary tables, this can
represent a significant performance advantage (in terms of indexing and
locking, for example). Affinity does not require any special (in-advance)
modeling or planning.

###Exclusivity-arcs in-place
In relational modeling, exclusivity-arcs model mutually exclusive relationships between
entities (e.g. an inventory item can only be at one place at one time). In the object-oriented
realm, this can be represented with a pointer to a base-class, and sub-classes. With Affinity,
another option is to implement this in-place, with a single [PIN](./terminology.md#pin)
that just evolves over time.

###Automatic assignment of globally-unique IDs to all instances
The relational model implies a complex decision process for each table: the selection of a primary key.
Object databases in general, and Affinity in particular simplify this process by attributing a globally unique surrogate 
key ([PID](./terminology.md#pin-id-pid)) to every object ([PIN](./terminology.md#pin)). 
This key enables random access to the instance, without the cost of an additional index lookup. 
Combined with [references](./terminology.md#pin-reference), it simplifies 
the modeling of relationships, and the traversal of graphs. In the context of super-types and sub-types, 
the globally unique PID eliminates issues such as contention for the next (shared)
unique id across multiple tables, or partially-null primary keys. In the context of data warehousing,
the PID removes the problem of accounting for each new dimension table in the compound primary key of the
fact table. More generally, these characteristics reduce significantly the justification for debates around primary
(and surrogate) keys encountered with relational systems.

###References and easy graph navigation
By avoiding joins for traversals on specific instances, Affinity provides similar advantages as object and graph databases,
in comparison with relational systems. Affinity also allows set operations on references, and [collections](./terminology.md#collection)
of [references](./terminology.md#pin-reference), providing the best of both worlds _(note: path indexing 
is not yet available, but planned for a future release; when relevant, joins are used in the meantime)_.
References are simpler to model than foreign keys, and further reduce the burden in terms of selecting keys upfront
(and in an immutable way).

###Path expressions for compact set navigation
The following relational queries

        select * from emp e
        where e.deptno in(select d.deptno from dept d
        where e.deptno = d.deptno);

        select * from emp e
        where exists (select d.deptno from dept d
        where e.deptno = d.deptno);

Can be written in a more compact form with Affinity, in a model using [references](./terminology.md#pin-reference):

        select * from emp where exists(dept);

Similarly,

        select P.upc from Productlist as P
        where P.upc in
          ((select W.upc from Warehouse as W where W.upc = P.upc),
          (select T.upc from TruckCenter as T where T.upc = P.upc),
          (select G.upc from Garbage as G where G.upc = P.upc)) and P.makerid in
          (select M.id from Maker as M where M.country = 'Belgium');

becomes:

        select upc from Inventory where maker.country = 'Belgium';

The difference is even more striking when arbitrarily deep recursion is involved.
Just imagine how to translate the following statement with traditional SQL:

        SELECT * FROM
          qn1:orgid(3).
          qn2:friendof[CONTAINS(qn2:occupation, 'ist')]{+}.
          qn2:friendof[BEGINS(qn2:lastname, 'M')];

###Ordered collections to retain sequential information
When normalizing a relational model, there is sometimes a risk of missing or losing
sequential information (e.g. the order of repeating column groups, that could
have implicitly represented a sequence). Affinity's [collections](./terminology.md#collection)
allow to easily model this information, without any need to fall back on weaker representations 
such as repeating column groups or sequence columns.

###Simpler modeling with less entities
In many cases, Affinity reduces the number of entities or columns required to model data.
For example, [references](./terminology.md#pin-reference) simplify the representation of many-to-many 
relationships. [Collections](./terminology.md#collection) can spare additional tables, 
repeating groups or sequence columns. [Units of measurement](./terminology.md#unit-of-measurement) 
save an extra column. URIs (and eventually enumerations) can spare a category table.

###Transactional, automatic full-text indexing
Affinity automatically indexes text properties, without any additional work required by the client,
while allowing to easily exclude undesired properties and PINs. Values of collections are 
indexed as well. Indexing happens synchronously alongside all 
other transaction operations, and queries can combine text searching with other conditions, 
with the same ACID expectations as for any other index.

###Units of measurement
Affinity allows to easily attach semantic value to floating point values, using [units of measurement](./terminology.md#unit-of-measurement).
This simplifies modeling, enhances the semantic value of data, and enables automatic conversions in the evaluation of 
expressions involving those values.

###SQL for non-relational data
Even though the Affinity [data model](./terminology.md#essential-concepts-data-model) is quite different from relational databases,
[pathSQL](./terminology.md#pathsql) is designed to be as close to SQL as possible (especially
the [DML](./pathSQL reference.md#keywords)). Affinity and pathSQL can handle relational modeling as well as
modeling by references.

###XML-friendliness
[Collections](./terminology.md#collection) and [references](./terminology.md#pin-reference) allow to easily represent 
the XML structure. [Namespaces](./terminology.md#namespace) and [property names](./terminology.md#property) (as URIs) 
further facilitate the mapping. It is possible to map the whole 
database to a single virtual XML document, in which XPath can navigate efficiently
and comprehensively. _Note: Affinity doesn't currently provide a XQuery or XPath interface, but
did in the past and may in the future._

###RDF-friendliness
The "subject-predicate-object" model can be easily represented in Affinity with the PIN as subject,
the property as predicate, and the value as object.

###No constraint on string length
Affinity is designed to deal with very flexible data structures, without sacrificing performance.
In particular, it does not require any upfront decision regarding the length of strings:
no CHAR vs VARCHAR vs LONG specification. Long strings can be explicitly stored on [separate pages](./terminology.md#ssv)
if desired, and very long strings can be accessed via a streaming interface.

###No compromise with structured data
Even though Affinity opens up the data modeling options and emphasizes
a freedom that could be associated with object-oriented, graph or document databases for example,
no compromise is made when the time comes to process structured data.
Great care is invested to represent data on [pages](./terminology.md#page) in the most compact form possible, and
to ensure data locality.

###Rich queries with joins
The query engine is extremely flexible, and accommodates
the SQL [DML](./pathSQL reference.md#keywords) without difficulty, with joins as first-class citizens.
Advanced features such as path expressions (and later path indexing) push the envelope by making set operations on graphs
considerably more easy and efficient.

###No compromise with transactions
Affinity makes no compromise with transactions. For example, it integrates full-text
indexing and searching into the transaction boundaries, with the same ACID guaranties
as everything else. The default PIN locking protocol used is "strong 2-phase-locking"
(all locks that a top-level transaction has acquired are held until the transaction terminates).
Unlike document databases, which usually can't do multi-object transactions, Affinity takes no shortcut
with respect to transactions. This choice makes room for the coexistence of applications that
require full transactional support, along with applications that require weaker transactional
guaranties (such as those well suited for document databases).

###Transactional DDL
Affinity's model is not only less tightly coupled with schema, but its DDL (Data Definition Language)
is transactional. This contributes to a simpler database maintenance process, for example when applying
migration patches (no need to worry about half-applied migration patches).

<!--
###Snapshot isolation for high concurrency
[Snapshot isolation](./terminology.md#snapshot-isolation) enables non-blocking reads of
stable, consistent data. This isolation mechanism provides excellent ACID guaranties,
while enabling highly-concurrent read-intensive scenarios, without affecting normal
write activity. In the future, it may also be used as a foundation for backup,
replication etc.
-->

###Nested transactions
Affinity conveniently allows code in a session to emit transactions inside already existing transactions.
This can be useful, for example, when integrating third-party software components.

###Robust recovery
Database recovery (the process that guaranties consistency when restarting the database after a crash) 
is one of those features that are practically invisible... until you need to count on it. 
It's difficult to implement properly, difficult to test, and difficult to prove for correctness in
practice (even though the algorithms are formally established). Considerable efforts were invested to
make Affinity's recovery rock-solid.

###Small, portable, embeddable
The [Affinity kernel](./terminology.md#kernel) is a small library (<50K LOC, < 1Mb binary) written in C++
and ported to all mainstream platforms (OSX, linux, windows, ARM-based devices). It allows one to configure all essential
aspects of its runtime footprint (global memory usage, memory usage per session, disk usage, file sizes etc.).

###Uniform programming environment with notifications
The Affinity kernel does not accept stored procedures, and does not process triggers directly.
Instead, it forwards [notifications](./terminology.md#notification) (e.g. via the [server](./terminology.md#server)) to clients
that request them, thus allowing those clients to express their data-change handling code in the
same programming environment as the rest of the application.

###Notifications to implement state machine or discrete-event dynamic systems
Class and PIN notifications cover the whole spectrum of value changes, structural changes
and state transitions that can occur over time. The notification approach further
facilitates the implementation of complex systems based on such events.

###Not an object database
With its use of object IDs ([PIDs](./terminology.md#pin-id-pid)) and
[references](./terminology.md#pin-reference), technically Affinity can be considered an object-oriented database.
Interacting with entities as objects is a deliberate choice. However, Affinity avoids
intimate associations with any particular object-oriented programming language, by providing
a pure-data abstraction (the [PIN](./terminology.md#pin)) and low-level expression evaluation
primitives. Also, Affinity does not attempt to solve the memory management complications
implicit in traditional object-oriented systems. In that respect, Affinity adopts a stance 
similar to some of the recent graph and document databases.

###Constraints transformed into qualifying criteria for classification
In general, constraints are conspicuously absent from Affinity's interfaces. This is because Affinity
is designed to bridge together various data storage approaches and representations of knowledge,
with special care to allow evolution of structures in time. In relational modeling,
even simple attributes can actually model constraints (e.g. only a woman can have a maiden name).
With Affinity, constraints become qualifying criteria for classification (if a class requires a maiden name, then
only objects with a maiden name will be classified by it; or conversely, if a class excludes
maiden names, then objects with a maiden name will not be classified by it). However, pathSQL
also provides a way to emulate traditional constraints, with its syntax to insert objects
into a set of existing classes (in which case, if a new object doesn't comply with any of the specified
classes, it won't be inserted).

###Flexible security features
Affinity offers AES encryption of pages and log files. It can also attach a HMAC signed cryptographic
checksum to each page, thus preventing attacks (in a context where encrypted pages may be stored
on external or cloud storage), and also providing redundant page-level integrity check.
Sessions are authenticated for owner and guest users. Affinity's interface also prevents
SQL injection attacks.
