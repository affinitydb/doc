# What is Affinity?

Affinity is a new database kernel with features that borrow (we hope the best) aspects from
RDBMS, OODBMS, document databases, graph databases, and RDF and XML stores. 
In academic terms, it is a hybrid between value-oriented databases (that distinguish entities primarily by their values
[e.g. primary keys of relational systems]) and ID-based object-oriented databases.

Unlike relational databases, Affinity is schema-less (no tables), yet provides a rich native 
[data model](./terminology.md#essential-concepts-data-model) including objects with fields of 
various native datatypes, ordered [collections](./terminology.md#collection) (for modeling XML-like list structures)
and [references](./terminology.md#pin-reference) (for modeling relationships between objects). 
Objects are self-describing (every field is labeled with a URI) and freely extensible 
(different objects can have different fields). Schema or organization ([classes](./terminology.md#class)) 
can be overlaid on the data, without any change to the data.

Affinity provides built-in [indexing](./terminology.md#index) (both structured and full-text) and query processing. 
However, unlike relational systems, Affinity does this using dynamic [classification](./terminology.md#class). 
The result is that Affinity objects do not need to be declared as belonging to any specific class (or table) when they are created. 
Instead, objects can be stored first, and then dynamically classified into independently defined classes. 
Membership in these classes may change as the objects change, and as new applications with new classes begin operating in the database.

The current C++ implementation of Affinity runs in a small-footprint, multithreaded process on OSX, linux, Windows and ARM-based systems. 
Data is persisted in the file system. There is support for ACID transactions with isolation and crash recovery.

Affinity has a native [C++ interface](./terminology.md#c-interface), as well as a remoteable interface operating through 
[protobuf](./terminology.md#protocol-buffer)-encoded request/response streams. Queries can be passed to the database via 
[pathSQL](./terminology.md#pathsql), a SQL-like query language. Affinity also produces JSON responses.

Affinity can also operate as a MySQL storage engine via afyEngine, 
which maps between the native Affinity data model and the MySQL relational data model.
This component is not part of the initial release.

Please refer to the [strengths](./strengths.md) page, for more information on the
basic tenets of Affinity.

## About the Team

The Affinity kernel has been under development since 2004, and is the work of a single author, Dr. Mark Venguerov.
He is surrounded by a small team that focuses primarily on testing and stability, but also provides
complementary components (e.g. server, consoles, client libraries, integration layers with other systems,
documentation, benchmarks, deployment etc.). At the present time, the team includes:
Michael Andronov, Dr. Adam Back, Ming Li, Wen Lin, Dr. Anoop Sinha, Sonic Wang, and Max Windisch.

## FAQ

### What is the history of Affinity?
Affinity was originally conceived as a flexible database engine for all personal information.
It started in 2003-2004, in the context of PI Corporation. PI was acquired by EMC in 2008.
Affinity was transferred to VMware in 2010.

### Why is VMware Open-Sourcing it now?
The Affinity Open-Source release shows VMware's support for the Open-Source community.
Affinity has been under research &amp; development for several years, and has reached a level of maturity
that we hope will be appreciated by the Open-Source community, especially for novel scenarios such as
social graph analysis, stream processing, and modern web applications.

### What were Affinity's design goals?
Designed with the target of having very flexible data model, no rigid schema, self-describing objects,
automatic multi-classification of objects, a strong commitment to ACID semantics,
and a SQL-based query language with great support for path expressions.
Implemented entirely in C++, with a rigorous discipline ensuring a tiny runtime footprint
(e.g. today the binary size of the kernel is ~1Mb).

### What is Affinity's query language?
We named Affinity's language ["pathSQL"](./pathSQL primer.md), to highlight its unique support for path expressions.
It also extends standard SQL with respect to the manipulation of references, collections and classes.
Due to Affinity's data modeling philosophy, constraints are practically absent from pathSQL.
Otherwise, the language offers very good compliance with standard SQL.

### What are Affinity's data elements?
The core data units within Affinity are objects (aka [PINs](./terminology.md#pin)) with untyped [properties](./terminology.md#property).
Affinity currently supports two external formats for serialization: JSON, and protocol buffers.
Both are exposed by the server via HTTP.

### What client libraries exist?
Presently, [client libraries](./terminology.md#client-side-libraries) are provided for javascript (in the context of node.js), ruby and python.
Additional libraries are under development for java and C++. The kernel can also be
embedded directly into an application, via its C++ interface.

### What other features does Affinity have?
Please follow this [link](./features.md) for a complete list of features.

### What about scalability?
Affinity is released in Open-Source as a single-node database kernel.
The initial release doesn't provide full support for replication, which is planned
for the next release.

### What is planned for Affinity in the future?
We are focusing on three aspects: better pathSQL for social graph analysis,
stream processing for small devices, and a novel approach to covering the spectrum of 
small devices to cloud storage.
