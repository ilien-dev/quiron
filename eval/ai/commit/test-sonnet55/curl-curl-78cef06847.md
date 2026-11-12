openssl: Revert to less sensitivity for SYSCALL errors

A recent change made the OpenSSL backend treat every SSL_ERROR_SYSCALL result as a hard failure, regardless of the circumstances. The intent was to stop transfers from silently succeeding when the connection had been cut short, but in practice it turned out to be too strict.

Many servers and middleboxes close the TCP connection without sending a TLS close_notify alert. OpenSSL reports this as SSL_ERROR_SYSCALL with errno set to zero and an empty error queue. For transfers where the end of the body is already known, for example through Content-Length or chunked encoding, this is harmless. Treating it as an error caused otherwise complete transfers to fail with "SSL_read: Connection reset by peer" or "OpenSSL SSL_read: SSL_ERROR_SYSCALL, errno 0", which is a regression for users who had been working fine against such servers.

This change restores the earlier behavior. When SSL_ERROR_SYSCALL is returned and there is no errno and nothing on the OpenSSL error queue, the condition is handled as before, and it is up to the protocol layer to decide whether the data received is complete. Cases with an actual errno value or a queued error are still reported as failures with the detailed message, so real network errors are not hidden.

The more relaxed handling also applies to the send path, keeping the two directions consistent.

The stricter checking can be revisited later, but only in a way that does not break connections to servers that terminate without a TLS shutdown. Such a change should come with a test that covers an unclean close after a complete response.
