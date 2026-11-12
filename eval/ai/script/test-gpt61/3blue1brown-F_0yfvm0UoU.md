# e to the pi i, a nontraditional take (old version)

[Opening shot: a blank screen. Five symbols appear, one at a time.]

**e. i. Pi. One. Zero.**

There’s a famous equation connecting these five numbers:

\[
e^{i\pi}+1=0.
\]

People call it beautiful. Sometimes they call it the most beautiful equation in mathematics.

But if you’ve never seen where it comes from, that praise might feel a little premature.

What does it even mean to raise a number to an imaginary power? Why should pi show up? And how does any of this produce negative one?

Usually, the explanation begins with infinite series.

Today, I want to begin with motion.

[An arrow appears, pointing right from the origin.]

Imagine an arrow whose tail stays fixed at the origin. Its tip can move around the plane.

We’ll describe that arrow with a complex number.

If complex numbers feel mysterious, think of them as a convenient notation for two-dimensional positions. The number \(a+bi\) means: move \(a\) units horizontally and \(b\) units vertically.

The special number \(i\) sits one unit above the origin.

But complex numbers aren’t just positions. You can multiply them, and that multiplication has a geometric meaning.

In particular, multiplying by \(i\) rotates an arrow ninety degrees counterclockwise.

[The arrow rotates through four quarter-turns.]

One becomes \(i\). Then \(i\) becomes negative one. Negative one becomes negative \(i\). And negative \(i\) becomes one again.

Four turns bring us home.

The familiar rule \(i^2=-1\) is what happens after two quarter-turns.

Now let’s use that rotation to describe movement.

Suppose our arrow starts at the number one. Its tip is at the point \((1,0)\).

And suppose we give it this instruction:

At every instant, move in the direction obtained by rotating your current position ninety degrees counterclockwise.

More precisely, let its velocity equal \(i\) times its position.

If the position is \(z(t)\), the rule is

\[
z'(t)=iz(t).
\]

Don’t worry if differential equations aren’t familiar. This equation just says that the arrow describing velocity is the position arrow, turned ninety degrees.

[At several points, a small velocity arrow appears perpendicular to the position arrow.]

At the starting point, the position points right, so the velocity points up.

A little later, the position points slightly upward, so the velocity points slightly left of vertical.

The direction of motion keeps changing.

What path does that create?

A circle.

Here’s why. The velocity is always perpendicular to the position. It has no component pointing outward or inward, so the distance from the origin doesn’t change.

We started one unit from the origin. We stay one unit from the origin.

And because multiplying by \(i\) preserves length, the speed is also one.

So this rule describes a point traveling counterclockwise around the unit circle at one unit of distance per unit of time.

That’s the geometric side of the story.

Now let’s approach the same motion from somewhere that initially seems unrelated: compound interest.

[Cut to the expression \(e^t\).]

The exponential function is special because its rate of change equals its current value:

\[
\frac{d}{dt}e^t=e^t.
\]

If you have twice as much, you grow twice as fast.

More generally, \(e^{at}\) changes at a rate equal to \(a\) times its current value.

For positive real \(a\), that means growth. For negative real \(a\), it means decay.

So what should happen if we replace \(a\) with \(i\)?

We would want

\[
\frac{d}{dt}e^{it}=ie^{it}.
\]

But that’s exactly the motion rule we just explored.

Its velocity is its position, multiplied by \(i\).

This suggests that \(e^{it}\) should describe circular motion.

There is, however, a small logical trap here.

We already understand real exponents. We haven’t yet explained what an imaginary exponent means. We can’t simply assume all the old rules still work and declare victory.

We need a definition that earns those rules.

One way to do that is to build the exponential from many tiny steps.

For real numbers, the exponential satisfies

\[
e^t=\lim_{n\to\infty}\left(1+\frac{t}{n}\right)^n.
\]

That’s continuous compounding: divide the growth into smaller and smaller stages.

Let’s try the same construction with \(it\):

\[
\lim_{n\to\infty}\left(1+\frac{it}{n}\right)^n.
\]

What does each multiplication do?

[Zoom in on the complex number \(1+it/n\).]

The number \(1+it/n\) points mostly right, with a tiny upward component.

Multiplying by it produces a small counterclockwise rotation, together with a small increase in length.

Repeat that multiplication \(n\) times, and you get a chain of little turns.

At first, you might expect the outward stretching to spoil the circle.

But the stretch and the turn behave differently as the steps get smaller.

Set \(h=t/n\). The length of \(1+ih\) is

\[
\sqrt{1+h^2}.
\]

Its departure from one is on the scale of \(h^2\), while its angle is approximately \(h\).

That distinction matters.

Across \(n\) steps, the total turning approaches \(t\), because \(nh=t\).

Meanwhile, the accumulated stretching disappears. Its scale is \(nh^2=t^2/n\), which approaches zero.

[The successive paths approach the unit circle.]

In the limit, we get pure rotation.

This construction gives a concrete meaning to \(e^{it}\): start at one, then rotate counterclockwise through an angle of \(t\) radians.

And radians are precisely the angle measurement that makes this work naturally.

On a unit circle, an angle of \(t\) radians corresponds to an arc length of \(t\).

Since our point moves at speed one, after time \(t\), it has traveled through angle \(t\).

Its horizontal coordinate is therefore \(\cos t\), and its vertical coordinate is \(\sin t\).

So we arrive at

\[
e^{it}=\cos t+i\sin t.
\]

This is Euler’s formula.

Notice what it says: exponential growth and circular motion belong to the same mathematical family.

A real multiplier in the rate equation produces growth or decay. An imaginary multiplier turns that changing direction sideways, producing rotation.

Now we can finally substitute pi.

[The point travels halfway around the circle.]

A full trip around the unit circle has length \(2\pi\).

After time \(\pi\), our point has completed half a trip. It started at one and arrived at negative one.

Therefore,

\[
e^{i\pi}=-1.
\]

Move everything to one side, and we get the famous identity:

\[
e^{i\pi}+1=0.
\]

The surprising part is how naturally the ingredients meet. The exponential describes change proportional to the current state. Multiplication by \(i\) turns that change perpendicular. Pi measures the half-circle that carries one to negative one.

Five familiar numbers appear in one equation because growth, rotation, and geometry fit together.

And that connection is the beauty.
