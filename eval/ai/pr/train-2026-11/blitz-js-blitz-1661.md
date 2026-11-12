This major change adds support for Prisma 2.13+ by removing the `blitz db` command wrappers, except for `blitz db seed`, and using the Prisma CLI directly for database workflows.

Applications should migrate database commands in package scripts, documentation, CI configuration, and local development workflows to their Prisma CLI equivalents. For example, use `prisma migrate` instead of `blitz db migrate`, `prisma introspect` instead of `blitz db introspect`, and `prisma studio` instead of `blitz db studio`. The `blitz db seed` command remains available for running application seed scripts.

Using Prisma directly gives developers access to its CLI commands and options without requiring Blitz to maintain matching wrappers. It also makes Prisma’s own documentation applicable when working with databases in Blitz applications.

This is a breaking CLI change: existing scripts that invoke removed `blitz db` commands must be updated. Review database setup, migration, introspection, and Studio workflows when upgrading, while retaining existing seed command usage.
