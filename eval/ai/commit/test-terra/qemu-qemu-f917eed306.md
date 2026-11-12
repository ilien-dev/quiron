qobject: Fix qnum_to_string() to use sufficient precision

qnum_to_string() formats floating-point QNums with %f and its default
precision of six digits after the decimal point.  This can discard
significant information: converting a double to a string and parsing
the string again may produce a different value.  Small values can even
be rounded to zero.

QNum strings are used when producing JSON, so the loss can be visible
in data sent to clients.  For example, a QAPI number in QMP or guest
agent output can differ from the value QEMU intended to report.  The
problem is not limited to values with many decimal places; the fixed
number of fractional digits also gives very small values too few
significant digits.

Format doubles with enough significant decimal digits to preserve their
value across a conversion to text and back.  Use 17 digits, the
DBL_DECIMAL_DIG precision for the double representation used here, with
a general floating-point format.  This allows the output to use
scientific notation where appropriate and avoids the limitations of a
fixed number of digits after the decimal point.

The resulting strings can be longer or less familiar for values whose
binary representation is only an approximation of a short decimal
fraction.  That is an intentional consequence of preserving the
underlying double.  JSON consumers must already accept both fractional
and exponent notation for numbers, so the representation remains valid
JSON.

Update the affected JSON conversion expectations to reflect the
additional precision.  Together with the existing QNum conversion
coverage, these checks exercise the text emitted for floating-point
values and guard against returning to the previous six-digit
formatting.

Integer QNums continue to use their existing conversion paths.  The
change applies to floating-point output, where decimal formatting must
retain enough information for a receiver to recover the original
value.
