bpo-38804: Fix REDoS in http.cookiejar (GH-17157)

The regex http.cookiejar.LOOSE_HTTP_DATE_RE was vulnerable to regular expression denial of service (REDoS). The pattern contained several adjacent `\s*` quantifiers, separated only by optional groups. When those optional groups do not match, the quantifiers sit next to each other, and the regex engine can split a single run of whitespace between them in many different ways.

On input that ultimately fails to match, the engine tries every one of those splits before giving up. A long sequence of spaces in a date string, such as one taken from an attacker-controlled Set-Cookie "expires" attribute or a similar header, therefore causes the running time to grow polynomially with the length of the input. A response of modest size could keep a client busy for a very long time, tying up a thread or process that parses cookies from untrusted servers.

The fix restructures the pattern so that each whitespace character can be consumed in only one way. Redundant `\s*` quantifiers are removed or merged into the groups that they trail. Because the match is anchored at both ends, the set of strings that the regex accepts is unchanged. Every date format that previously parsed, including those with an optional clock, a numeric or named timezone, or a parenthesized ASCII timezone, still parses to the same result. Only the backtracking behavior on non-matching input changes.

Tests

A regression test is added to test_http_cookiejar. It feeds the parser a string containing a long run of spaces that cannot match and checks that the call returns promptly with the expected result (no parsed date). Before the change, an input of this shape took a disproportionate amount of time. After the change it completes effectively instantly. The existing date-parsing tests in the same module continue to pass unmodified, which confirms that the accepted grammar was not altered.

Notes

- No public API changes. `http2time` and `loose_http_date`-style parsing keep their signatures and return values.
- A NEWS entry is added under Security so that downstream distributors can identify the fix for backporting to maintained branches.
- The same pattern of adjacent optional whitespace quantifiers was audited elsewhere in the module. No other expression was found to have the same problem.

Reported at https://bugs.python.org/issue38804.

Patch by Anthony Sottile.
