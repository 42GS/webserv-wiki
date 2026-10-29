> Source: <https://pubs.opengroup.org/onlinepubs/9799919799/functions/dup.html>
> Retrieved: 2026-10-29. Original HTML: kept next to this file as `.source.html`.
> Converted with pandoc 3.10 (`-f html -t gfm --wrap=none`, `pandoc/opengroup-body.lua`).

The Open Group Base Specifications Issue 8\
IEEE Std 1003.1-2024\
Copyright © 2001-2024 The IEEE and The Open Group

------------------------------------------------------------------------

<span id="top"></span> <span id="dup"></span> <span id="tag_17_116"></span>

#### <span id="tag_17_116_01"></span>NAME

> dup, dup2, dup3 — duplicate an open file descriptor

#### <span id="tag_17_116_02"></span>SYNOPSIS

> `#include <`[`unistd.h`](../basedefs/unistd.h.html)`>`\
> \
> `int dup(int`` `*`fildes`*`);`\
> `int dup2(int`` `*`fildes`*`, int`` `*`fildes2`*`);`\
> `int dup3(int`` `*`fildes`*`, int`` `*`fildes2`*`, int`` `*`flag`*`);`\

#### <span id="tag_17_116_03"></span>DESCRIPTION

> The *dup*() function provides an alternative interface to the service provided by [*fcntl*()](../functions/fcntl.html) using the F_DUPFD command. The call *dup*(*fildes*) shall be equivalent to:
>
>     fcntl(fildes, F_DUPFD, 0);
>
> The *dup2*() function shall cause the file descriptor *fildes2* to refer to the same open file description as the file descriptor *fildes* and to share any locks, and shall return *fildes2*. If *fildes2* is already a valid open file descriptor, it shall be closed first, unless *fildes* is equal to *fildes2* in which case *dup2*() shall return *fildes2* without closing it. If the close operation fails to close *fildes2*, *dup2*() shall return -1 without changing the open file description to which *fildes2* refers. If *fildes* is not a valid file descriptor, *dup2*() shall return -1 and shall not close *fildes2*. If *fildes2* is less than 0 or greater than or equal to {OPEN_MAX}, *dup2*() shall return -1 with *errno* set to \[EBADF\].
>
> Upon successful completion, if *fildes* is not equal to *fildes2*, the FD_CLOEXEC and FD_CLOFORK flags associated with *fildes2* shall be cleared. If *fildes* is equal to *fildes2*, the FD_CLOEXEC and FD_CLOFORK flags associated with *fildes2* shall not be changed.
>
> The *dup3*() function shall be equivalent to the *dup2*() function, except that it shall be an error if *fildes* is equal to *fildes2*, and the state of FD_CLOEXEC and FD_CLOFORK on the *fildes2* file descriptor shall be determined solely by the *flag* argument, which can be constructed from a bitwise-inclusive OR of flags from the following list:
>
> O_CLOEXEC
>
> Atomically set the FD_CLOEXEC flag on *fildes2*.
>
> O_CLOFORK
>
> Atomically set the FD_CLOFORK flag on *fildes2*.
>
> <sup>\[[TYM](javascript:open_code('TYM'))\]</sup> <img src="../images/opt-start.gif" data-border="0" alt="[Option Start]" /> If *fildes* refers to a typed memory object, the result of the *dup2*() or *dup3*() functions is unspecified. <img src="../images/opt-end.gif" data-border="0" alt="[Option End]" />

#### <span id="tag_17_116_04"></span>RETURN VALUE

> Upon successful completion a non-negative integer, namely the file descriptor, shall be returned; otherwise, -1 shall be returned and *errno* set to indicate the error.

#### <span id="tag_17_116_05"></span>ERRORS

> The *dup*() function shall fail if:
>
> \[EBADF\]
>
> The *fildes* argument is not a valid open file descriptor.
>
> \[EMFILE\]
>
> All file descriptors available to the process are currently open.
>
> The *dup2*() and *dup3*() functions shall fail if:
>
> \[EBADF\]
>
> The *fildes* argument is not a valid open file descriptor or the argument *fildes2* is negative or greater than or equal to {OPEN_MAX}.
>
> \[EINTR\]
>
> The function was interrupted by a signal.
>
> The *dup3*() function shall fail if:
>
> \[EINVAL\]
>
> The *fildes* and *fildes2* arguments are equal.
>
> The *dup2*() and *dup3*() functions may fail if:
>
> \[EIO\]
>
> An I/O error occurred while attempting to close *fildes2*.
>
> The *dup3*() function may fail if:
>
> \[EINVAL\]
>
> The value of the *flag* argument is invalid.

------------------------------------------------------------------------

<div class="box">

*The following sections are informative.*

</div>

#### <span id="tag_17_116_06"></span>EXAMPLES

> ##### <span id="tag_17_116_06_01"></span>Redirecting Standard Output to a File
>
> The following example closes standard output for the current processes, re-assigns standard output to go to the file referenced by *pfd*, and closes the original file descriptor to clean up.
>
>     #include <unistd.h>
>     ...
>     int pfd;
>     ...
>     close(1);
>     dup(pfd);
>     close(pfd);
>     ...
>
> ##### <span id="tag_17_116_06_02"></span>Redirecting Error Messages
>
> The following example redirects messages from *stderr* to *stdout*.
>
>     #include <unistd.h>
>     ...
>     dup2(1, 2);
>     ...

#### <span id="tag_17_116_07"></span>APPLICATION USAGE

> Implementations may use file descriptors that must be inherited into child processes for the child process to remain conforming, such as for message catalog or tracing purposes. Therefore, an application that calls *dup2*() with an arbitrary integer for *fildes2* risks non-conforming behavior, and *dup2*() can only portably be used to overwrite file descriptor values that the application has obtained through explicit actions, or for the three file descriptors corresponding to the standard file streams. In order to avoid a race condition of leaking an unintended file descriptor into a child process or executed program, an application should consider opening all file descriptors with the FD_CLOFORK or FD_CLOEXEC flag, or both flags, set unless the file descriptor is intended to be inherited by child processes or executed programs, respectively.

#### <span id="tag_17_116_08"></span>RATIONALE

> The *dup*() function is redundant. Its services are also provided by the [*fcntl*()](../functions/fcntl.html) function. It has been included in this volume of POSIX.1-2024 primarily for historical reasons, since many existing applications use it. On the other hand, the *dup2*() function provides unique services, as no other interface is able to atomically replace an existing file descriptor.
>
> The *dup2*() function is not marked obsolescent because it presents a type-safe version of functionality provided in a type-unsafe version by [*fcntl*()](../functions/fcntl.html). It is used in the POSIX Ada binding.
>
> The *dup2*() function is not intended for use in critical regions as a synchronization mechanism.
>
> In the description of \[EBADF\], the case of *fildes* being out of range is covered by the given case of *fildes* not being valid. The descriptions for *fildes* and *fildes2* are different because the only kind of invalidity that is relevant for *fildes2* is whether it is out of range; that is, it does not matter whether *fildes2* refers to an open file when the *dup2*() call is made.
>
> The *dup3*() function with the O_CLOEXEC and O_CLOFORK flags is necessary to avoid a data race in multi-threaded applications. Without O_CLOFORK, a file descriptor is leaked into a child process created by one thread in the window between another thread creating a file descriptor with *dup2*() and then using [*fcntl*()](../functions/fcntl.html) to set the FD_CLOFORK flag. Without O_CLOEXEC, a file descriptor intentionally inherited by child processes is similarly leaked into an executed program if FD_CLOEXEC is not set atomically. The safe counterpart for avoiding the same race with *dup*() is the use of the F_DUPFD_CLOFORK or F_DUPFD_CLOEXEC action of the [*fcntl*()](../functions/fcntl.html) function.

#### <span id="tag_17_116_09"></span>FUTURE DIRECTIONS

> None.

#### <span id="tag_17_116_10"></span>SEE ALSO

> [*close*()](../functions/close.html#), [*fcntl*()](../functions/fcntl.html#), [*open*()](../functions/open.html#)
>
> XBD [*\<unistd.h\>*](../basedefs/unistd.h.html)

#### <span id="tag_17_116_11"></span>CHANGE HISTORY

> First released in Issue 1. Derived from Issue 1 of the SVID.

#### <span id="tag_17_116_12"></span>Issue 7

> SD5-XSH-ERN-187 is applied.
>
> POSIX.1-2008, Technical Corrigendum 1, XSH/TC1-2008/0075 \[149,428\] and XSH/TC1-2008/0076 \[149\] are applied.

#### <span id="tag_17_116_13"></span>Issue 8

> Austin Group Defects 411, 1318, 1483, and 1577 are applied, adding *dup3*() and FD_CLOFORK.

<div class="box">

*End of informative text.*

</div>

------------------------------------------------------------------------

 
