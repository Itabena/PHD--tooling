---
source_file: Information Theory/Derivations/Kraft's inequality.md
---

## Q1 what the inequality bounds
For a binary prefix code with codeword lengths $\ell_i$, what does Kraft's
inequality assert?

- [x] The sum of $2^{-\ell_i}$ over all codewords is at most 1.
- [ ] The sum of $2^{-\ell_i}$ over all codewords equals exactly 1.
- [ ] The sum of the lengths $\ell_i$ is at most the alphabet size.
- [ ] The longest codeword length is at most $\log_2 n$.

quote: \sum_{i=1}^{n}2^{-\ell_i}\leq 1.
location: Derivations, Kraft's inequality

## Q2 the tree argument
Why does each codeword rule out a block of leaves in the depth-$L$ tree?

- [x] A prefix codeword at depth $\ell_i$ owns the whole subtree beneath it, so no other codeword may sit there.
- [ ] Each codeword is itself a leaf at depth $L$, so it removes exactly one leaf.
- [ ] The tree is pruned to remove codewords that share a prefix after the fact.
- [ ] Codewords are placed only at even depths, halving the available leaves.

quote: every codeword $c_i$ corresponds to a node at depth $\ell_i$.
location: Derivations, Kraft's inequality

## Q3 role of L
What is $L$ in the proof?

- [x] The length of the longest codeword.
- [ ] The number of codewords in the code.
- [ ] The depth at which the first collision occurs.
- [ ] The base-2 logarithm of the code size.

quote: L=\max_i \ell_i
location: Derivations, Kraft's inequality

## Q4 disjointness
The subtrees claimed by two different prefix codewords are:

- [x] disjoint, because neither codeword is a prefix of the other.
- [ ] nested, with the shorter codeword's subtree inside the longer one's.
- [ ] overlapping only at the root of the tree.
- [ ] identical when the codewords have the same length.

quote: binary prefix code
location: Derivations, Kraft's inequality
