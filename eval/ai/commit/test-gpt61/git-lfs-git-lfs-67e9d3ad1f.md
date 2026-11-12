lfs: use blobSizeCutoff in clean pointer buf test

When the clean filter receives an existing LFS pointer, it needs to
recognize that the input already represents an LFS object and preserve
the pointer contents. In copyToTemp(), this requires both successful
pointer decoding and a check that the buffered data contains the whole
input. A successfully decoded prefix alone is insufficient, since more
data may remain in the reader.

The length check still uses a literal limit of 512 bytes, although the
buffer used for this operation is sized using blobSizeCutoff, currently
1024 bytes. Replace the literal with blobSizeCutoff so the completeness
check agrees with the amount of data the function actually buffers.

The mismatch dates back to changes in pointer decoding. Originally,
DecodeFrom() used a 512-byte buffer, and the clean code checked against
that same boundary. The decoding buffer was subsequently enlarged, and
later changes moved the buffering into copyToTemp(), but the original
comparison survived those updates.

With the comparison aligned, a decoded pointer whose buffered contents
are shorter than blobSizeCutoff can follow the existing
CleanPointerError path, preserving its original bytes. [Source](https://github.com/git-lfs/git-lfs/pull/4433)

Using the named constant also makes the purpose of this condition easier
to understand. The relevant question is whether the read filled the
available buffer. A separate numeric threshold obscures that
relationship and requires maintainers to remember that two values must
be updated together. Expressing the comparison in terms of the buffer
limit keeps that dependency visible at the point where the decision is
made.

Retain the strict less-than comparison. Filling a bounded buffer does
not, by itself, establish that the reader has reached the end of its
input. Treating that case as complete would make the decision depend on
an assumption about data beyond the bytes already inspected. The
comparison should continue to distinguish a short read from a buffer
that may have additional input behind it.

This change therefore brings the existing condition back into agreement
with its underlying buffer allocation. It removes an outdated numeric
assumption and makes future changes to the cutoff easier to apply
consistently. The intended invariant is straightforward: the size used
to assess whether buffered input is complete should track the size used
to collect that input.
