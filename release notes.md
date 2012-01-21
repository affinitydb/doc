#Release Notes
The following limitations are part of the initial version of ChaosDB.

 * dump&load and replication not fully exposed
 * limitations related to introspection of a class's properties
 * a few marginal memory leaks
 * Bug 130 - rebuildIndexFT ifdef-ed out
 * Bug 131 - inconsistencies when dropping classes
 * Bug 152 - OP_CONCAT should work on more than 2 values
 * Bug 195 - can't create and drop the same class within one transaction
 * Bug 237 - SELECT * FROM ks:ClassOfClasses; returns some classes with blank ks:URI
