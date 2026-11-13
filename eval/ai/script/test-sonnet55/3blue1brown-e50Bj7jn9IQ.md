# A quick trick for computing eigenvalues
### Chapter 15, Essence of linear algebra

**[Format: narration in plain text, visual directions in brackets. Target runtime is about 15 to 16 minutes.]**

---

## COLD OPEN (~200 words)

**[Visual: A 2x2 matrix [[3, 1], [4, 1]] appears. The usual machinery slides in: the det(A − λI) expression, a quadratic, the quadratic formula. It all looks heavy.]**

Suppose I hand you a two-by-two matrix and ask for its eigenvalues. If you've taken a linear algebra course, you know the routine. Subtract lambda from the diagonal, take the determinant, get a quadratic polynomial, and then solve it with the quadratic formula.

It works, and I'm not going to pretend otherwise. But if you do this a lot, in physics, in differential equations, or in a stats class, you start to notice that it's slow. Worse, it hides the structure of what's happening. You grind through the algebra and come out the other side with two numbers and no feeling for where they came from.

**[Visual: The machinery fades. Three short lines appear: "Sum of eigenvalues," "Product of eigenvalues," "A formula."]**

There's a much faster way to do it, one you can often carry out in your head. It relies on three facts, and each of them is something you can actually understand rather than memorize.

If you haven't watched the chapter on eigenvectors and eigenvalues, I'd suggest starting there. But I'll give a quick refresher, because the whole trick depends on seeing eigenvalues the right way.

---

## REFRESHER (~250 words)

**[Visual: The plane with grid lines. A matrix transformation is applied. Most vectors get knocked off their spans. One special vector stays on its line.]**

When a matrix transforms space, most vectors get knocked off the line they started on. But some special vectors stay on their own span. They only get stretched or squished, as if the transformation were just multiplication by a number.

**[Visual: Highlight an eigenvector, scale it by 2. Label: "λ = 2".]**

Those vectors are the eigenvectors, and the factor by which each is stretched is its eigenvalue. In symbols, A times v equals lambda times v.

**[Visual: Show the equation Av = λv, then rearrange to (A − λI)v = 0.]**

The standard way to find them is to rewrite this as (A minus lambda times the identity) times v equals zero. We want a nonzero vector v that gets sent to zero. That can only happen if the matrix A minus lambda I squishes space into a lower dimension, which means its determinant is zero.

**[Visual: Show the 2x2 matrix [[a − λ, b], [c, d − λ]] and expand the determinant.]**

So we expand that determinant. For a general matrix with entries a, b, c, d, we get lambda squared, minus (a plus d) times lambda, plus (ad minus bc), and we set it equal to zero.

Hold on to that expression for a moment. It's about to tell us something.

---

## FACT 1: THE TRACE (~380 words)

**[Visual: The polynomial λ² − (a + d)λ + (ad − bc) = 0. Highlight (a + d) in one color and (ad − bc) in another.]**

Look at the coefficients. The one in front of lambda is the sum of the diagonal entries, a plus d. That sum has a name, the **trace** of the matrix.

Now think about what the roots of a quadratic look like. If a quadratic has roots lambda one and lambda two, it factors as (λ minus λ₁)(λ minus λ₂). Multiply that out and you get lambda squared, minus the sum of the roots times lambda, plus the product of the roots.

**[Visual: Side-by-side expansion of (λ − λ₁)(λ − λ₂) next to the characteristic polynomial. Matching terms light up.]**

Matching the two expressions gives us the first fact. **The sum of the eigenvalues equals the trace.** Equivalently, the *mean* of the two eigenvalues equals the mean of the diagonal entries.

**[Visual: Matrix [[8, 4], [2, 6]]. Diagonal entries 8 and 6 highlighted. Mean: 7. Number line with a point at 7.]**

Take the matrix with 8 and 6 on the diagonal. Their mean is 7, so we immediately know the two eigenvalues average to 7. We haven't computed anything yet and already we know where they're centered.

Now, I'll admit the polynomial argument is a bit of a cheat, since it proves the fact without explaining it. Is there a reason you'd expect this to be true?

**[Visual: Show a diagonal matrix [[λ₁, 0], [0, λ₂]], where the diagonal entries are obviously the eigenvalues.]**

Here's one way to see it. When a matrix has two independent eigenvectors, you can change your coordinate system so those eigenvectors become the basis. In that system the matrix is diagonal, with the eigenvalues sitting on the diagonal, so the trace is plainly their sum.

**[Visual: Show a change of basis: A → P⁻¹AP. The text "trace unchanged" appears.]**

The remaining piece is that changing basis doesn't change the trace. Computing the trace of P inverse times A times P, you can cycle the matrices around inside the trace, and the P's cancel. I'll leave that as a short exercise. The takeaway is that the trace is a property of the transformation itself, not of the coordinates you happen to use.

So fact one: the mean of the eigenvalues is the mean of the diagonal entries. I'll call that mean **m**.

---

## FACT 2: THE DETERMINANT (~330 words)

**[Visual: Unit square in the plane transforms into a parallelogram. The area is labeled "det(A)".]**

The second fact is one you may already know. The determinant tells you how much a transformation scales areas.

**[Visual: Return to the characteristic polynomial and highlight the constant term (ad − bc).]**

And look back at the polynomial. The constant term, ad minus bc, is the determinant. Matching with the factored form, the constant term is also the product of the two roots.

So fact two: **the product of the eigenvalues equals the determinant.** I'll call that product **p**.

**[Visual: An eigenvector basis grid. The unit square built from the two eigenvectors gets stretched by λ₁ along one direction and λ₂ along the other. The area scales by λ₁ × λ₂.]**

This one has a clean geometric reading. Imagine a parallelogram built from the two eigenvectors. The transformation stretches one side by lambda one and the other by lambda two, so the area gets multiplied by their product. And since the determinant is exactly the area scaling factor, the two must agree.

**[Visual: Matrix [[8, 4], [2, 6]]. Compute det: 8·6 − 4·2 = 40. Label p = 40.]**

For our example, 8 times 6 is 48, minus 4 times 2 which is 8, gives 40. So the eigenvalues multiply to 40.

Now we're in an interesting position. We know two eigenvalues that average to 7 and multiply to 40. You might already be able to guess them. But in general there's a formula that gets us there with no guessing.

---

## FACT 3: THE FORMULA (~480 words)

**[Visual: A number line. A point at m. Two points symmetric around it, at m − d and m + d, with a bracket labeled "d" on each side.]**

Here's the key idea. Two numbers whose mean is m must sit at equal distances on either side of m. So we can write them as m plus d and m minus d, for some unknown distance d.

**[Visual: Write (m + d)(m − d) = m² − d² = p.]**

We also know their product. Multiply (m plus d) by (m minus d) and you get the difference of squares, m squared minus d squared. That must equal p.

**[Visual: Rearrange: d² = m² − p, so d = √(m² − p).]**

Solving for d gives d squared equals m squared minus p. So d is the square root of m squared minus p.

**[Visual: Large formula on screen: λ = m ± √(m² − p).]**

That's the whole formula. **The eigenvalues are m plus or minus the square root of (m squared minus p).**

Notice this is just the quadratic formula in disguise. But written in terms of the mean and the product, it's much friendlier. You never touch the lambda polynomial at all, and there's no negative b to forget about.

**[Visual: Matrix [[8, 4], [2, 6]]. m = 7, p = 40. Compute: 7² = 49, 49 − 40 = 9, √9 = 3. Eigenvalues: 7 ± 3 = 10 and 4.]**

Let's run it on our example. The mean m is 7. The product p is 40. Seven squared is 49, minus 40 is 9, and the square root of 9 is 3. So the eigenvalues are 7 plus 3 and 7 minus 3, which gives 10 and 4.

**[Visual: Verify: 10 + 4 = 14 = 8 + 6 ✓. 10 × 4 = 40 ✓.]**

That took about five seconds, and we can sanity-check it right away. Ten plus four is 14, matching the trace. Ten times four is 40, matching the determinant.

**[Visual: Matrix [[3, 1], [4, 1]]. m = 2, p = 3·1 − 1·4 = −1.]**

Let's try one that isn't so tidy. Take the matrix with rows (3, 1) and (4, 1). The diagonal is 3 and 1, so the mean is 2. The determinant is 3 minus 4, which is negative 1.

**[Visual: Compute: 2² − (−1) = 5. λ = 2 ± √5.]**

Then m squared minus p is 4 minus negative 1, which is 5. So the eigenvalues are 2 plus or minus the square root of 5, roughly 4.24 and negative 0.24.

If you'd run the standard approach, you'd have set up a polynomial, written out the discriminant, and probably made a sign error somewhere along the way. Here the whole computation is three small steps: find the mean, find the product, plug in.

---

## A SECOND LOOK AT WHY IT WORKS (~250 words)

**[Visual: Slow zoom on the number line with m, and d appearing as a "radius" of a circle around m.]**

I want to pause on the structure here, because it's what makes this more than a computational shortcut.

The mean m tells you where the eigenvalues are centered. The quantity under the square root, m squared minus p, tells you how far apart they are. If that quantity is large and positive, the eigenvalues are far apart. If it's zero, the two eigenvalues land on top of each other.

**[Visual: Shear matrix [[1, 1], [0, 1]]. m = 1, p = 1, m² − p = 0. A single point at 1 with a double marker.]**

A shear is the classic example. The matrix with rows (1, 1) and (0, 1) has mean 1 and determinant 1. So m squared minus p is zero, and the single eigenvalue 1 shows up twice. The formula tells you about this degenerate case without any extra work.

**[Visual: Negative number under the root. The number line gets a vertical imaginary axis, and the two eigenvalues appear as a conjugate pair.]**

And if m squared minus p is *negative*, the square root is imaginary, and the eigenvalues come out as a complex conjugate pair, with real part m.

---

## THE ROTATION EXAMPLE (~250 words)

**[Visual: Rotation by 90 degrees. The matrix [[0, −1], [1, 0]]. Every vector turns, none stay on their span.]**

This is exactly what should happen for a rotation. Take the matrix that rotates the plane by 90 degrees, with rows (0, negative 1) and (1, 0). No real vector stays on its own line when you rotate it, so there are no real eigenvectors.

**[Visual: Compute: m = 0, p = 0·0 − (−1)(1) = 1.]**

Let's see what the formula says. The diagonal entries are both 0, so the mean is 0. The determinant is 0 times 0 minus negative 1 times 1, which is 1.

**[Visual: Compute: m² − p = −1. λ = 0 ± √(−1) = ±i.]**

So m squared minus p is negative 1, and the eigenvalues are plus and minus i. Pure imaginary, centered at zero, exactly as you'd expect from a transformation that rotates without stretching.

**[Visual: General rotation-scaling matrix [[a, −b], [b, a]]. m = a, p = a² + b². λ = a ± bi.]**

You can push this further. A matrix of the form (a, negative b) over (b, a) is a rotation combined with a scaling. Its mean is a and its determinant is a squared plus b squared, so the formula gives lambda equals a plus or minus b times i. The real part controls the scaling and the imaginary part controls the rotation.

---

## A BEAUTIFUL EXAMPLE: THE GOLDEN RATIO (~230 words)

**[Visual: Fibonacci numbers 1, 1, 2, 3, 5, 8, 13... and the matrix [[1, 1], [1, 0]].]**

Here's one more, because it's too good to skip. The matrix with rows (1, 1) and (1, 0) is the one that generates the Fibonacci numbers. Each time you apply it to a pair of consecutive Fibonacci numbers, you get the next pair.

**[Visual: m = 1/2, p = 0 − 1 = −1.]**

The diagonal entries are 1 and 0, so the mean is one half. The determinant is 0 minus 1, which is negative 1.

**[Visual: m² − p = 1/4 + 1 = 5/4. √(5/4) = √5/2. λ = 1/2 ± √5/2.]**

Then m squared minus p is one quarter plus one, or five quarters. The square root of five quarters is root five over two. So the eigenvalues are one half plus or minus root five over two.

**[Visual: Highlight (1 + √5)/2 ≈ 1.618, labeled "the golden ratio". The Fibonacci ratios converge toward it.]**

That's the golden ratio, along with its conjugate. And now you can see *why* the ratio of consecutive Fibonacci numbers converges to it. Applying the matrix over and over amplifies the component along the larger eigenvector, whose eigenvalue is 1.618, until that component dominates everything else. Just by averaging two diagonal entries and computing a determinant, we found one of the most famous numbers in mathematics.

---

## A QUICK CAUTION (~120 words)

**[Visual: A 3x3 matrix appears with a question mark over it.]**

Before the recap, a caution. Everything here is specific to two-by-two matrices. The sum and product facts have analogues in higher dimensions: the trace is always the sum of the eigenvalues, and the determinant is always their product. But with three or more eigenvalues, knowing those two facts isn't enough to pin them down, and there's no tidy formula like the one we just built.

For larger matrices, you'd reach for other tools. But the two-by-two case comes up so often that having this trick in your back pocket is worth it.

---

## RECAP AND CLOSING (~250 words)

**[Visual: The three facts stacked on screen, one at a time.]**

Let's gather everything together. For a two-by-two matrix:

First, the mean of the eigenvalues equals the mean of the diagonal entries. Call it m.

Second, the product of the eigenvalues equals the determinant. Call it p.

Third, the eigenvalues are m plus or minus the square root of m squared minus p.

**[Visual: A worked example runs in fast-forward: a random matrix, mean, determinant, formula, answer, all in a few seconds.]**

With a little practice, you can do this almost instantly. Find the mean of the diagonal, find the determinant, and plug them in. No polynomial, no expanding, no solving.

**[Visual: Return to the original opening: the heavy machinery of det(A − λI). It now looks like a detour.]**

What I like most about this approach isn't the speed, though. It's that each step means something. The mean tells you where the eigenvalues are centered, the determinant tells you how areas scale, and the square root tells you how far apart the eigenvalues are spread. Instead of turning a crank, you're reading off the geometry of the transformation.

**[Visual: The number line one last time, with m at the center and the two eigenvalues symmetric on either side.]**

If you want to practice, try making up your own matrices and finding their eigenvalues in your head. Start with ones where m squared minus p is a perfect square, then try ones where it isn't, and then try ones where it's negative. After a few rounds you'll start to see the pattern.

Thanks for watching.

**[END]**

---

*Approximate word count: 2,400, including visual directions.*
