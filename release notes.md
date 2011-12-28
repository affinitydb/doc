#Release Notes
The following limitations are part of the initial version of mvStore.

 * a few marginal memory leaks
 * Bug 130 - rebuildIndexFT ifdef-ed out
 * Bug 131 - inconsistencies when dropping classes
 * Bug 152 - OP_CONCAT should work on more than 2 values
 * Bug 195 - can't create and drop the same class within one transaction
 * Bug 237 - SELECT * FROM mv:ClassOfClasses; returns some classes with blank mv:URI
