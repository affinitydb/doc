Getting Started with mvSQL
==========================

mvSQL is the name of a dialect of SQL defined for mvStore. Although the [mvStore data model](./terminology.md#essential-concepts-data-model) is different
from relational databases, mvSQL is designed to be as close to SQL as possible. This document shows
**how to** insert, update, query and index data ([PINs](./terminology.md#pin)).

For a more systematic survey of mvSQL and its commands, please visit the [reference](./mvSQL reference.md).

To setup a runtime environment, please visit this [link](./mvStore getting started.md).

How to insert data
------------------
There is no concept of table in mvStore: all data are inserted in global scope. Two styles can be used to
perform [PIN](./terminology.md#pin) inserts:

1. SQL-like syntax:

  <code class='mvsql_snippet'>INSERT (property1, property2) VALUES ('value1','value2');</code>    

2. mvStore-specific syntax:

  <code class='mvsql_snippet'>INSERT property1 ='value1', property2 ='value2';</code>  

Different [data types](./mvSQL reference.md#data-types) may have different input formats, e.g.

  <code class='mvsql_snippet'>INSERT prop_string ='string', prop_binary_string =X'DEF5', prop_url=U'http://test/', prop_int=128, prop_float=3.40282f, prop_double=3.40282, prop_bool=true, prop_datatime=TIMESTAMP '2010-12-31 23:59:59', prop_internal=INTERVAL '-12:00:00', prop_collection={1,2,4};</code>  

        PIN@00000000000D000D(10):(<prop_string|VT_STRING>:string  <prop_binary_string|VT_BSTR>:DEF5  <prop_url|VT_URL>:http://test/  <prop_int|VT_INT>:128  <prop_float|VT_FLOAT>:3.40282  <prop_double|VT_DOUBLE>:3.40282  <prop_bool|VT_BOOL>:TRUE  <prop_datatime|VT_DATETIME>:2010-12-31 23:59:59  <prop_internal|VT_INTERVAL>:-12:00:00  <prop_collection|VT_ARRAY(3)>:{<0|VT_INT>:1, <1|VT_INT>:2, <2|VT_INT>:4})
        1 PINs INSERTED.   

Other examples:

  <code class='mvsql_snippet'>INSERT name='Jurgen', bornin='South Africa', email='jleschner@vmware.com', livesin='Boston';</code>  

        {"id":"00000000000A0000", "name": "Jurgen", "bornin": "South Africa", "email": "jleschner@vmware.com", "livesin": "Boston"}
  
  <code class='mvsql_snippet'>INSERT (name, bornin, email, livesin) VALUES ('Sonny', 'USA', 'sthai@mit.edu', 'Boston');</code>  

        {"id":"00000000000A0001", "name": "Sonny", "bornin": "USA", "email": "sthai@mit.edu", "livesin": "Boston"}

How to update or delete data
----------------------------

  <code class='mvsql_snippet'>UPDATE ADD livesin='Cambridge' WHERE name = 'Sonny';</code>  

        {"id":"00000000000A0001", "name": "Sonny", "bornin": "USA", "email": "sthai@mit.edu", "livesin": {"0": "Boston","1": "Cambridge"}}
        
  <code class='mvsql_snippet'>UPDATE SET livesin[1]='USA' WHERE name='Sonny';</code>  

        {"id":"00000000000A0001", "name": "Sonny", "bornin": "USA", "email": "sthai@mit.edu", "livesin": {"0": "Boston","1": "USA"}}
        
  <code class='mvsql_inert'>UPDATE @A0001 ADD school='MIT';</code>  

        {"id":"00000000000A0001", "name": "Sonny", "bornin": "USA", "email": "sthai@mit.edu", "livesin": {"0": "Boston","1": "USA"}, "school": "MIT"}

  <code class='mvsql_inert'>delete @A0001;</code>  

How to classify data 
--------------------
All data are inserted in global scope, but applications can freely define specialized access paths for their data
(before or after the data is inserted), by creating what we call [classes](./terminology.md#class).  Here's an example:

  <code class='mvsql_snippet'>CREATE CLASS class1 AS SELECT * WHERE property1 IS NOT NULL;</code>  

How to query 
------------
Most of the querying syntax in mvStore is compatible with standard SQL: expressions, function calls, WHERE, ORDER BY,
UNION, INTERSECT, EXCEPT etc.  Here's an example:

  <code class='mvsql_snippet'>SELECT * FROM class1 WHERE LENGTH(property2) > 5 ORDER BY property2 DESC NULLS FIRST;</code>  

Other examples:

  <code class='mvsql_snippet'>SELECT name WHERE EXISTS(livesin);</code>

        {"id":"00000000000A0000", "name": "Jurgen"}
        {"id":"00000000000A0001", "name": "Sonny"}

  <code class='mvsql_snippet'>SELECT WHERE livesin = 'Boston' ORDER BY name ASC;</code>  

        {"id":"00000000000A0000", "name": "Jurgen", "bornin": "South Africa", "email": "jleschner@vmware.com", "livesin": "Boston"}
        {"id":"00000000000A0001", "name": "Sonny", "bornin": "USA", "email": "sthai@mit.edu", "livesin": {"0": "Boston","1": "USA"}, "school": "MIT"}
        
  <code class='mvsql_snippet'>SELECT * MATCH AGAINST ('Boston');</code>  

        {"id":"00000000000A0000", "name": "Jurgen", "bornin": "South Africa", "email": "jleschner@vmware.com", "livesin": "Boston"}
        {"id":"00000000000A0001", "name": "Sonny", "bornin": "USA", "email": "sthai@mit.edu", "livesin": {"0": "Boston","1": "USA"}, "school": "MIT"}
        
  <code class='mvsql_snippet'>SELECT * MATCH AGAINST ('South');</code>  

        {"id":"00000000000A0000", "name": "Jurgen", "bornin": "South Africa", "email": "jleschner@vmware.com", "livesin": "Boston"}

How to use join
---------------
mvStore returns immutable PIN collections as query results.  Presently, the join results are somewhat limited
(they only contain PINs from the left-hand class).  Here's an example:

  <code class='mvsql_snippet'>SELECT * FROM class1 AS c1 JOIN class2 AS c2 ON (c1.prop1 = c2.prop2);</code>  

mvStore supports every kind of JOIN (LEFT/RIGHT/FULL/CROSS JOIN), except the Natural JOIN.

How to use [references](./terminology.md#pin-reference)
---------------------
Relational databases use foreign keys to establish relationships between tables.  mvStore uses [references](./terminology.md#pin-reference),
similarly to object-oriented databases:

  <code class='mvsql_snippet'>INSERT (prop1) VALUES ({'test for pin refer', 'test for property refer', 'test for property element refer'});</code>  

        PIN@0000000000050001(1):(<prop1|VT_ARRAY(3)>:{<0|VT_STRING>:test for pin refer,<1|VT_STRING>:test for property refer, <2|VT_STRING>:test for property element refer})
        1 PINs INSERTED.
  
  <code class='mvsql_snippet'>INSERT (propRef, prop2) VALUES (@50001, 'test for ref pin');</code>  

        PIN@0000000000050002(2):(<propRef|VT_REFID>:PIN@0000000000050001        <prop2|VT_STRING>:test for ref pin)
        1 PINs INSERTED.
  
  <code class='mvsql_snippet'>INSERT (propRef, prop2) VALUES (@50001.prop1, 'test for ref property');</code>  

        PIN@0000000000050003(2):(<propRef|VT_REFIDPROP>:PIN@0000000000050001.prop1<prop2|VT_STRING>:test for ref property)
        1 PINs INSERTED.
  
  <code class='mvsql_snippet'>INSERT (propRef, prop2) VALUES (@50001.prop1[2], 'test for ref property element');</code>  

        PIN@0000000000050004(2):(<propRef|VT_REFIDELT>:PIN@0000000000050001.prop1[2]<prop2|VT_STRING>:test for ref property element)
        1 PINs INSERTED.

To leverage this information while querying, mvStore offers the following syntax (path expression):

  <code class='mvsql_snippet'>SELECT * WHERE COUNT(propRef.prop1) > 1;</code>  
  <code class='mvsql_snippet'>SELECT * FROM myclass WHERE propRef.prop2 IN (1, 2, 3);</code>  

<p style="color:red">
REVIEW (maxw): add more stuff here.
</p>

How to use [collections](./terminology.md#collection)
----------------------
### 1. Add elements to a [collection](./terminology.md#collection)
#### 1.1 Insert a PIN with a collection property:

  <code class='mvsql_snippet'>INSERT (prop1, prop2) VALUES ({1, 'inserted', '3'}, 2);</code>  

        PIN@0000000000050001(2):(<prop1|VT_ARRAY(3)>:{<0|VT_INT>:1, <1|VT_STRING>:inserted, <2|VT_STRING>:3}    <prop2|VT_INT>:2)
        1 PINs INSERTED.

#### 1.2 Update a property in a collection
Using "UPDATE ... SET ...", we can replace a property with a whole collection directly:  

  <code class='mvsql_inert'>UPDATE @50001 SET prop3={3, 'update set'};</code>  

        PIN@0000000000050001(3):(<prop1|VT_ARRAY(3)>:{<0|VT_INT>:1, <1|VT_STRING>:inserted, <2|VT_STRING>:3}      <prop2|VT_INT>:2        <prop3|VT_ARRAY(2)>:{<0|VT_INT>:3, <1|VT_STRING>:update set})   
        1 PINs UPDATED.  

Using "UPDATE ... ADD ...", we can convert a property from a scalar value to a collection:

  <code class='mvsql_inert'>UPDATE @50001 ADD prop2='update add';</code>  

        PIN@0000000000050001(3):(<prop1|VT_ARRAY(3)>:{<0|VT_INT>:1, <1|VT_STRING>:inserted, <2|VT_STRING>:3}      <prop2|VT_ARRAY(2)>:{<prop2|VT_INT>:2, <prop2|VT_STRING>:updateadd}    <prop3|VT_ARRAY(2)>:{<0|VT_INT>:3, <1|VT_STRING>:update set})  
        1 PINs UPDATED.  

### 2. Delete an element from a collection

  <code class='mvsql_inert'>UPDATE @50001 DELETE prop1[2];</code>  

        PIN@0000000000050001(3):(<prop1|VT_ARRAY(2)>:{<0|VT_INT>:1, <1|VT_STRING>:inserted} <prop2|VT_ARRAY(2)>:{<0|VT_INT>:2, <1|VT_STRING>:update add}    <prop3|VT_ARRAY(2)>:{<0|VT_INT>:3, <1|VT_STRING>:update set})  
        1 PINs UPDATED.  

### 3. Query on collections
Here are a few examples of queries that can be run against the PIN created in section 1.1:

>1. SELECT * WHERE 1 IN prop1;   
>2. SELECT * WHERE {1,2} IN prop1;  
>3. SELECT * WHERE CARDINALITY(prop1)=2;  
>4. SELECT * WHERE 1 = prop1;  -- equivalent to example 1.
>5. SELECT * WHERE {1,2} = prop1;  -- equivalent to example 2.

How to index properties
-----------------------
mvStore does not support the "CREATE INDEX" statement.  However, it proposes a somewhat similar statement: "CREATE CLASS family". Here's an example:

  <code class='mvsql_snippet'>CREATE CLASS clsfml1 AS select * where prop1 = :0(int, desc, nulls first) and prop2=:1(int);</code>  

This class [family](./terminology.md#family) will create an [index](./terminology.md#index) on prop1 and prop2. The prop1 will be sorted in descending order, and will order nulls first. When parameters are passed, 
the class family behaves like a CLASS. For example:

  <code class='mvsql_snippet'>SELECT * FROM clsfml5(*, 2);</code>  

        PIN@0000000000050012(2):(<prop2|VT_INT>:2	<prop3|VT_STRING>:test NULL)   
        PIN@0000000000050013(3):(<prop1|VT_DOUBLE>:13.3	<prop2|VT_INT>:2	<prop3|VT_STRING>:extra)   
        PIN@0000000000050018(2):(<prop1|VT_DOUBLE>:12.1	<prop2|VT_INT>:2)   
        PIN@0000000000050019(3):(<prop1|VT_INT>:12	<prop2|VT_INT>:2	<prop3|VT_DOUBLE>:34)   
        4 PINs SELECTED.   
