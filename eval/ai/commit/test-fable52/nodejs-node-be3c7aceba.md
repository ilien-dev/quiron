http2: wait for session socket writable end on close/destroy

This slightly alters the behaviour of session close. The session
now first calls .end() on its socket so that pending data is
flushed, and only then calls .destroy() to make sure the Readable
side is closed as well. This lets the socket finish transmitting,
receive a proper FIN packet and avoid ECONNRESET errors on a
graceful close.

onStreamClose now calls stream.destroy() directly instead of going
through kMaybeDestroy. The latter first checks that the stream has
writableFinished set, which may not be true yet: we have just
(synchronously) called .end() on the stream if it was not already
closed, and that does not give it enough time to finish. There is
also no point in waiting for 'finish' here, because the other
party has already closed the stream and we would not be able to
write to it anyway.

A few tests are updated to handle graceful session close
correctly:

* Read the request data on the client side where it was
  previously left unread.
* Read the push stream data on the client side where it was
  previously left unread.
* Stop relying on socket.destroy() on the client to finish the
  server session. Destroying the socket does not close the server
  session, and a GOAWAY frame by itself is *not* a session close.

Also add a few mustCall checks for 'close' events.
