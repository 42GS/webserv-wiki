> Source: <https://pubs.opengroup.org/onlinepubs/9799919799/functions/socket.html>
> Retrieved: 2026-10-29. Original HTML: kept next to this file as `.source.html`.
> Converted with pandoc 3.10 (`-f html -t gfm --wrap=none`, `pandoc/opengroup-body.lua`).

The Open Group Base Specifications Issue 8\
IEEE Std 1003.1-2024\
Copyright © 2001-2024 The IEEE and The Open Group

------------------------------------------------------------------------

<span id="top"></span> <span id="socket"></span> <span id="tag_17_710"></span>

#### <span id="tag_17_710_01"></span>NAME

> socket — create an endpoint for communication

#### <span id="tag_17_710_02"></span>SYNOPSIS

> `#include <`[`sys/socket.h`](../basedefs/sys_socket.h.html)`>`\
> \
> `int socket(int`` `*`domain`*`, int`` `*`type`*`, int`` `*`protocol`*`);`\

#### <span id="tag_17_710_03"></span>DESCRIPTION

> The *socket*() function shall create an unbound socket in a communications domain, and return a file descriptor that can be used in later function calls that operate on sockets. The file descriptor shall be allocated as described in [*2.6 File Descriptor Allocation*](../functions/V2_chap02.html#tag_16_06).
>
> The *socket*() function takes the following arguments:
>
> *domain*
>
> Specifies the communications domain in which a socket is to be created.
>
> *type*
>
> Specifies the type of socket to be created.
>
> *protocol*
>
> Specifies a particular protocol to be used with the socket. Specifying a *protocol* of 0 causes *socket*() to use an unspecified default protocol appropriate for the requested socket type.
>
> The *domain* argument specifies the address family used in the communications domain. The address families supported by the system are implementation-defined.
>
> Symbolic constants that can be used for the domain argument are defined in the [*\<sys/socket.h\>*](../basedefs/sys_socket.h.html) header.
>
> The *type* argument specifies the socket type, which determines the semantics of communication over the socket. The following socket types are defined; implementations may specify additional socket types:
>
> SOCK_STREAM
>
> Provides sequenced, reliable, bidirectional, connection-mode byte streams, and may provide a transmission mechanism for out-of-band data.
>
> SOCK_DGRAM
>
> Provides datagrams, which are connectionless-mode, unreliable messages of fixed maximum length.
>
> SOCK_SEQPACKET
>
> Provides sequenced, reliable, bidirectional, connection-mode transmission paths for records. A record can be sent using one or more output operations and received using one or more input operations, but a single operation never transfers part of more than one record. Record boundaries are visible to the receiver via the MSG_EOR flag.
>
> Additionally, the *type* argument can contain the bitwise-inclusive OR of flags from the following list:
>
> SOCK_CLOEXEC
>
> Atomically set the FD_CLOEXEC flag on the new file descriptor.
>
> SOCK_CLOFORK
>
> Atomically set the FD_CLOFORK flag on the new file descriptor.
>
> SOCK_NONBLOCK
>
> Set the O_NONBLOCK file status flag on the new file description.
>
> Implementations may define additional flags.
>
> If the *protocol* argument is non-zero, it shall specify a protocol that is supported by the address family. If the *protocol* argument is zero, the default protocol for this address family and type shall be used. The protocols supported by the system are implementation-defined.
>
> The process may need to have appropriate privileges to use the *socket*() function or to create some sockets.

#### <span id="tag_17_710_04"></span>RETURN VALUE

> Upon successful completion, *socket*() shall return a non-negative integer, the socket file descriptor. Otherwise, a value of -1 shall be returned and *errno* set to indicate the error.\

#### <span id="tag_17_710_05"></span>ERRORS

> The *socket*() function shall fail if:
>
> \[EAFNOSUPPORT\]
>
> The implementation does not support the specified address family.
>
> \[EMFILE\]
>
> All file descriptors available to the process are currently open.
>
> \[ENFILE\]
>
> No more file descriptors are available for the system.
>
> \[EPROTONOSUPPORT\]
>
> The value of *protocol* is non-zero and either the protocol is not supported by the address family or the protocol is not supported by the implementation.
>
> \[EPROTOTYPE\]
>
> The value of *protocol* is non-zero and the socket type is not supported by the protocol.
>
> \[ESOCKTNOSUPPORT\] <sup>\[[OB](javascript:open_code('OB'))\]</sup> <img src="../images/opt-start.gif" data-border="0" /> or \[EPROTONOSUPPORT\] or \[EPROTOTYPE\] <img src="../images/opt-end.gif" data-border="0" />\
> \
> The socket type is not supported by the address family, or the socket type is not supported by the implementation.
>
> The *socket*() function may fail if:
>
> \[EACCES\]
>
> The process does not have appropriate privileges.
>
> \[ENOBUFS\]
>
> Insufficient resources were available in the system to perform the operation.
>
> \[ENOMEM\]
>
> Insufficient memory was available to fulfill the request.

------------------------------------------------------------------------

<div class="box">

*The following sections are informative.*

</div>

#### <span id="tag_17_710_06"></span>EXAMPLES

> None.

#### <span id="tag_17_710_07"></span>APPLICATION USAGE

> The documentation for specific address families specifies which protocols each address family supports. The documentation for specific protocols specifies which socket types each protocol supports.
>
> The application can determine whether an address family is supported by trying to create a socket with *domain* set to the protocol in question.

#### <span id="tag_17_710_08"></span>RATIONALE

> The use of the SOCK_CLOEXEC and SOCK_CLOFORK flags in the *type* argument of *socket*() is necessary to avoid a data race in multi-threaded applications. Without SOCK_CLOFORK, a file descriptor is leaked into a child process created by one thread in the window between another thread calling *socket*() and using [*fcntl*()](../functions/fcntl.html) to set the FD_CLOFORK flag. Without SOCK_CLOEXEC, a file descriptor intentionally inherited by child processes is similarly leaked into an executed program if FD_CLOEXEC is not set atomically. The SOCK_NONBLOCK flag is for convenience in avoiding additional [*fcntl*()](../functions/fcntl.html) calls.
>
> Historically the standard did not specify the *errno* value to be used when the socket type is not supported, and there were differences between implementations. Some reused the existing standard \[EPROTONOSUPPORT\] or \[EPROTOTYPE\] values while others set *errno* to a (then) non-standard value of \[ESOCKTNOSUPPORT\]. All three values are permitted in this version of the standard, but the use of \[EPROTONOSUPPORT\] or \[EPROTOTYPE\] is considered to be misleading when no protocol is specified (that is, the value of *protocol* is zero) and consequently those alternatives have been marked obsolescent. If *protocol* is non-zero, since there is no precedence between error conditions, all three values will still be permitted even after the obsolescent alternatives for the \[ESOCKTNOSUPPORT\] condition have been removed.

#### <span id="tag_17_710_09"></span>FUTURE DIRECTIONS

> A future version of this standard may disallow setting *errno* to \[EPROTONOSUPPORT\] or \[EPROTOTYPE\] when the socket type is not supported and *protocol* is zero.

#### <span id="tag_17_710_10"></span>SEE ALSO

> [*2.6 File Descriptor Allocation*](../functions/V2_chap02.html#tag_16_06), [*accept*](../functions/accept.html#), [*bind*](../functions/bind.html#), [*close*](../functions/close.html#), [*connect*](../functions/connect.html#), [*getsockname*](../functions/getsockname.html#), [*getsockopt*](../functions/getsockopt.html#), [*listen*](../functions/listen.html#), [*recv*](../functions/recv.html#), [*recvfrom*](../functions/recvfrom.html#), [*recvmsg*](../functions/recvmsg.html#), [*send*](../functions/send.html#), [*sendmsg*](../functions/sendmsg.html#), [*setsockopt*](../functions/setsockopt.html#), [*shutdown*](../functions/shutdown.html#), [*socketpair*](../functions/socketpair.html#)
>
> XBD [*\<netinet/in.h\>*](../basedefs/netinet_in.h.html), [*\<sys/socket.h\>*](../basedefs/sys_socket.h.html)

#### <span id="tag_17_710_11"></span>CHANGE HISTORY

> First released in Issue 6. Derived from the XNS, Issue 5.2 specification.

#### <span id="tag_17_710_12"></span>Issue 7

> POSIX.1-2008, Technical Corrigendum 2, XSH/TC2-2008/0335 \[835\] is applied.

#### <span id="tag_17_710_13"></span>Issue 8

> Austin Group Defects 411 and 1318 are applied, adding SOCK_CLOEXEC, SOCK_CLOFORK, and SOCK_NONBLOCK.
>
> Austin Group Defect 1067 is applied, adding the \[ESOCKTNOSUPPORT\] error and changing the \[EPROTONOSUPPORT\] and \[EPROTOTYPE\] errors.
>
> Austin Group Defect 1475 is applied, adding [*close*()](../functions/close.html) to the SEE ALSO section.

<div class="box">

*End of informative text.*

</div>

------------------------------------------------------------------------

 
