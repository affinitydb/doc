#Features
mvStore is a new database kernel with features that borrow aspects from
RDBMS, OODBMS, document databases, graph databases, and RDF and XML stores. More context
is available on the [philosophy](./mvStore FAQ.md), [software components](./terminology.md#software-components),
[interfaces](./terminology.md#interfaces) and [data model](./terminology.md#essential-concepts-data-model). Here
is a list of mvStore's features:

 * small, embeddable, cross-platform C++ kernel (no dependency on any virtual machine)
 * [mvSQL](./terminology.md#mvsql) interface, plus streaming interface using [protocol-buffers](./terminology.md#protocol-buffer)
 * path expressions for advanced (yet compact) graph queries
 * ability to mix SQL and graph queries
 * nested DML for compact graph inserts and updates
 * ACID transactions (with support for JOIN spanning multiple objects)
 * [snapshot isolation](./terminology.md#snapshot-isolation) for read-only transactions
 * nested transactions
 * logging & recovery
 * compact storage, suited for structured data as well as semi-structured, dynamic objects (aka [PINs](./terminology.md#pin))
 * universal naming convention for [properties](./terminology.md#property) and [classes](./terminology.md#class), using URIs
 * globally-unique object IDs with random-access physical addressing ([PIDs](./terminology.md#pin-id-pid))
 * self-describing objects (objects can represent themselves as dictionaries)
 * highly optimized B-link tree indexing engine, used for all indexes
 * transactional, dynamic, automatic and continuous multi-classification of objects, stored in indexes
 * multi-segment indexing
 * asynchronous query processing, for highly concurrent servers
 * transactional full-text indexing
 * ability to use full-text search in combination with regular structured queries
 * [notifications](./terminology.md#notifications) for object-level changes as well as for classification changes
 * authenticated sessions
 * page-level AES [encryption](./terminology.md#encryption) and log encryption
 * extensive multi-user support
 * [ACL](./terminology.md#acl) at object granularity
 * rich set of [data types](./mvSQL reference.md#data-types), including [collections](./terminology.md#collection),
   [references](./terminology.md#pin-reference) and [BLOBs](./terminology.md#blob)
 * [units of measurement](./terminology.md#unit-of-measurement) and dimensionality control in calculations
 * data type and unit conversions
 * document model allowing document objects to own constitutive parts
 * [soft deletion](./terminology.md#soft-deletion-vs-purge) of objects
 * page-level storage control at the granularity of properties of objects
 * external sort (implicit) for very large result sets
 * basic replication framework

###The following features are expected soon:

 * extensive support for data transformations in query results
 * fine-grained sub-structure inside objects (similar to what's available in document databases), for efficiency and expressiveness
 * DSNS (Data Stream Management System) with data windowing and triggers, for ESP (Event Stream Processing) and EDA (Event Driven Architectures)
 * object and schema versioning, with support for concurrent schema versions at run-time

###The following features are expected later:

 * path indexing for path queries or transitive closure
 * automatic data partitioning for scalability, and distributed querying
 * reasoning, inductive inferences, data mining
 * XQuery interface
