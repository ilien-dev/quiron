Technical interviews can feel like a wall of unknowns, but most problems fall back on a small set of data structures. If you understand these six well (what they're good at, what they cost, and when to use them), you'll recognize patterns faster and spend less time staring at a blank editor.

I'll assume you're comfortable with arrays and strings, since nearly every problem uses them. Here's what to build on top of that.

## 1. Hash Maps (and Hash Sets)

If you only master one structure before your interview, make it this one. Hash maps give you average **O(1)** insertion, deletion, and lookup, which often turns a brute-force O(n²) solution into O(n).

**When to reach for it:**
- Counting frequencies (anagrams, most common element)
- Checking whether you've "seen" something before
- Mapping values to indices (the classic Two Sum)

```python
def two_sum(nums, target):
    seen = {}
    for i, n in enumerate(nums):
        if target - n in seen:
            return [seen[target - n], i]
        seen[n] = i
```

**Interview tip:** When your first idea involves a nested loop, ask yourself, "Could a hash map remember what I need?"

## 2. Stacks and Queues

Stacks (LIFO) and queues (FIFO) are simple, but they show up constantly.

**Stacks** shine when you need to process things in reverse or match pairs:
- Validating parentheses
- Undo operations
- Evaluating expressions
- "Next greater element" problems (monotonic stacks)

**Queues** are the backbone of breadth-first search and anything involving processing in arrival order.

```python
def is_valid(s):
    pairs = {')': '(', ']': '[', '}': '{'}
    stack = []
    for ch in s:
        if ch in pairs:
            if not stack or stack.pop() != pairs[ch]:
                return False
        else:
            stack.append(ch)
    return not stack
```

**Interview tip:** In Python, use `collections.deque` for queues. `list.pop(0)` is O(n).

## 3. Linked Lists

Linked lists rarely appear in production code, but interviewers love them because they test pointer manipulation and careful reasoning about edge cases.

**Common problems:**
- Reversing a list
- Detecting a cycle (Floyd's tortoise and hare)
- Merging two sorted lists
- Finding the middle node

**Interview tip:** Use a **dummy head node** to avoid special-casing an empty list or a change to the first element. Also, draw it out. Seriously. Boxes and arrows on paper prevent most bugs.

## 4. Trees (Especially Binary Search Trees)

Trees test your comfort with recursion. A binary search tree keeps left children smaller and right children larger, giving **O(log n)** operations when balanced.

**Know these traversals cold:**
- **In-order** (left, root, right): yields sorted order in a BST
- **Pre-order** and **post-order**: useful for copying or deleting trees
- **Level-order**: BFS with a queue

```python
def max_depth(root):
    if not root:
        return 0
    return 1 + max(max_depth(root.left), max_depth(root.right))
```

**Interview tip:** Most tree problems reduce to "What do I need from my left and right subtrees, and how do I combine it?" Answer that, and the recursion writes itself.

## 5. Heaps (Priority Queues)

A heap gives you quick access to the smallest (or largest) element: **O(1)** to peek, **O(log n)** to insert or remove.

**When to reach for it:**
- "Top K" problems (K largest elements, K most frequent words)
- Merging K sorted lists
- Finding a running median
- Dijkstra's shortest path algorithm

```python
import heapq

def k_largest(nums, k):
    heap = []
    for n in nums:
        heapq.heappush(heap, n)
        if len(heap) > k:
            heapq.heappop(heap)
    return heap
```

**Interview tip:** If you see "K" in the problem statement, think heap.

## 6. Graphs

Graphs generalize trees: nodes connected by edges, possibly with cycles. Many problems are graphs in disguise, such as grids, dependency lists, and social networks.

**Must-know techniques:**
- **BFS** for shortest paths in unweighted graphs
- **DFS** for exploring connected components and detecting cycles
- **Topological sort** for ordering dependencies (course schedules)

Represent graphs with an **adjacency list** (a hash map of node to neighbors) unless you have a reason not to.

**Interview tip:** Always track visited nodes. Forgetting this is the number one cause of infinite loops in graph problems.

## Final Thoughts

You don't need to memorize hundreds of LeetCode solutions. Focus on understanding *why* each structure exists and what trade-offs it makes. When you see a new problem, ask:

1. What operation do I need to be fast?
2. Which structure makes that operation cheap?

Practice a handful of problems for each structure, talk through your reasoning out loud, and you'll walk into your next interview with far more confidence.

Good luck! 🚀

*What data structure tripped you up most in interviews? Let me know in the comments!*
