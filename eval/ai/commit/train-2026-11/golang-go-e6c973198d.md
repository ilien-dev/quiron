[dev.regabi] cmd/compile: stop mangling SelectorExpr.Sel for ODOTMETH

ODOTMETH currently differs from other SelectorExpr operations by replacing
Sel's original identifier, such as "Foo", with the qualified method
symbol, such as "pkg.Type.Foo". Most consumers need the original
identifier, so this transformation forces compiler code to recover it
from the mangled name.

Preserve the original selector symbol for ODOTMETH. Update the few
consumers that require the qualified method symbol to obtain it through
ir.MethodExprName(n).Sym(), or equivalently
ir.MethodExprName(n).Func.Sym(). This makes selector formatting simpler
and lets method-value wrapper construction use the selector's existing
method selection directly, including its declaration position.

Historically, parts of the backend have used types.Sym where an ir.Name
or ir.Func would better represent the selected function. Consequently,
there is some risk in removing Sel's ability to uniquely identify the
called method. CL 280294, which desugars OCALLMETH into OCALLFUNC, should
substantially reduce that risk: ODOTMETH expressions are now eliminated
earlier in compilation, before reaching those backend paths.

The resulting representation keeps the selected identifier available
consistently while making consumers request the method's function symbol
explicitly when needed.

Passes toolstash -cmp.

[Source](https://go.googlesource.com/go/+/e6c973198d9f8e68e4dce8637e2d1492032ce939)
