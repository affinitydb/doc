### DML
Here is a description of pathSQL's Data Manipulation Language.  

#### INSERT
Synopsis:  

  - INSERT [INTO class_name[& class_name2 ...]] [OPTIONS(pin_option[, ...])] (property [, ...]) VALUES ( expression [, ...] ) [, ...]   
  - INSERT [INTO class_name[& class_name2 ...]] [OPTIONS(pin_option[, ...])] property[(prop_option[, ...])] = expression [, ...]  
  - INSERT [INTO class_name[& class_name2 ...]] [OPTIONS(pin_option[, ...])] SELECT ...  

Examples: [insert.sql](./sources/pathsql/insert.html).
	
where *pin_option* can be: 
	- HIDDEN: special pin - totally hidden from search/replication - accessible only through its PID
	- NOTIFY: pin generates notifications
	- NO_INDEX: ???
	- NO_REPLICATION: marks a pin as one which shouldn't be replicated (only when the pin is committed)
	- TRANSIENT:  PINs which are not persisted in commitPINs() but rather used as messages and to trigger class actions.

and *prop_option* is property options which also be specified for a specific property, it can be:
	- NO_FT_INDEX: this property is not to be FT indexed/searched
	- NO_NOTIFICATION: this property doesn't generate notifications when modified
	- STOPWORDS: filter stop words in ft indexing
	- SEPARATE_STORAGE: store this property separately from the pin body (for string, stream and collection property types)		

##### Constraint:
	- The part "INTO class_name" will add a constraint for INSERT operation: need to check the inserted pin should be a member of the class 'class_name'.
	  moreover the multiple classes membership constraint can be added as:  INSERT INTO class1 & class2 & class3 property1 = ...
	- UNIQUE constraint: Is it related to a specific class?

##### Nested INSERT

Nested INSERT is supported, moreover we can specify the child pin which is part of a specific pin, in this case, 
the child pin will be deleted when the parent PIN is deleted, e.g.

		INSERT PROP_PARENT1=(INSERT PART PROP_CHILD1=1, PROP_CHILD2=2 ), PROP_PARENT2='PARENT PIN';

Mutual reference nested INSERT	
the pathSQL also support the insertion of graphs (with cycles) in a single statement, the part "@:number" in below sample indicate the temporary PIN id. e.g.

		INSERT @:1 SELF_REF=30, ref={(INSERT @:2 SELF_REF=31, ref=@:1), (INSERT @:3 SELF_REF=32, ref=@:2)};
		
#### UPDATE
Synopsis:  

  - UPDATE [{pin_reference|class_name| class_family_name({expression_as_param| *| NULL}, ...)}] actions [WHERE conditions]  

where *actions* can be:  

  - {SET|ADD} property = expression [, ...]  
  - DELETE property [, ...]   
  - RENAME property = new_property [, ...]  
  - MOVE collection_property[element_id] {BEFORE|AFTER} {element_id|:LAST|:FIRST}  
  - EDIT ...  

and *pin_reference* can be:
  
  - a pin reference (@PID, e.g. @D001). *Note*: when the UPDATE statement is used as a value of a property of type QUERY, then the AT sign (@) can be used to denote the PIN ID which is being processed.  
  - a collection of pin references with format: { @PID[, ...] }, such as {@D001, @D002}.  

and *expression_as_param* can be any [expression](./pathSQL reference.md#value-expressions).  

The *:LAST* indicator means the element at the LAST postion, and the *:FIRST* indicator means the element at the FIRST position. While the *element_id* does not related to position,  it's the id assigned when the element created, and never be changed anymore, just like pin id.

Examples: [update.sql](./sources/pathsql/update.html).  

Notes:  

1. UPDATE {SET|ADD} a non-existing property: add a property   
2. UPDATE SET an existing property: change the value of that property (if the property is a collection, overwrite the whole collection)   
3. UPDATE ADD an existing property: append a new value to that property (if the property only has one value, then change the type to collection, and append the new value)  

Also pathSQL supports C-style operation-assignments `op=`, where op is one of +,-,*,/,%,&,|,^,<<,>>,>>>,min,max,||. For example:  
        
        UPDATE * SET prop+=1;

Any reference to a non-existing property will make the query return without any result set. In order to skip those PINs missing the property, you can use 
'!' modifiers in UPDATE, and only process those PINs which include that property using the '?' modifiers, such as:  
        
        UPDATE * SET prop!=0, prop?+=1;

This statement will update all PINs: for PINs without "prop" property, it will add this property; for PINs already having "prop", it will increment its value.

#### DELETE/UNDELETE/PURGE   
Synopsis:  

  - {DELETE|UNDELETE|PURGE}  
    [FROM {pin_reference|class_name| class_family_name({expression_as_param| *| NULL}, ...)}]  
    [WHERE conditions]  

where

  - DELETE:    Mark PINs in deleted status ("soft delete").  
  - UNDELETE:  Change from deleted status to normal active status.  
  - PURGE:     Permanently delete PINs from the physical disk (note: cannot remove PINs in deleted status).  
 
Examples: [delete.sql](./sources/pathsql/delete.html).  

### QUERY

Synopsis: 

  - SELECT [ * | {property_name [AS new_name] } [, ...] ]  
    [ FROM from_item [, ...] ]  
    [ WHERE conditions ]  
    [ GROUP BY {property_name | expression | position} [ASC | DESC][ NULLS { FIRST | LAST } ] [, ...] ]  
    [ HAVING conditions ]  
    [ { UNION | INTERSECT | EXCEPT } [ ALL ] select ]  
    [ ORDER BY {property_name | expression | position} [ ASC | DESC ] [ NULLS { FIRST | LAST } ] [, ...] ]  

where *from_item* can be one of:
  
  - pin_reference
  - class_name 
  - class_family_name({expression_as_param| *| NULL}, ...) 
  - path expression
  - from_item join_type from_item [ ON join_condition | USING ( join_column [, ...] ) ]
  - sub_query AS alias_name
  - from_item AS alias_name

and *join_type* can be one of:

  - [ INNER ] JOIN
  - LEFT [ OUTER ] JOIN
  - RIGHT [ OUTER ] JOIN
  - FULL [ OUTER ] JOIN
  - CROSS JOIN

#### Alias name in FROM clause
A substitute name for the FROM item containing the alias. An alias is used for brevity or to eliminate ambiguity for self-joins (where the same table is scanned multiple times). 
When an alias is provided, it completely hides the actual name of the class or family; for example given FROM foo AS f, the remainder of the SELECT must refer to this FROM item as f, not foo.

#### Order by
Examples: [orderBy.sql](./sources/pathsql/orderBy.html).   

  - ORDER BY must appear after ALL the unionsbut .  
  - ORDER BY is considered to apply to the whole UNION result (it's effectively got lower binding priority than the UNION).  

To order a subquery result, use parentheses around the subquery.  

*Notes*:  
1. In order to include null values, NULLS FIRST/LAST must be added to the ORDER BY clause. 
2. The default behavior is order by ASC, without NULL value PINs.

#### Group by
Examples: [groupBy.sql](./sources/pathsql/groupBy.html).   

#### Set Operators: UNION | INTERSECT | EXCEPT
Examples: [set_operator.sql](./sources/pathsql/set_operator.html).   

The functionality of all these set operators is similar to standard SQL, 
except that Affinity does not require that all operands have same number of properties or types. 
Duplicates are identified based on [PIN ID](./terminology.md#pin-id-pid) instead of property value, which is differnt from standard SQL.

The keyword DISTINCT/ALL can be used to eliminate duplicates.

#### Join
Affinity returns immutable PIN collections as query results.

        SELECT * FROM class1 as c1 join class1 as c2 on (c1.prop1 = c2.prop2);

Affinity supports every kind of JOIN (LEFT/RIGHT/FULL/CROSS JOIN), except the natural JOIN.

Examples: [join.sql](./sources/pathsql/join.html).   

#### Sub query in FROM clause
This is not yet supported.

In a future release, when a sub-SELECT appears in the FROM clause, it will act as though its output were created as a temporary table for the duration of this single SELECT command. 
Note that a sub-SELECT must be surrounded by parentheses. 

### Inheritance
Affinity's classification model lets a PIN belong to multiple classes, and also allows to define a hierarchy of classes, such as:

        CREATE CLASS Person AS SELECT * WHERE EXISTS(firstname) OR EXISTS(lastname);
        CREATE CLASS Taxpayer AS SELECT * FROM Person;

Examples: [inheritance.sql](./sources/pathsql/inheritance.html). 

#### How to query only PINs belonging to 2 classes

There are 2 ways:  

  - Using built-in property afy:pinID in WHERE CLAUSE, e.g. SELECT * WHERE class1.afy:pinID=class2.afy:pinID.
  - Using operator & for class names in FROM CLAUSE, e.g.  SELECT * FROM class1 & class2.

### TRANSACTIONS
Affinity not only supports basic transactions, but also sub-transactions.
The session holds a transaction stack.  Every sub-transaction can be rolled back independently (without affecting the state of the whole transaction).
Changes are committed to the store only when the outermost transaction in the stack is committed.  

Examples: [transaction_basic.sql](./sources/pathsql/transaction_basic.html).  

#### Start a Transaction
START TRANSACTION is used to start a transaction/sub-transaction block.

Synopsis: 

  - START TRANSACTION [ transaction_mode [, ...] ]

where transaction_mode is one of:  
 
  - ISOLATION LEVEL { READ UNCOMMITTED | READ COMMITTED | REPEATABLE READ  | SERIALIZABLE }   
  - READ ONLY |READ WRITE  

Examples:  
[transaction_readonly.sql](./sources/pathsql/transaction_readonly.html),
[transaction_sub.sql](./sources/pathsql/transaction_sub.html).   

Note:     
1. Affinity doesn't support isolation level READ UNCOMMITTED.  
2. When READ ONLY is specified, no operation in this transaction must write, otherwise the transaction will fail.  
3. When READ ONLY is specified, Affinity uses the Read-Only Multi-Version Concurrency Control (ROMV), which will not block (or be blocked by) any read/write transaction.  

#### End a Transaction
##### COMMIT
Synopsis: 

  - COMMIT [ALL]; 

If ALL is specified, then Affinity will commit the whole stack of transactions (started in the current session), otherwise it only commits the innermost transaction/sub-transaction block in the stack.    

##### ROLLBACK
Synopsis: 

  - ROLLBACK [ALL];  
    
If ALL is specified, then Affinity will rollback the whole stack of transactions (started in the current session), otherwise it only rolls back the innermost transaction/sub-transaction block in the stack.    
