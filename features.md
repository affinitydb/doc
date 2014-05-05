#Features
AffinityNG is a universal embedded information-processing, control and communication platform,
with a graph database at its heart. More context is available on the [philosophy](./FAQ.md),
[software components](./terminology.md#software-components),
[interfaces](./terminology.md#interfaces) and [data model](./terminology.md#essentials-data-model). Here
is a list of AffinityNG's main features:

 * one semantically rich representation for all transient and persistent data: the [PIN](./terminology.md#pin)
 * event-driven programming model combining [rules](./terminology.md#rule), [finite-state machines](./terminology.md#fsm) and [CEP](./terminology.md#cep) - <span class='pathsql_new'>NEW</span>
 * [communication PINs](./terminology.md#communication-pin) to read from and write to the real world (i.e. sensors,
   actuators, web services, other instances of AffinityNG, etc.) - <span class='pathsql_new'>NEW</span>
 * [timer PINs](./terminology.md#timer) to trigger events on a time basis - <span class='pathsql_new'>NEW</span>
 * declarative, configurable and queryable definitions (as [PINs](./terminology.md#pin)) of all [active components](./terminology.md#data-model:-active-components) - <span class='pathsql_new'>NEW</span>
 * loadable external [services](./terminology.md#service) - <span class='pathsql_new'>NEW</span>
 * a <span class='pathsql_new'>NEW</span> data type for matrices, and native pathSQL support for linear algebra
 * small, embeddable, cross-platform C++ kernel (with no dependency on any virtual machine)
 * ACID transactions
 * logging & recovery
 * [pathSQL](./terminology.md#pathsql) query language
 * graph queries seemlessly integrated into SQL

<!-- TODO: when we approach the next official release, enumerate the published services -->

##More Details

 * path expressions for advanced, recursive, yet compact graph queries
 * nested DML for single-statement graph inserts and updates
 * nested transactions
 * ability to mix transient and persistent PINs
 * compact storage, suited for structured data as well as semi-structured, dynamic objects (aka [PINs](./terminology.md#pin))
 * streaming interface using [protocol-buffers](./terminology.md#protocol-buffer)
 * universal naming convention for [properties](./terminology.md#property) and [classes](./terminology.md#class), using URIs
 * globally-unique object IDs with random-access physical addressing ([PIDs](./terminology.md#pin-id-pid))
 * self-describing objects (objects can represent themselves as dictionaries)
 * highly optimized B-link tree indexing engine, used for all indexes
 * transactional, dynamic, automatic and continuous multi-classification of objects, stored in indexes
 * multi-segment indexing
 * asynchronous query processing option, for highly concurrent servers
 * transactional full-text indexing
 * ability to use full-text search in combination with regular structured queries
 * extensive support for data transformations in query results
 * [notifications](./terminology.md#notifications) for object-level changes as well as for classification changes
 * authenticated sessions
 * page-level AES [encryption](./terminology.md#encryption) and log encryption
 * extensive multi-user support (e.g. hundreds of distinct store instances can be managed by a single process)
 * [ACL](./terminology.md#acl) at object granularity
 * rich set of [data types](./pathSQL reference.md#data-types), including [collections](./terminology.md#collection),
   [structures](./terminology.md#structure) (<span class='pathsql_new'>NEW</span>),
   [maps](./terminology.md#map) (<span class='pathsql_new'>NEW</span>),
   [references](./terminology.md#pin-reference) and [BLOBs](./terminology.md#blob)
 * [units of measurement](./terminology.md#unit-of-measurement) and dimensionality control in calculations
 * data type and unit conversions
 * document model allowing document objects to own constitutive parts
 * page-level storage control at the granularity of properties of objects
 * external sort (implicit) for very large result sets
