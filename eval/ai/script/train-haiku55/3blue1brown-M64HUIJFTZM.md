# The Unexpectedly Hard Windmill Question (2011 IMO, Problem 2)

**[RUNTIME: ~12 min]**

---

## COLD OPEN

**[ON SCREEN: a scatter of colored dots on a white background. A thin black line spins slowly around one of them.]**

**NARRATOR:**

Watch this line. It's pivoting around a dot. Then it hits a second dot and starts pivoting around that one. Then a third. It keeps going, hopping from point to point, forever.

Here's the question. Can we set this up so that every single dot takes a turn as the pivot, and does it again and again, forever?

This is Problem 2 from the 2011 International Mathematical Olympiad. It looks like a playful puzzle about spinning lines. Most people who try it get stuck fast, and many of the students who solved it on the exam did so in a short, clever burst of insight.

Today we're going to work through it together. No advanced math required, just patience and curiosity.

**[ON SCREEN: title card, "The Unexpectedly Hard Windmill Question"]**

---

## PART 1: THE PROBLEM, SLOWLY

**[ON SCREEN: the problem statement appears line by line as narration reads it.]**

**NARRATOR:**

Let's read the problem carefully, because every word matters here.

We start with a finite set S of points in the plane. There are at least two of them. And there's one important rule: no three points of S are collinear. That means no three of them lie on a single straight line. It's a bit like placing pins on a corkboard so that no three pins line up.

Now define the windmill.

We pick a point P in S, and we draw a line ℓ through it. This line is our blade. It rotates clockwise around P, like the hand of a clock whose center is the pivot. It keeps turning until, for the first time, it runs into another point of S. Call that point Q.

At that moment, the line has found a new pivot. So now it rotates clockwise around Q, until it hits the next point of S. Then it pivots around that point, and so on, forever.

**[ON SCREEN: animated diagram showing the line rotating around P, catching Q, then rotating around Q.]**

The goal is to show that we can choose a starting point P and a starting line ℓ through it, so that the windmill uses every single point of S as a pivot infinitely many times.

Notice what that asks for. It's not enough for the windmill to visit every point once. It has to keep coming back, over and over, to every point, forever.

---

## PART 2: WHY IT FEELS IMPOSSIBLE AT FIRST

**[ON SCREEN: a set of points with a line sweeping, with some points quickly skipped.]**

**NARRATOR:**

Let's get a feel for why this is hard. Try a simple experiment in your head.

Suppose you place a pivot at some point, and the blade starts sweeping. Depending on where the other points sit, the blade might hit a point on the far left, pivot there, and then immediately hit a point nearby that sends it right back. You can easily end up in a little loop, bouncing between two or three points forever.

If that happens, the other points are simply never used. The windmill is trapped.

So the challenge is really about escaping loops. We need a starting configuration that refuses to get stuck in a small corner of the set.

Here's the first hint of structure. If the blade gets stuck in a loop, something about the geometry must be limiting where it can go. The trick is to find a starting choice that prevents that limiting from happening.

---

## PART 3: A FIRST REAL IDEA, THE CONVEX HULL

**[ON SCREEN: a set of points with a stretchy rubber band wrapped around the outside. The band is labeled "convex hull."]**

**NARRATOR:**

Now we bring in a standard tool: the convex hull.

Imagine each point of S is a nail in a board. Stretch a rubber band around all the nails and let it snap tight. The shape it makes is the convex hull of S. The nails touching the band are its vertices. Every other nail sits inside the band, somewhere in the interior.

A few things are nice about the convex hull. First, all of the points of S lie inside it. Second, the vertices of the hull are, in a sense, the most exposed points. They're the ones you can see from outside.

This matters for the windmill. Consider a vertex P of the hull, and draw a line through P that touches the hull only at P, with every other point of S on one side. Such a line is called a supporting line. Think of it as a ruler laid against the outside of the rubber band, touching it at one corner.

**[ON SCREEN: a supporting line drawn at a hull vertex, with all other points shaded on one side.]**

**NARRATOR:**

This is the starting configuration we want to consider. We put the pivot at a hull vertex P, and the blade ℓ on a supporting line through P.

Why this choice? Because it gives us a clean starting point. All the other points are on one side of the blade. As the blade starts rotating clockwise, it begins to sweep across the set, and that sweeping is exactly what drives the windmill.

But here's where we need to be careful. A supporting line doesn't stay a supporting line for long. As the blade rotates around P, it will swing across the interior of the hull and hit interior points. So the pivots won't stay on the hull. They'll wander inward. That's good news, actually, because we need every point to get a turn, including the ones inside.

---

## PART 4: THE SWEEP ARGUMENT

**[ON SCREEN: a line rotating through a full 360 degrees around a point, with points flashing as it passes them.]**

**NARRATOR:**

Here's the central intuition, and I want to be honest with you about its scope.

The official solutions make this precise with careful bookkeeping. What I'm giving you now is the shape of the argument, so you can see why it works.

Think about the blade's direction. Each time the blade pivots around a point, it sweeps through angles. Because it rotates clockwise and never stops, its direction keeps decreasing without end. Over time, it covers every direction again and again.

Now suppose some point X of S is never used as a pivot. What does that mean for the blade? It means that whenever the blade swept past X's direction from the current pivot, the blade hit some other point first. Otherwise X would have become the next pivot.

So X is always "shadowed." Some other point always sits in front of it, from the blade's point of view.

The key insight is that this shadowing can't last forever. The windmill keeps moving to new pivots, and each new pivot has a different view of the whole set. A point that is hidden behind one pivot can be exposed from the next.

**[ON SCREEN: a point X highlighted, with arrows showing it being hidden from one pivot and visible from another.]**

**NARRATOR:**

So the picture is this. The windmill is like a lighthouse that hops from tower to tower. Each tower casts shadows, but the beam keeps moving, and every point eventually gets lit.

That's the heart of it. The supporting-line start prevents the windmill from settling into a small region, and the constant clockwise rotation prevents any point from being hidden forever.

---

## PART 5: WHY THE STARTING CHOICE MATTERS

**[ON SCREEN: two side-by-side windmills. One starts from an arbitrary line and gets stuck in a loop. The other starts from a supporting line and visits all points.]**

**NARRATOR:**

Let's compare two starts to see why the choice of P and ℓ matters.

In the first, we pick an arbitrary point in the middle of the set and a random line through it. The blade hits a nearby point, pivots, hits another nearby point, and quickly settles into a cycle among a handful of points. The rest of the set is never reached. The windmill has gotten trapped.

In the second, we pick a hull vertex with a supporting line. The blade must sweep across most of the set before it can hit anything, and the pivots are forced to spread out. This is the difference between a windmill that wanders and one that gets stuck.

The problem asks us to show that a good start exists. We don't have to find the best one, just one that works. And the supporting-line start is the natural candidate.

---

## PART 6: THE PROOF, RECAPPED IN PLAIN LANGUAGE

**[ON SCREEN: a numbered list appears, one item at a time.]**

**NARRATOR:**

Let me pull the threads together in plain language.

**One.** Pick a vertex P of the convex hull of S, and draw a supporting line ℓ through P. All other points lie on one side of it.

**Two.** Start the clockwise rotation. The blade sweeps and eventually hits a new point, which becomes the next pivot. Pivots now move inward and outward across the set.

**Three.** Because the blade rotates forever in one direction, every direction from every pivot is swept over and over. A point can only be skipped if it is shadowed from every pivot the windmill ever uses.

**Four.** Suppose some point X is skipped forever. Then the windmill is confined to a smaller and smaller part of the set. But the supporting-line start forbids that confinement. The pivots must keep reaching different regions, so eventually X is exposed.

**Five.** Therefore every point of S becomes a pivot infinitely many times.

**[ON SCREEN: the list is highlighted.]**

**NARRATOR:**

I want to emphasize step four, because it's the step most people miss. The argument isn't that the windmill visits each point once and then stops. It's that the windmill cannot ever settle into a loop that excludes a point. Any excluded point gets exposed eventually, and the process repeats forever.

For the rigorous version, with the precise inequalities and the careful handling of the case where the blade passes through several points at once, look at the official IMO solutions. The problem explicitly rules out three collinear points, and that assumption does real work: it guarantees the blade hits exactly one new point at each stage, so the pivot is always well defined.

---

## PART 7: WHY THIS PROBLEM IS SO SATISFYING

**[ON SCREEN: a shot of the moving windmill, looping across the set.]**

**NARRATOR:**

Here's what I find beautiful about this problem.

The statement looks like a game about spinning sticks. The solution uses something far more general: a convex hull, a supporting line, and an argument about how persistent motion must eventually reach every corner of a finite set.

It's also a lesson in choosing the right starting condition. Many hard problems become easy once you pick the right setup. Here, the choice of a hull vertex and supporting line does nearly all the work. Without it, the windmill traps itself. With it, the windmill can't help but explore everything.

And it's a reminder that "forever" in mathematics is a strong word. The problem asks for infinitely many visits, not just one. That single demand turns a puzzle about lines into a question about persistence and coverage.

---

## OUTRO

**[ON SCREEN: the windmill spins one last time, leaving a trail through every point.]**

**NARRATOR:**

So, to recap. We put a windmill on a convex set of points, we start it from a supporting line at a hull vertex, and we let it spin. Because it can't settle into a loop that skips anyone, every point of the set gets its turn, again and again, forever.

If you want to try it yourself, grab a sheet of paper, place about six or seven points with no three in a line, and sketch the windmill from a hull vertex. Watch how the pivots move. Try a random start too, and see how easily it gets trapped. That contrast is the whole lesson.

If you enjoyed this, let me know in the comments which step you'd like unpacked in a follow-up video. I'm happy to go deeper into the official proof, or to look at the other problems from the 2011 paper.

Thanks for watching. Keep spinning those ideas.

**[ON SCREEN: end card with subscribe prompt and links to the IMO 2011 problem sheet.]**

**[END]**
