# What is mvStore?

mvStore is a new database kernel with features that borrow (we hope the best) aspects from
RDBMS, OODBMS, document databases, graph databases, and RDF and XML stores. 
In academic terms, it is a hybrid between value-oriented databases (that distinguish entities primarily by their values
[e.g. primary keys of relational systems]) and ID-based object-oriented databases.

Unlike relational databases, mvStore is schema-less (no tables), yet provides a rich native 
[data model](./terminology.md#essential-concepts-data-model) including objects with fields of 
various native datatypes, ordered [collections](./terminology.md#collection) (for modeling XML-like list structures)
and [references](./terminology.md#pin-reference) (for modeling relationships between objects). 
Objects are self-describing (every field is labeled with a URI) and freely extensible 
(different objects can have different fields). Schema or organization ([classes](./terminology.md#class)) 
can be overlaid on the data, without any change to the data.

mvStore provides built-in [indexing](./terminology.md#index) (both structured and full-text) and query processing. 
However, unlike relational systems, mvStore does this using dynamic [classification](./terminology.md#class). 
The result is that mvStore objects do not need to be declared as belonging to any specific class (or table) when they are created. 
Instead, objects can be stored first, and then dynamically classified into independently defined classes. 
Membership in these classes may change as the objects change, and as new applications with new classes begin operating in the database.

The current C++ implementation of mvStore runs in a small-footprint, multithreaded process on OSX, linux, Windows and ARM-based systems. 
Data is persisted in the file system. There is support for ACID transactions with isolation and crash recovery.

mvStore has a native [C++ interface](./terminology.md#c-interface), as well as a remoteable interface operating through 
[protobuf](./terminology.md#protocol-buffer)-encoded request/response streams. Queries can be passed to the database via 
[pathSQL](./terminology.md#pathsql), a SQL-like query language. mvStore also produces JSON responses.

mvStore can also operate as a MySQL storage engine via mvEngine, 
which maps between the native mvStore data model and the MySQL relational data model.
This component is not part of the initial release.

Please refer to the [strengths](./strengths.md) page, for more information on the
basic tenets of mvStore.

# FAQ
This section will provide answers to frequently-asked questions.
