> Source: <https://pubs.opengroup.org/onlinepubs/9799919799/functions/listen.html>
> Retrieved: 2026-10-29. Original HTML: kept next to this file as `.source.html`.
> Converted with pandoc 3.10 (`-f html -t gfm --wrap=none`, `pandoc/opengroup-body.lua`).

The Open Group Base Specifications Issue 8\
IEEE Std 1003.1-2024\
Copyright © 2001-2024 The IEEE and The Open Group

------------------------------------------------------------------------

<span id="top"></span> <span id="listen"></span> <span id="tag_17_306"></span>

#### <span id="tag_17_306_01"></span>NAME

> listen — listen for socket connections and limit the queue of incoming connections

#### <span id="tag_17_306_02"></span>SYNOPSIS

> `#include <`[`sys/socket.h`](../basedefs/sys_socket.h.html)`>`\
> \
> `int listen(int`` `*`socket`*`, int`` `*`backlog`*`);`\

#### <span id="tag_17_306_03"></span>DESCRIPTION

> The *listen*() function shall mark a connection-mode socket, specified by the *socket* argument, as accepting connections.
>
> The *backlog* argument provides a hint to the implementation which the implementation shall use to limit the number of outstanding connections in the socket's listen queue. Implementations may impose a limit on *backlog* and silently reduce the specified value. Normally, a larger *backlog* argument value shall result in a larger or equal length of the listen queue. Implementations shall support values of *backlog* up to SOMAXCONN, defined in [*\<sys/socket.h\>*](../basedefs/sys_socket.h.html).
>
> The implementation may include incomplete connections in its listen queue. The limits on the number of incomplete connections and completed connections queued may be different.
>
> The implementation may have an upper limit on the length of the listen queue—either global or per accepting socket. If *backlog* exceeds this limit, the length of the listen queue is set to the limit.
>
> If *listen*() is called with a *backlog* argument value that is less than 0, the function behaves as if it had been called with a *backlog* argument value of 0.
>
> A *backlog* argument of 0 may allow the socket to accept connections, in which case the length of the listen queue may be set to an implementation-defined minimum value.
>
> The socket in use may require the process to have appropriate privileges to use the *listen*() function.

#### <span id="tag_17_306_04"></span>RETURN VALUE

> Upon successful completions, *listen*() shall return 0; otherwise, -1 shall be returned and *errno* set to indicate the error.

#### <span id="tag_17_306_05"></span>ERRORS

> The *listen*() function shall fail if:
>
> \[EBADF\]
>
> The *socket* argument is not a valid file descriptor.
>
> \[EDESTADDRREQ\]
>
> The socket is not bound to a local address, and the protocol does not support listening on an unbound socket.
>
> \[EINVAL\]
>
> The *socket* is already connected.
>
> \[ENOTSOCK\]
>
> The *socket* argument does not refer to a socket.
>
> \[EOPNOTSUPP\]
>
> The socket protocol does not support *listen*().
>
> The *listen*() function may fail if:
>
> \[EACCES\]
>
> The calling process does not have appropriate privileges.
>
> \[EINVAL\]
>
> The *socket* has been shut down.
>
> \[ENOBUFS\]
>
> Insufficient resources are available in the system to complete the call.

------------------------------------------------------------------------

<div class="box">

*The following sections are informative.*

</div>

#### <span id="tag_17_306_06"></span>EXAMPLES

> None.

#### <span id="tag_17_306_07"></span>APPLICATION USAGE

> None.

#### <span id="tag_17_306_08"></span>RATIONALE

> None.

#### <span id="tag_17_306_09"></span>FUTURE DIRECTIONS

> None.

#### <span id="tag_17_306_10"></span>SEE ALSO

> [*accept*()](../functions/accept.html#), [*connect*()](../functions/connect.html#), [*socket*()](../functions/socket.html#)
>
> XBD [*\<sys/socket.h\>*](../basedefs/sys_socket.h.html)

#### <span id="tag_17_306_11"></span>CHANGE HISTORY

> First released in Issue 6. Derived from the XNS, Issue 5.2 specification.
>
> The DESCRIPTION is updated to describe the relationship of SOMAXCONN and the *backlog* argument.

<div class="box">

*End of informative text.*

</div>

------------------------------------------------------------------------

 
