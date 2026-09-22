# Six Data Structures To Help You Ace Your Technical Interview

Technical interviews can feel overwhelming. There are hundreds of possible questions, and it's easy to feel like you need to memorize all of them. The good news is that most interview problems are built on a small set of core data structures. If you really understand these six, you'll be able to recognize patterns and approach almost any question with confidence.

Let's go through them one by one.

## 1. Arrays

Arrays are the foundation of almost everything. They store elements in contiguous memory, which gives you **O(1)** access by index.

**Key operations:**
- Access: O(1)
- Search: O(n)
- Insert/delete at the end: O(1) amortized
- Insert/delete in the middle: O(n)

**When to use them in interviews:** Look for problems involving sequences, subarrays, or sorting. Common techniques include **two pointers** (e.g., checking if a sorted array has a pair that sums to a target) and **sliding window** (e.g., finding the longest substring without repeating characters).

## 2. Hash Maps

If you only take one thing from this post, let it be this: when you're stuck, ask yourself whether a hash map would help. Hash maps (also called dictionaries or objects) store key-value pairs with **O(1)** average lookup, insertion, and deletion.

```javascript
function twoSum(nums, target) {
  const seen = new Map();
  for (let i = 0; i < nums.length; i++) {
    const complement = target - nums[i];
    if (seen.has(complement)) return [seen.get(complement), i];
    seen.set(nums[i], i);
  }
}
```

**When to use them:** Counting frequencies, detecting duplicates, grouping items, or caching results you've already computed. They often turn an O(n²) brute-force solution into O(n).

## 3. Linked Lists

A linked list is a chain of nodes, where each node points to the next. Unlike arrays, they don't need contiguous memory, and inserting or removing a node is **O(1)** once you have a reference to it. The tradeoff is **O(n)** access by index.

**When to use them in interviews:** You'll see classic problems like reversing a linked list, detecting a cycle, or merging two sorted lists. Learn the **fast and slow pointer** technique: it's the key to finding cycles and the middle of a list.

## 4. Stacks and Queues

These are two sides of the same coin.

- **Stack:** Last In, First Out (LIFO). Think of a stack of plates.
- **Queue:** First In, First Out (FIFO). Think of a line at the coffee shop.

Both have **O(1)** push and pop operations.

**When to use them:** Stacks are perfect for matching parentheses, undo functionality, and evaluating expressions. They're also how recursion works under the hood, so any recursive solution can be rewritten with an explicit stack. Queues show up in breadth-first search and anything involving processing items in order.

## 5. Trees

A tree is a hierarchical structure made of nodes, where each node has children. The most common type in interviews is the **binary search tree (BST)**, where every node's left children are smaller and right children are larger. A balanced BST gives you **O(log n)** search, insert, and delete.

**When to use them:** Expect questions on traversals (in-order, pre-order, post-order, and level-order), finding the height of a tree, validating a BST, or finding the lowest common ancestor. Most tree problems are solved recursively, so get comfortable thinking in terms of "what do I do at this node, and what do I ask my children?"

Also worth knowing: **heaps**, a special kind of tree used to implement priority queues. They're great for "find the top K" problems.

## 6. Graphs

Graphs are collections of nodes (vertices) connected by edges. Trees are actually a special kind of graph. Graphs can be directed or undirected, weighted or unweighted, and are usually represented as an **adjacency list**.

```javascript
const graph = {
  A: ['B', 'C'],
  B: ['D'],
  C: ['D'],
  D: [],
};
```

**When to use them:** Social networks, maps, dependencies, and grids are all graphs in disguise. Master **breadth-first search** (shortest path in unweighted graphs) and **depth-first search** (exploring all paths, detecting cycles). Topological sort is also a common follow-up.

## How to Practice

Knowing the data structures is only half the battle. Here's how to make it stick:

1. **Implement each one from scratch** at least once. Building a linked list or a BST yourself teaches you more than reading about it.
2. **Practice by pattern, not at random.** Do five sliding window problems in a row, then five tree problems, and so on.
3. **Always talk about complexity.** Interviewers want to hear you reason about time and space tradeoffs.
4. **Say your thinking out loud.** Communication is just as important as the correct answer.

## Wrapping Up

Arrays, hash maps, linked lists, stacks and queues, trees, and graphs make up the core of most technical interviews. Get comfortable with each one, learn the common patterns, and you'll walk into your next interview feeling a lot more prepared.

Good luck, you've got this!
