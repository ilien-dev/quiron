I've written `README.md` in the working directory. It runs to about 1,250 words of prose plus code samples and tables.

The flag names, defaults, endpoint behaviour and Docker image name (`tarent/loginsrv`) come from what I know of the existing open-source loginsrv. This directory has no source code, so I couldn't check any of them against your build. Please check these before publishing:

- **Defaults:** the default port (`6789`, though the Quick Start uses `8080`), the JWT algorithm (`HS512`), and the cookie defaults.
- **Backend options:** the parameter strings for each backend and OAuth2 provider.
- **User file:** the YAML format for `-user-file`.
- **Contributing:** the Go interface name `login.Backend`.
- **License:** I said MIT; change it if yours is different.

The README covers:

- **Overview and How It Works:** the login → backend → JWT → downstream verification flow.
- **Installation:** Docker, `go install`, and prebuilt binaries, followed by a curl-based Quick Start.
- **Configuration:** a table of flags, plus how they map to `LOGINSRV_*` environment variables.
- **Backends:** Simple, htpasswd, OSIAM and HTTP upstream.
- **OAuth2 providers:** GitHub, Google, Bitbucket, Facebook and GitLab, with a user-file example for restricting logins and adding claims.
- **API:** `GET`/`POST`/`DELETE /login`, how the `Accept` header changes the response, token refresh, and logout.
- **Templating, Security, Contributing and License.**
