#Release Notes
The following limitations are part of the initial release of Affinity.

 * dump&load and replication not yet available
 * limitations with multi-segment indexes
 * limitations with projections in JOIN and ORDER BY
 * limitations with nested JOIN (bug 183)
 * limitations with path expressions in clauses other than FROM
 * limitations with projections in path expressions
 * limitations related with introspection of a class's properties
 * can't insert cyclic graphs in a single statement, with protobuf and pathSQL (bug 173)
 * SELECT COUNT with protobuf (bug 249)
 * the function to rebuild full-text indexes is disabled (bug 130)
 * inconsistencies when dropping classes (bug 131)
 * incompleteness of OP_CONCAT (bug 152)
 * server clean shutdown (bug 200)
 * weak support for uniqueness during insert (bug 166)
 * a few marginal memory leaks
