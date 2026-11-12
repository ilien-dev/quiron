deps: various quic patches from akamai/openssl

Node.js is working toward experimental support for the QUIC transport
protocol. QUIC requires a TLS 1.3 implementation that exposes the
handshake to the QUIC layer, so that the transport can carry the TLS
messages itself in CRYPTO frames and manage packet protection keys
directly. TLS records are never used. Upstream OpenSSL 1.1.1 does not
provide such an API, and there is no indication that it will be
backported to the 1.1.1 LTS series.

To unblock this work, this commit applies the QUIC patch set maintained
by Akamai in the akamai/openssl fork (branch OpenSSL_1_1_1-quic) on top
of the OpenSSL version currently vendored in deps/openssl. The patches
implement an API that closely mirrors the one already shipped by
BoringSSL. That API is what existing QUIC stacks, including ngtcp2,
already target. Keeping that compatibility lets Node.js build on ngtcp2
and nghttp3 without carrying a separate TLS backend.

The patch set adds the following public API:

  * SSL_CTX_set_quic_method() and SSL_set_quic_method(), which register
    the callbacks used to install read and write secrets, deliver
    outgoing handshake data, flush, and report alerts.
  * SSL_provide_quic_data(), used to feed received CRYPTO frame data
    into the handshake at a given encryption level.
  * SSL_process_quic_post_handshake(), for processing post-handshake
    messages such as NewSessionTicket.
  * SSL_quic_read_level() and SSL_quic_write_level(), which report the
    current OSSL_ENCRYPTION_LEVEL (initial, early data, handshake and
    application).
  * SSL_set_quic_transport_params() and
    SSL_get_peer_quic_transport_params(), which send and receive the
    quic_transport_parameters TLS extension.
  * SSL_quic_max_handshake_flight_len(), SSL_is_quic() and
    SSL_set_quic_early_data_enabled().

The patches also change libssl's behavior when a QUIC method is
installed, as the QUIC-TLS specification requires:

  * Only TLS 1.3 may be negotiated.
  * Middlebox compatibility mode is disabled, so no dummy
    ChangeCipherSpec messages are sent.
  * EndOfEarlyData messages are not sent.
  * KeyUpdate messages are rejected, because QUIC handles key updates
    itself.
  * The quic_transport_parameters extension is required, and its
    absence is reported as a missing_extension alert.

None of this changes behavior for connections that do not opt in to
QUIC. All new code is guarded by OPENSSL_NO_QUIC. The existing
tls/https/crypto surface in Node.js is unaffected, and nothing in lib/
uses the new API yet. A follow-up change will wire it into an
experimental, build-flag-gated QUIC implementation.

The architecture-specific configuration files and generated headers
under deps/openssl/config/archs have been regenerated with
`make -C deps/openssl/config` so that the new symbols and the
OPENSSL_NO_QUIC define are consistent on every supported platform.

Maintenance note: these patches are not part of upstream OpenSSL. They
have to be reapplied, or replaced with the matching akamai/openssl
release, every time the vendored OpenSSL is updated. When the upgrade
path in doc/guides/maintaining-openssl.md is followed, take the source
tarball from the corresponding OpenSSL_1_1_1x-quic tag instead of the
plain upstream release, or cherry-pick the QUIC commits on top of it.
Then regenerate the arch files as usual. Distributions that build
Node.js against a shared system OpenSSL will not have this API. The
QUIC support has to stay optional and must be detected at configure
time.

Refs: https://github.com/akamai/openssl/tree/OpenSSL_1_1_1-quic
Refs: https://datatracker.ietf.org/doc/html/draft-ietf-quic-tls
PR-URL: <PR URL>
Reviewed-By: <reviewer>
