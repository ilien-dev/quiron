Create a new type category for "internal use" types.

Introduce TYPCATEGORY_INTERNAL, represented by category code 'Z', for
types intended for internal use. Move "char" and special-purpose types
such as pg_node_tree out of the string category so they no longer
receive preferential treatment during implicit cast resolution. Use
'Z' because 'I' is already assigned to another category.

Historically, "char" has belonged to TYPCATEGORY_STRING despite storing
only a single byte and serving primarily as an enum-like catalog value.
Other internal types have inherited the same classification. However,
the string-category heuristics in parse_func.c and parse_coerce.c assume
that their targets can represent arbitrary text. Applying those rules
to restricted internal representations can select unexpected conversion
targets and produce surprising behavior.

Adjust the affected query in psql/describe.c to cast the catalog "char"
value explicitly to text before concatenating it with an untyped
literal. Update the citext regression case to request its conversion
to "char" explicitly, and revise the expected results accordingly.
These changes make the required conversions clear while preserving the
intended restriction on implicit target selection.

Document the new category, update the built-in catalog entries, and
bump the catalog version to reflect the changed metadata.

Reported by Ian Campbell.

Discussion: [original report and discussion](https://postgr.es/m/2216388.1638480141@sss.pgh.pa.us).
