# The quick proof of Bayes' theorem

**[COLD OPEN: formula on screen]**

Bayes' theorem has a reputation. It runs spam filters, medical tests, and half of machine learning, and it's usually handed to you as a formula to memorize.

But the proof is two lines long. If you know what conditional probability means, you already know Bayes' theorem. You just haven't noticed yet.

**[ON SCREEN: P(A|B) = P(B|A) · P(A) / P(B)]**

Here's the claim: the probability of A given B equals the probability of B given A, times the probability of A, divided by the probability of B.

Let's prove it.

**[SECTION 1: The one ingredient]**

We need exactly one definition.

**[ANIMATION: rectangle containing two overlapping circles, A and B]**

Picture a rectangle holding everything that could possibly happen. Inside it are two overlapping circles: event A and event B.

Now I tell you that B happened. Your world shrinks to the B circle, and everything outside it is gone. The only way A can still be true is if you're in the overlap.

So the probability of A given B is the overlap, as a fraction of B.

**[ON SCREEN: P(A|B) = P(A and B) / P(B)]**

That's the definition of conditional probability, and it's the only idea in this video.

**[SECTION 2: The proof]**

Multiply both sides by P(B).

**[ON SCREEN: P(A and B) = P(A|B) · P(B)]**

The probability of both happening is the probability of B, times the probability of A once you know B.

The definition never cared which circle we called A and which we called B. So run the same argument with the names swapped.

**[ON SCREEN: P(A and B) = P(B|A) · P(A)]**

Now look at the left-hand sides. "A and B" is the same region as "B and A". We've measured the same overlap in two different ways, so the two right-hand sides must be equal.

**[ON SCREEN: P(A|B) · P(B) = P(B|A) · P(A)]**

Divide by P(B).

**[ON SCREEN: P(A|B) = P(B|A) · P(A) / P(B)]**

Done. That's Bayes' theorem.

**[SECTION 3: Why something this simple matters]**

So why is a two-line fact so famous?

Because P(A given B) and P(B given A) are different numbers, and people mix them up constantly.

**[ON SCREEN: 1,000 stick figures]**

Take a disease that affects 1 percent of people. There's a test that catches 90 percent of real cases, but it also gives a false positive 9 percent of the time.

You test positive. What's the chance you're actually sick?

Most people say 90 percent. Let's count instead.

Out of 1,000 people, 10 have the disease, and 9 of them test positive.

**[ANIMATION: 9 figures turn red]**

The other 990 are healthy, but 9 percent of them test positive anyway. That's about 89 people.

**[ANIMATION: 89 figures turn orange]**

So there are 98 positive tests, and only 9 belong to sick people. Your chance of having the disease is about 9 percent, not 90.

That calculation is Bayes' theorem. The 90 percent is the probability of a positive test given that you're sick. What you wanted was the probability that you're sick given a positive test. To flip one into the other, you multiply by how common the disease is and divide by how common positive tests are.

**[ON SCREEN: formula with each term labeled]**

The 9 sick positives are the numerator. The 98 total positives are the denominator. It's the same overlap, divided by a different circle.

**[OUTRO]**

So that's the quick proof: write the overlap two ways, set them equal, and divide.

The formula was never the hard part. The hard part is remembering that "A given B" and "B given A" are different questions, and Bayes' theorem is the bridge between them.

Thanks for watching, and I'll see you in the next one.
