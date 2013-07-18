# What is AffinityNG?

AffinityNG is the second major open-source release of the Affinity kernel, licensed under the Apache License Version 2.0.
In a nutshell, it's a platform that brings together information processing, control, and secure communication.
It's built around the unified data representation, storage and access provided by the AffinityDB core (a graph database).
AffinityNG is designed to lower the barrier of entry for systems targeting
the Internet of Things (IoT), Wireless Sensor Networks (WSNs), ubiquitous computing, control systems
and robotics.

AffinityNG provides complete data-acquisition and device control functionality.  The primary
programming language is a SQL dialect ([pathSQL](./terminology.md#pathsql)).  All components of a program (the program itself
as well as configurations, logs etc.) are represented in a declarative
manner, as inspectable data items ([PINs](./terminology.md#pin)).  AffinityNG offers a
multi-level programming model, with interoperable modes of expression including
event-driven, rule-based, state-machine-based (textual and graphical),
functional, synchronous and asynchronous, etc.  

By taking care of a multitude of lower-level difficulties (e.g. establishment of ad-hoc networks,
communication over various channels, interaction with devices, event detection, exception handling,
synchronization etc.), and by exposing simple solutions at a higher level of abstraction,
we believe that AffinityNG can significantly reduce the burden of interacting with complex ecosystems
seen in typical IoT and industrial sensor network scenarios, such as smart factories, smart retail etc.
A single data representation for all components (the [PIN](./terminology.md#pin))
brings at your fingertips the complete database artillery.  

###Database Core

The database core pays special attention to stream processing for data acquisition and analytics.
For the more static aspects, it also borrows (we hope the best) aspects from
RDBMS, OODBMS, document databases, RDF and XML stores.
Affinity is schema-less (no tables), yet provides a rich native 
[data model](./terminology.md#essential-concepts-data-model) including objects with fields of 
various native datatypes, ordered [collections](./terminology.md#collection) (for modeling XML-like list structures),
[sub-structures](./terminology.md#structure), [associative arrays](./terminology.md#map)
and [references](./terminology.md#pin-reference) (for modeling relationships between objects). 
Objects are self-describing (every field is labeled with a URI) and freely extendable
(different objects can have different fields). Schema or organization ([classes](./terminology.md#class)) 
can be overlaid on the data, without any change to the data.

Affinity provides built-in [indexing](./terminology.md#index) (both structured and full-text) and query processing,
with dynamic [classification](./terminology.md#class).  Affinity objects do not need to be declared as belonging to
any specific class (or table) when they are created.  Instead, objects can be stored first, and then dynamically
classified into independently defined classes.  Membership in these classes may change as the objects change,
and as new applications with new classes begin operating in the store.

The current C++ implementation of Affinity runs in a small-footprint, multithreaded process on smaller ARM-based
systems (iOS, Android, Raspberry Pi etc.), OSX, linux and Windows. There is full support for ACID transactions, with
isolation and crash recovery.

Affinity has a native embedded [C++ interface](./terminology.md#c-kernel-interface), as well as a remoteable interface operating through 
[protobuf](./terminology.md#protocol-buffer)-encoded request/response streams. From punctual queries all the way to complete programs,
everything can be expressed via [pathSQL](./terminology.md#pathsql).

Please refer to the [strengths](./strengths.md) page, for more information on the
basic tenets of Affinity.

## About the Team

The Affinity kernel has been under development since 2004, and is the work of a single author, Dr. Mark Venguerov.
He is surrounded by a small team that focuses primarily on testing and stability, but also provides
complementary components (e.g. services, consoles, client libraries, integration layers with other systems,
documentation, benchmarks, deployment, platform compatibility etc.). At the present time, the team includes:
Michael Andronov, Dr. Adam Back, Ming Li, Wen Lin, Dr. Mark Venguerov and Max Windisch.

## FAQ

### What is the history of Affinity?
Affinity was originally conceived as a flexible embedded database engine for personal information.
It started in 2003-2004, in the context of PI Corporation. PI was acquired by EMC in 2008.
Affinity was transferred to VMware in 2010, where it was released as an open-source
project for the first time (in February 2012), presented as a graph database with a SQL interface.
In 2012-2013 the team re-oriented the product around the requirements of the increasingly
actual "Internet of Things", by adding to the database core a set of
[active components](./terminology.md#active-components-of-the-data-model),
thus transforming it into AffinityNG, a universal embedded information-processing,
control and communication platform - the present release.

### Why Open-Source?
The Affinity Open-Source release shows GoPivotal's support for the Open-Source community.
With fast-growing interest for the "Internet of Things", and increased availability
of very cheap, small, generic hardware platforms (e.g. ARM-based devices), we believe that
a free, easy to use and comprehensive software platform can play an enabling role, by
bringing more developers up to speed and by supporting the deployment of more
systems, faster.

### What were Affinity's design goals?
The AffinityNG platform was designed for the "Internet of Things", providing a unified,
high-level, efficient platform for communication, control and stream processing,
with an event-driven processing model.  AffinityNG builds on a database kernel
with a very flexible data model, no rigid schema, self-describing objects,
automatic multi-classification of objects, a strong commitment to ACID semantics,
and a SQL-based query language with great support for path expressions.
Implemented entirely in C++, with a rigorous discipline ensuring a tiny runtime footprint
(e.g. today the binary size of the kernel is ~1Mb).

### What is Affinity's query language?
We named Affinity's language ["pathSQL"](./pathSQL basics [control].md), to highlight its unique support for path expressions.
It also extends standard SQL with respect to the manipulation of references, collections, sub-structures and classes.
Due to Affinity's data modeling philosophy, constraints are practically absent from pathSQL.
Otherwise, the language offers very good compliance with standard SQL.

### What are Affinity's data elements?
The core data units within Affinity are objects (aka [PINs](./terminology.md#pin)) with untyped [properties](./terminology.md#property).
Affinity currently supports several external formats for serialization, e.g. XML, JSON, and protocol buffers.

### What client libraries exist?
We expect AffinityNG to be used as an operating system, with programs written in pure pathSQL.
For more traditional use cases, [client libraries](./terminology.md#client-side-libraries) are also provided,
for javascript (in the context of node.js), ruby, python and soon java.
The kernel can also be embedded directly into an application, via its C++ interface.
<!-- TODO: update as soon as java lib will be thoroughly reviewed and copied to github -->

### What other features does Affinity have?
Please follow this [link](./features.md) for a complete list of features.
