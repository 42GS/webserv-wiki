> Source: <https://pubs.opengroup.org/onlinepubs/9799919799/functions/accept.html>
> Retrieved: 2026-10-29. Original HTML: kept next to this file as `.source.html`.
> Converted with pandoc 3.10 (`-f html -t gfm --wrap=none`, `pandoc/opengroup-body.lua`).

The Open Group Base Specifications Issue 8\
IEEE Std 1003.1-2024\
Copyright © 2001-2024 The IEEE and The Open Group

------------------------------------------------------------------------

<span id="top"></span> <span id="accept"></span> <span id="tag_17_06"></span>

#### <span id="tag_17_06_01"></span>NAME

> accept, accept4 — accept a new connection on a socket

#### <span id="tag_17_06_02"></span>SYNOPSIS

> `#include <`[`sys/socket.h`](../basedefs/sys_socket.h.html)`>`\
> \
> `int accept(int`` `*`socket`*`, struct sockaddr *restrict`` `*`address`*`,`\
> `       socklen_t *restrict`` `*`address_len`*`);`\
> `int accept4(int`` `*`socket`*`, struct sockaddr *restrict`` `*`address`*`,`\
> `       socklen_t *restrict`` `*`address_len`*`, int`` `*`flag`*`);`\

#### <span id="tag_17_06_03"></span>DESCRIPTION

> The *accept*() function shall extract the first connection on the queue of pending connections, create a new socket with the same socket type protocol and address family as the specified socket, and allocate a new file descriptor for that socket. The file descriptor shall be allocated as described in [*2.6 File Descriptor Allocation*](../functions/V2_chap02.html#tag_16_06).
>
> The *accept*() function takes the following arguments:
>
> *socket*
>
> Specifies a socket that was created with [*socket*()](../functions/socket.html), has been bound to an address with [*bind*()](../functions/bind.html), and has issued a successful call to [*listen*()](../functions/listen.html).
>
> *address*
>
> Either a null pointer, or a pointer to a **sockaddr** structure where the address of the connecting socket shall be returned.
>
> *address_len*
>
> Either a null pointer, if *address* is a null pointer, or a pointer to a **socklen_t** object which on input specifies the length of the supplied **sockaddr** structure, and on output specifies the length of the address of the connecting socket.
>
> If *address* is not a null pointer, the address of the peer for the accepted connection shall be stored in the **sockaddr** structure pointed to by *address*, and the length of this address shall be stored in the object pointed to by *address_len*.
>
> If the actual length of the address is greater than the length of the supplied **sockaddr** structure, the stored address shall be truncated.
>
> If the protocol permits connections by unbound clients, and the peer is not bound, then the value stored in the object pointed to by *address* is unspecified.
>
> If the listen queue is empty of connection requests and O_NONBLOCK is not set on the file descriptor for the socket, *accept*() shall block until a connection is present. If the [*listen*()](../functions/listen.html) queue is empty of connection requests and O_NONBLOCK is set on the file descriptor for the socket, *accept*() shall fail and set *errno* to \[EAGAIN\] or \[EWOULDBLOCK\].
>
> The accepted socket cannot itself accept more connections. The original socket remains open and can accept more connections.
>
> If O_NONBLOCK is set on the file description for *socket*, it is implementation-defined whether O_NONBLOCK will be set on the file description created by *accept*(). FD_CLOEXEC and FD_CLOFORK for the new file descriptor shall be clear, regardless of how they are currently set for *socket*.
>
> It is implementation-defined which socket options, if any, on the accepted socket will have a default value determined by a value previously customized by [*setsockopt*()](../functions/setsockopt.html) on *socket*, rather than the default value used for other new sockets.
>
> The *accept4*() function shall be equivalent to the *accept*() function, except that the state of O_NONBLOCK on the new file description, and FD_CLOEXEC and FD_CLOFORK on the returned file descriptor shall be determined solely by the *flag* argument, which can be constructed from a bitwise-inclusive OR of flags from the following list:
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

#### <span id="tag_17_06_04"></span>RETURN VALUE

> Upon successful completion, *accept*() and *accept4*() shall return the non-negative file descriptor of the accepted socket. Otherwise, -1 shall be returned, *errno* shall be set to indicate the error, and any object pointed to by *address_len* shall remain unchanged.

#### <span id="tag_17_06_05"></span>ERRORS

> The *accept*() and *accept4*() functions shall fail if:
>
> \[EAGAIN\] or \[EWOULDBLOCK\]
>
> O_NONBLOCK is set for the socket file descriptor and no connections are present to be accepted.
>
> \[EBADF\]
>
> The *socket* argument is not a valid file descriptor.
>
> \[ECONNABORTED\]
>
> A connection has been aborted.
>
> \[EINTR\]
>
> The *accept*() function was interrupted by a signal that was caught before a valid connection arrived.
>
> \[EINVAL\]
>
> The *socket* is not accepting connections.
>
> \[EMFILE\]
>
> All file descriptors available to the process are currently open.
>
> \[ENFILE\]
>
> The maximum number of file descriptors in the system are already open.
>
> \[ENOBUFS\]
>
> No buffer space is available.
>
> \[ENOMEM\]
>
> There was insufficient memory available to complete the operation.
>
> \[ENOTSOCK\]
>
> The *socket* argument does not refer to a socket.
>
> \[EOPNOTSUPP\]
>
> The socket type of the specified socket does not support accepting connections.
>
> The *accept*() and *accept4*() functions may fail if:
>
> \[EPROTO\]
>
> A protocol error has occurred.
>
> The *accept4*() function may fail if:
>
> \[EINVAL\]
>
> The value of the *flag* argument is invalid.

------------------------------------------------------------------------

<div class="box">

*The following sections are informative.*

</div>

#### <span id="tag_17_06_06"></span>EXAMPLES

> None.

#### <span id="tag_17_06_07"></span>APPLICATION USAGE

> When a connection is available, [*select*()](../functions/select.html) indicates that the file descriptor for the socket is ready for reading.
>
> Many socket options are described as having implementation-defined default values, which may differ according to the protocol in use by the socket. Existing practice differs on whether socket options such as SO_SNDBUF that were customized on the original listening socket will impact the corresponding option on the newly returned socket. Implementations are permitted to allow inheritance of customized settings where it makes sense, although the most portable approach for applications is to limit [*setsockopt*()](../functions/setsockopt.html) customizations to only the accepted socket.
>
> For AF_UNIX sockets, it is recommended that *address* points to a buffer of length greater than `sizeof(struct sockaddr_un)` which has been initialized with null bytes. That way, even if the implementation supports the use of all bytes of *sun_path* without a terminating null byte, the larger buffer guarantees that the *sun_path* member can then be passed to other interfaces that expect a null-terminated string. If no truncation occurred based on the input value of *address_len*, it is unspecified whether the returned *address_len* will be `sizeof(struct sockaddr_un)`, or merely a value at least as large as `offsetof(struct sockaddr_un, sun_path)` plus the number of non-null bytes stored in *sun_path*.

#### <span id="tag_17_06_08"></span>RATIONALE

> The SOCK_CLOEXEC and SOCK_CLOFORK flags of *accept4*() are necessary to avoid a data race in multi-threaded applications. Without SOCK_CLOFORK, a file descriptor is leaked into a child process created by one thread in the window between another thread creating a file descriptor with *accept*() and then using [*fcntl*()](../functions/fcntl.html) to set the FD_CLOFORK flag. Without SOCK_CLOEXEC, a file descriptor intentionally inherited by child processes is similarly leaked into an executed program if FD_CLOEXEC is not set atomically.
>
> Two designs often used for network servers are multi-threaded servers with a pre-created pool of worker threads, where the thread that accepts the connection request hands over the new file descriptor to a worker thread for servicing, and pre-fork servers with a pre-created pool of worker processes, where the process that accepts the connection request passes the new file descriptor (for example via [*sendmsg*()](../functions/sendmsg.html)) to a worker process. In both of these designs, *accept4*() should be used with the SOCK_CLOFORK flag set. Simpler designs are also sometimes used that do not pre-create a pool. For a multi-threaded server that creates a thread to handle each request, SOCK_CLOFORK should still be used. For a forking server that creates a child to service each request, clearly SOCK_CLOFORK cannot be used if the child is to inherit the file descriptor to be serviced, and therefore this type of server needs to use an alternative method of indicating the end of communications, for example using [*shutdown*()](../functions/shutdown.html), to ensure the client sees end-of-file, rather than just closing the socket. Such child processes should set FD_CLOFORK on the inherited file descriptor before they attempt to start any additional child processes to avoid leakage into those children.
>
> The SOCK_NONBLOCK flag is for convenience in avoiding additional [*fcntl*()](../functions/fcntl.html) calls, as well as providing specific control over the O_NONBLOCK flag, since traditional implementations of *accept*() differ on whether O_NONBLOCK is inherited from the *socket* argument.

#### <span id="tag_17_06_09"></span>FUTURE DIRECTIONS

> None.

#### <span id="tag_17_06_10"></span>SEE ALSO

> [*2.6 File Descriptor Allocation*](../functions/V2_chap02.html#tag_16_06), [*bind*()](../functions/bind.html#), [*connect*()](../functions/connect.html#), [*listen*()](../functions/listen.html#), [*socket*()](../functions/socket.html#)
>
> XBD [*\<sys/socket.h\>*](../basedefs/sys_socket.h.html)

#### <span id="tag_17_06_11"></span>CHANGE HISTORY

> First released in Issue 6. Derived from the XNS, Issue 5.2 specification.
>
> The **restrict** keyword is added to the *accept*() prototype for alignment with the ISO/IEC 9899:1999 standard.

#### <span id="tag_17_06_12"></span>Issue 7

> SD5-XBD-ERN-4 is applied, changing the definition of the \[EMFILE\] error.
>
> Austin Group Interpretation 1003.1-2001 \#044 is applied, changing the "may fail" \[ENOBUFS\] and \[ENOMEM\] errors to become "shall fail" errors.
>
> Functionality relating to XSI STREAMS is marked obsolescent.
>
> POSIX.1-2008, Technical Corrigendum 1, XSH/TC1-2008/0018 \[464\] is applied.
>
> POSIX.1-2008, Technical Corrigendum 2, XSH/TC2-2008/0035 \[835\] and XSH/TC2-2008/0036 \[836\] are applied.

#### <span id="tag_17_06_13"></span>Issue 8

> Austin Group Defects 411 and 1318 are applied, adding *accept4*(), requiring FD_CLOEXEC and FD_CLOFORK to be clear for the file descriptor returned by *accept*(), and clarifying the requirements for O_NONBLOCK on the file description created by *accept*().
>
> Austin Group Defect 561 is applied, adding a paragraph about *sun_path* to APPLICATION USAGE.
>
> Austin Group Defect 1330 is applied, removing obsolescent interfaces.
>
> Austin Group Defect 1337 is applied, clarifying socket option default values.
>
> Austin Group Defect 1565 is applied, changing the description of *address_len*.

<div class="box">

*End of informative text.*

</div>

------------------------------------------------------------------------

 
