> Source: <https://pubs.opengroup.org/onlinepubs/9799919799/functions/send.html>
> Retrieved: 2026-10-15. Original HTML: kept next to this file as `.source.html`.
> Converted to markdown by text extraction of `div#content`; wording is unchanged,
> whitespace, list markup and code fences were normalized.

The Open Group Base Specifications Issue 8 IEEE Std 1003.1-2024 Copyright © 2001-2024 The IEEE and The Open Group

<a id="top"></a>

<a id="send"></a>

<a id="tag_17_516"></a>

<a id="tag_17_516_01"></a>

#### NAME

send — send a message on a socket

<a id="tag_17_516_02"></a>

#### SYNOPSIS

`#include <sys/socket.h> ssize_t send(int socket, const void *buffer, size_t length, int flags); `

<a id="tag_17_516_03"></a>

#### DESCRIPTION

The send() function shall initiate transmission of a message from the specified socket to its peer. The send() function shall send a message only when the socket is connected. If the socket is a connectionless-mode socket, the message shall be sent to the pre-specified peer address.

The send() function takes the following arguments:

- socket

- Specifies the socket file descriptor.

- buffer

- Points to the buffer containing the message to send.

- length

- Specifies the length of the message in bytes.

- flags

Specifies the type of message transmission. Values of this argument are formed by logically OR'ing zero or more of the following flags:

- MSG_EOR

- Terminates a record (if supported by the protocol).

- MSG_OOB

- Sends out-of-band data on sockets that support out-of-band communications. The significance and semantics of out-of-band data are protocol-specific.

- MSG_NOSIGNAL

- Requests not to send the SIGPIPE signal if an attempt to send is made on a stream-oriented socket that is no longer connected. The [EPIPE] error shall still be returned.

The length of the message to be sent is specified by the length argument. If the message is too long to pass through the underlying protocol, send() shall fail and no data shall be transmitted.

Successful completion of a call to send() does not guarantee delivery of the message. A return value of -1 indicates only locally-detected errors.

If space is not available at the sending socket to hold the message to be transmitted, and the socket file descriptor does not have O_NONBLOCK set, send() shall block until space is available or a timeout occurs (see SO_SNDTIMEO in 2.10.16 Use of Options). If space is not available at the sending socket to hold the message to be transmitted, and the socket file descriptor does have O_NONBLOCK set, send() shall fail. The select() and poll() functions can be used to determine when it is possible to send more data.

The socket in use may require the process to have appropriate privileges to use the send() function.

<a id="tag_17_516_04"></a>

#### RETURN VALUE

Upon successful completion, send() shall return the number of bytes sent. Otherwise, -1 shall be returned and errno set to indicate the error.

<a id="tag_17_516_05"></a>

#### ERRORS

The send() function shall fail if:

- [EAGAIN] or [EWOULDBLOCK]

- The socket's file descriptor is marked O_NONBLOCK and the requested operation would block. See also SO_SNDTIMEO in 2.10.16 Use of Options.

- [EBADF]

- The socket argument is not a valid file descriptor.

- [ECONNRESET]

- A connection was forcibly closed by a peer.

- [EDESTADDRREQ]

- The socket is not connection-mode and no peer address is set.

- [EINTR]

- A signal interrupted send() before any data was transmitted.

- [EMSGSIZE]

- The message is too large to be sent all at once, as the socket requires.

- [ENOTCONN]

- The socket is not connected.

- [ENOTSOCK]

- The socket argument does not refer to a socket.

- [EOPNOTSUPP]

- The socket argument is associated with a socket that does not support one or more of the values set in flags.

- [EPIPE]

- The socket is shut down for writing, or the socket is connection-mode and is no longer connected. In the latter case, and if the socket is of type SOCK_STREAM or SOCK_SEQPACKET and the MSG_NOSIGNAL flag is not set, the SIGPIPE signal is generated to the calling thread.

The send() function may fail if:

- [EACCES]

- The calling process does not have appropriate privileges.

- [EIO]

- An I/O error occurred while reading from or writing to the file system.

- [ENETDOWN]

- The local network interface used to reach the destination is down.

- [ENETUNREACH]

- No route to the network is present.

- [ENOBUFS]

- Insufficient resources were available in the system to perform the operation.

The following sections are informative.

<a id="tag_17_516_06"></a>

#### EXAMPLES

None.

<a id="tag_17_516_07"></a>

#### APPLICATION USAGE

If the socket argument refers to a connection-mode socket, the send() function is equivalent to sendto() (with any value for the dest_addr and dest_len arguments, as they are ignored in this case). If the socket argument refers to a socket and the flags argument is 0, the send() function is equivalent to write().

<a id="tag_17_516_08"></a>

#### RATIONALE

None.

<a id="tag_17_516_09"></a>

#### FUTURE DIRECTIONS

None.

<a id="tag_17_516_10"></a>

#### SEE ALSO

connect(), getsockopt(), poll(), pselect(), recv(), recvfrom(), recvmsg(), sendmsg(), sendto(), setsockopt(), shutdown(), socket(), write()

XBD <sys/socket.h>

<a id="tag_17_516_11"></a>

#### CHANGE HISTORY

First released in Issue 6. Derived from the XNS, Issue 5.2 specification.

<a id="tag_17_516_12"></a>

#### Issue 7

Austin Group Interpretation 1003.1-2001 #035 is applied, updating the DESCRIPTION to clarify the behavior when the socket is a connectionless-mode socket.

The MSG_NOSIGNAL flag is added from The Open Group Technical Standard, 2006, Extended API Set Part 2.

The [EPIPE] error is modified.

POSIX.1-2008, Technical Corrigendum 1, XSH/TC1-2008/0543 [463] is applied.

<a id="tag_17_516_13"></a>

#### Issue 8

Austin Group Defect 1429 is applied, clarifying the behavior on timeout by adding references to 2.10.16 Use of Options.

End of informative text.
