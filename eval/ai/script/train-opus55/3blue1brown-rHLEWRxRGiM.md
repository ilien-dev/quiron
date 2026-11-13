# Three-Dimensional Linear Transformations | Chapter 5, Essence of Linear Algebra

*[Opening: a 3D coordinate grid slowly rotates on screen]*

**NARRATOR:**
So far in this series, we've lived on a flat plane. We've watched grids stretch, rotate, and shear, and we've seen that every one of those motions can be captured by a small grid of numbers called a matrix. The good news is that almost nothing we've built depends on staying in two dimensions. Everything carries over to three dimensions with only small changes. In this short chapter, we'll make that jump.

*[The flat grid lifts off the page and gains depth]*

Let's start with the space itself. In three dimensions, every vector has three coordinates. Picture an arrow starting at the origin and ending at a point floating in space. The first coordinate tells you how far to move along the x-axis, the second along the y-axis, and the third along the new z-axis, pointing up out of the old flat world.

Just as before, we have basis vectors. Alongside **i-hat**, the unit vector along x, and **j-hat**, along y, we now add **k-hat**, a unit vector pointing along z. Any vector in space is some combination of these three: a certain amount of i-hat, plus a certain amount of j-hat, plus a certain amount of k-hat.

*[Three colored arrows appear: green, red, blue]*

Now, what does a *linear* transformation look like in 3D? Think of it as a motion that takes every point in space and moves it somewhere else, while following two rules. First, the origin stays fixed. Second, grid lines stay parallel and evenly spaced. Imagine a lattice of cubes filling all of space. After a linear transformation, those cubes might be tilted, squashed, or stretched into slanted boxes, but they all stay identical to each other, and the lattice never bends or curves.

*[The cube lattice morphs smoothly into a sheared, rotated lattice]*

Here's the key idea, the same one from two dimensions: **you only need to track the basis vectors.** If you know where i-hat, j-hat, and k-hat land, you know where *every* vector lands.

Why? Take any vector, say, two parts i-hat, one part j-hat, and three parts k-hat. Because the transformation keeps grid lines parallel and evenly spaced, that vector ends up as the same combination of the *transformed* basis vectors: two times wherever i-hat went, plus one times wherever j-hat went, plus three times wherever k-hat went.

*[The vector is assembled tip-to-tail from scaled copies of the new basis vectors]*

So we record that information. Each transformed basis vector has three coordinates. Write the new i-hat as the first column, the new j-hat as the second column, and the new k-hat as the third. What you get is a three-by-three matrix: nine numbers that fully describe the transformation.

*[A 3×3 matrix appears, each column color-coded to match its basis vector]*

To apply that matrix to a vector, you do exactly what we just described. Multiply the first column by the vector's first coordinate, the second column by its second, and the third column by its third, then add the results. That's matrix-vector multiplication. It isn't an arbitrary rule. It's the bookkeeping for "same combination, new basis vectors."

Let's look at an example. Suppose we rotate all of space by ninety degrees around the y-axis. i-hat, which pointed along x, swings around to point along negative z. j-hat sits on the axis of rotation, so it doesn't move. k-hat swings down to point along x. Put those landing spots into columns, and you've written the rotation as a matrix.

*[The rotation plays out, with the matrix filling in column by column]*

This idea matters well beyond the abstract. Computer graphics, robotics, physics simulations, and 3D modeling software all describe orientation and motion this way. Every time a game character turns their head, a three-by-three matrix like this is probably working behind the scenes.

Finally, composition works just like it did in 2D. If you apply one transformation and then another, the combined effect is still a linear transformation, so it has its own matrix. To find it, follow the basis vectors through both steps, or equivalently, multiply the two matrices. Reading right to left, the product tells you: first do this, then do that. And to compute each column of the product, you apply the left matrix to each column of the right one.

*[Two transformations play in sequence, then merge into one]*

I'd encourage you to try this yourself. Pick two simple transformations, like a rotation and a stretch along one axis, then figure out the product both geometrically and numerically. When the two answers match, the picture really sticks.

In the next chapter, we'll ask a natural question: when a transformation stretches or squishes space, *by how much* does volume change? That leads us to the determinant.

*[Fade out on the transformed lattice]*

---

*Word count: ~700*
