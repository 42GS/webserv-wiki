> Source: <https://pubs.opengroup.org/onlinepubs/9799919799/functions/recv.html>
> Retrieved: 2026-10-15. Original HTML: kept next to this file as `.source.html`.
> Converted to markdown by text extraction of `div#content`; wording is unchanged,
> whitespace, list markup and code fences were normalized.

The Open Group Base Specifications Issue 8 IEEE Std 1003.1-2024 Copyright © 2001-2024 The IEEE and The Open Group

<a id="top"></a>

<a id="recv"></a>

<a id="tag_17_482"></a>

<a id="tag_17_482_01"></a>

#### NAME

recv — receive a message from a connected socket

<a id="tag_17_482_02"></a>

#### SYNOPSIS

`#include <sys/socket.h> ssize_t recv(int socket, void *buffer, size_t length, int flags); `

<a id="tag_17_482_03"></a>

#### DESCRIPTION

The recv() function shall receive a message from a connection-mode or connectionless-mode socket. It is normally used with connected sockets because it does not permit the application to retrieve the source address of received data.

The recv() function takes the following arguments:

- socket

- Specifies the socket file descriptor.

- buffer

- Points to a buffer where the message should be stored.

- length

- Specifies the length in bytes of the buffer pointed to by the buffer argument.

- flags

Specifies the type of message reception. Values of this argument are formed by logically OR'ing zero or more of the following values:

- MSG_PEEK

- Peeks at an incoming message. The data is treated as unread and the next recv() or similar function shall still return this data.

- MSG_OOB

- Requests out-of-band data. The significance and semantics of out-of-band data are protocol-specific.

- MSG_WAITALL

- On SOCK_STREAM sockets this requests that the function block until the full amount of data can be returned. The function may return the smaller amount of data if the socket is a message-based socket, if a signal is caught, if the connection is terminated, if MSG_PEEK was specified, or if an error is pending for the socket.

The recv() function shall return the length of the message written to the buffer pointed to by the buffer argument. For message-based sockets, such as SOCK_DGRAM and SOCK_SEQPACKET, the entire message shall be read in a single operation. If a message is too long to fit in the supplied buffer, and MSG_PEEK is not set in the flags argument, the excess bytes shall be discarded. For stream-based sockets, such as SOCK_STREAM, message boundaries shall be ignored. In this case, data shall be returned to the user as soon as it becomes available, and no data shall be discarded.

If the MSG_WAITALL flag is not set, data shall be returned only up to the end of the first message.

If no messages are available at the socket and O_NONBLOCK is not set on the socket's file descriptor, recv() shall block until a message arrives or a timeout occurs (see SO_RCVTIMEO in 2.10.16 Use of Options). If no messages are available at the socket and O_NONBLOCK is set on the socket's file descriptor, recv() shall fail and set errno to [EAGAIN] or [EWOULDBLOCK].

<a id="tag_17_482_04"></a>

#### RETURN VALUE

Upon successful completion, recv() shall return the length of the message in bytes. If no messages are available to be received and the peer has performed an orderly shutdown, recv() shall return 0. Otherwise, -1 shall be returned and errno set to indicate the error.

<a id="tag_17_482_05"></a>

#### ERRORS

The recv() function shall fail if:

- [EAGAIN] or [EWOULDBLOCK]

- The socket's file descriptor is marked O_NONBLOCK and no data is waiting to be received; or MSG_OOB is set and no out-of-band data is available and either the socket's file descriptor is marked O_NONBLOCK or the socket does not support blocking to await out-of-band data. See also SO_RCVTIMEO in 2.10.16 Use of Options .

- [EBADF]

- The socket argument is not a valid file descriptor.

- [ECONNRESET]

- A connection was forcibly closed by a peer.

- [EINTR]

- The recv() function was interrupted by a signal that was caught, before any data was available.

- [EINVAL]

- The MSG_OOB flag is set and no out-of-band data is available.

- [ENOTCONN]

- A receive is attempted on a connection-mode socket that is not connected.

- [ENOTSOCK]

- The socket argument does not refer to a socket.

- [EOPNOTSUPP]

- The specified flags are not supported for this socket type or protocol.

- [ETIMEDOUT]

- The connection timed out during connection establishment, or due to a transmission timeout on active connection.

The recv() function may fail if:

- [EIO]

- An I/O error occurred while reading from or writing to the file system.

- [ENOBUFS]

- Insufficient resources were available in the system to perform the operation.

- [ENOMEM]

- Insufficient memory was available to fulfill the request.

The following sections are informative.

<a id="tag_17_482_06"></a>

#### EXAMPLES

None.

<a id="tag_17_482_07"></a>

#### APPLICATION USAGE

The recv() function is equivalent to recvfrom() with null pointer address and address_len arguments, and to read() if the socket argument refers to a socket and the flags argument is 0.

The select() and poll() functions can be used to determine when data is available to be received.

<a id="tag_17_482_08"></a>

#### RATIONALE

None.

<a id="tag_17_482_09"></a>

#### FUTURE DIRECTIONS

None.

<a id="tag_17_482_10"></a>

#### SEE ALSO

poll(), pselect(), read(), recvmsg(), recvfrom(), send(), sendmsg(), sendto(), setsockopt(), shutdown(), socket(), write()

XBD <sys/socket.h>

<a id="tag_17_482_11"></a>

#### CHANGE HISTORY

First released in Issue 6. Derived from the XNS, Issue 5.2 specification.

<a id="tag_17_482_12"></a>

#### Issue 7

POSIX.1-2008, Technical Corrigendum 1, XSH/TC1-2008/0502 [462] is applied.

<a id="tag_17_482_13"></a>

#### Issue 8

Austin Group Defect 1429 is applied, clarifying the behavior on timeout by adding references to 2.10.16 Use of Options.

End of informative text.
