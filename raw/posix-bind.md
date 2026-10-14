> Source: <https://pubs.opengroup.org/onlinepubs/9799919799/functions/bind.html>
> Retrieved: 2026-10-15. Original HTML: kept next to this file as `.source.html`.
> Converted to markdown by text extraction of `div#content`; wording is unchanged,
> whitespace, list markup and code fences were normalized.

The Open Group Base Specifications Issue 8 IEEE Std 1003.1-2024 Copyright © 2001-2024 The IEEE and The Open Group

<a id="top"></a>

<a id="bind"></a>

<a id="tag_17_44"></a>

<a id="tag_17_44_01"></a>

#### NAME

bind — bind a name to a socket

<a id="tag_17_44_02"></a>

#### SYNOPSIS

`#include <sys/socket.h> int bind(int socket, const struct sockaddr *address,        socklen_t address_len); `

<a id="tag_17_44_03"></a>

#### DESCRIPTION

The bind() function shall assign a local socket address address to a socket identified by descriptor socket that has no local socket address assigned. Sockets created with the socket() function are initially unnamed; they are identified only by their address family.

The bind() function takes the following arguments:

- socket

- Specifies the file descriptor of the socket to be bound.

- address

- Points to a sockaddr structure containing the address to be bound to the socket. The length and format of the address depend on the address family of the socket.

- address_len

- Specifies the length of the sockaddr structure pointed to by the address argument.

The socket specified by socket may require the process to have appropriate privileges to use the bind() function.

If the address family of the socket is AF_UNIX, the application shall ensure that a null terminator after the pathname is included in the sun_path member of address as a sockaddr_un structure, and that address_len is at least offsetof(struct sockaddr_un, sun_path) + 1 plus the length of the pathname. If the pathname in the sun_path member of address names an existing file, including a symbolic link, bind() shall treat the address as already in use; see ERRORS below.

If the socket address cannot be assigned immediately and O_NONBLOCK is set for the file descriptor for the socket, bind() shall fail and set errno to [EINPROGRESS], but the assignment request shall not be aborted, and the assignment shall be completed asynchronously. Subsequent calls to bind() for the same socket, before the assignment is completed, shall fail and set errno to [EALREADY].

When the assignment has been performed asynchronously, pselect(), select(), poll(), and ppoll() shall indicate that the file descriptor for the socket is ready for reading and writing.

<a id="tag_17_44_04"></a>

#### RETURN VALUE

Upon successful completion, bind() shall return 0; otherwise, -1 shall be returned and errno set to indicate the error.

<a id="tag_17_44_05"></a>

#### ERRORS

The bind() function shall fail if:

- [EADDRINUSE]

- The specified address is already in use.

- [EADDRNOTAVAIL]

- The specified address is not available from the local machine.

- [EAFNOSUPPORT]

- The specified address is not a valid address for the address family of the specified socket.

- [EALREADY]

- An assignment request is already in progress for the specified socket.

- [EBADF]

- The socket argument is not a valid file descriptor.

- [EINPROGRESS]

- O_NONBLOCK is set for the file descriptor for the socket and the assignment cannot be immediately performed; the assignment shall be performed asynchronously.

- [EINVAL]

- The socket is already bound to an address, and the protocol does not support binding to a new address; or the socket has been shut down.

- [ENOBUFS]

- Insufficient resources were available to complete the call.

- [ENOTSOCK]

- The socket argument does not refer to a socket.

- [EOPNOTSUPP]

- The socket type of the specified socket does not support binding to an address.

If the address family of the socket is AF_UNIX, then bind() shall fail if:

- [EACCES]

- A component of the path prefix denies search permission, or the requested name requires writing in a directory with a mode that denies write permission.

- [EDESTADDRREQ] or [EISDIR]

- The address argument is a null pointer.

- [EILSEQ]

- The last pathname component is not a portable filename, and cannot be created in the target directory.

- [EIO]

- An I/O error occurred.

- [ELOOP]

- A loop exists in symbolic links encountered during resolution of the pathname in address.

- [ENAMETOOLONG]

- The length of a component of a pathname is longer than {NAME_MAX}.

- [ENOENT]

- A component of the path prefix of the pathname in address does not name an existing file or the pathname is an empty string.

- [ENOENT] or [ENOTDIR]

- The pathname in address contains at least one non-<slash> character and ends with one or more trailing <slash> characters. If the pathname without the trailing <slash> characters would name an existing file, an [ENOENT] error shall not occur.

- [ENOTDIR]

- A component of the path prefix of the pathname in address names an existing file that is neither a directory nor a symbolic link to a directory, or the pathname in address contains at least one non-<slash> character and ends with one or more trailing <slash> characters and the last pathname component names an existing file that is neither a directory nor a symbolic link to a directory.

- [EROFS]

- The name would reside on a read-only file system.

The bind() function may fail if:

- [EACCES]

- The specified address is protected and the current user does not have permission to bind to it.

- [EINVAL]

- The address_len argument is not a valid length for the address family.

- [EISCONN]

- The socket is already connected.

- [ELOOP]

- More than {SYMLOOP_MAX} symbolic links were encountered during resolution of the pathname in address.

- [ENAMETOOLONG]

- The length of a pathname exceeds {PATH_MAX}, or pathname resolution of a symbolic link produced an intermediate result with a length that exceeds {PATH_MAX}.

The following sections are informative.

<a id="tag_17_44_06"></a>

#### EXAMPLES

The following code segment shows how to create a socket and bind it to a name in the AF_UNIX domain.

```
#define MY_SOCK_PATH "/somepath"
 
int sfd;
struct sockaddr_un my_addr;
 
sfd = socket(AF_UNIX, SOCK_STREAM, 0);
if (sfd == -1)
    /* Handle error */;
 
memset(&my_addr, '\0', sizeof(struct sockaddr_un));
                     /* Clear structure */
my_addr.sun_family = AF_UNIX;
strncpy(my_addr.sun_path, MY_SOCK_PATH, sizeof(my_addr.sun_path) -1);
 
if (bind(sfd, (struct sockaddr *) &my_addr,
    sizeof(struct sockaddr_un)) == -1)
    /* Handle error */;
```

<a id="tag_17_44_07"></a>

#### APPLICATION USAGE

An application program can retrieve the assigned socket name with the getsockname() function.

For AF_UNIX sockets, some implementations support an extension where address_len does not have to include a null terminator for the pathname stored in sun_path, which in turn allows a pathname to be one byte longer. However, such usage is not portable, and carries a risk of accessing beyond the intended bounds of the pathname length.

<a id="tag_17_44_08"></a>

#### RATIONALE

Implementations are encouraged to have bind() report an [EILSEQ] error if the last component of the address to be bound to an AF_UNIX family socket contains any bytes that have the encoded value of a <newline> character.

<a id="tag_17_44_09"></a>

#### FUTURE DIRECTIONS

None.

<a id="tag_17_44_10"></a>

#### SEE ALSO

connect(), getsockname(), listen(), socket()

XBD <sys/socket.h>

<a id="tag_17_44_11"></a>

#### CHANGE HISTORY

First released in Issue 6. Derived from the XNS, Issue 5.2 specification.

<a id="tag_17_44_12"></a>

#### Issue 7

Austin Group Interpretation 1003.1-2001 #044 is applied, changing the "may fail" [ENOBUFS] error to become a "shall fail" error.

Austin Group Interpretation 1003.1-2001 #143 is applied.

SD5-XSH-ERN-185 is applied.

An example is added.

POSIX.1-2008, Technical Corrigendum 1, XSH/TC1-2008/0042 [146], XSH/TC1-2008/0043 [146], and XSH/TC1-2008/0044 [324] are applied.

POSIX.1-2008, Technical Corrigendum 2, XSH/TC2-2008/0050 [822] is applied.

<a id="tag_17_44_13"></a>

#### Issue 8

Austin Group Defect 251 is applied, encouraging implementations to disallow the creation of filenames containing any bytes that have the encoded value of a <newline> character.

Austin Group Defects 293 and 1482 are applied, adding the [EILSEQ] error.

Austin Group Defect 561 is applied, changing the requirements for the sun_path member of the sockaddr_un structure.

Austin Group Defect 1263 is applied, adding ppoll().

Austin Group Defect 1605 is applied, clarifying how the [EADDRINUSE] error applies to AF_UNIX sockets.

End of informative text.
