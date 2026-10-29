> Source: <https://pubs.opengroup.org/onlinepubs/9799919799/functions/close.html>
> Retrieved: 2026-10-29. Original HTML: kept next to this file as `.source.html`.
> Converted with pandoc 3.10 (`-f html -t gfm --wrap=none`, `pandoc/opengroup-body.lua`).

The Open Group Base Specifications Issue 8\
IEEE Std 1003.1-2024\
Copyright © 2001-2024 The IEEE and The Open Group

------------------------------------------------------------------------

<span id="top"></span> <span id="close"></span> <span id="tag_17_81"></span>

#### <span id="tag_17_81_01"></span>NAME

> close, posix_close — close a file descriptor

#### <span id="tag_17_81_02"></span>SYNOPSIS

> `#include <`[`unistd.h`](../basedefs/unistd.h.html)`>`\
> \
> `int close(int`` `*`fildes`*`);`\
> `int posix_close(int`` `*`fildes`*`, int`` `*`flag`*`);`\

#### <span id="tag_17_81_03"></span>DESCRIPTION

> The *close*() function shall deallocate the file descriptor indicated by *fildes*. To deallocate means to make the file descriptor available for return by subsequent calls to [*open*()](../functions/open.html) or other functions that allocate file descriptors. All process-owned file locks that the calling process owns on the file associated with the file descriptor shall be unlocked.
>
> If *close*() is interrupted by a signal that is to be caught, then it is unspecified whether it returns -1 with *errno* set to \[EINTR\] and *fildes* remaining open, or returns -1 with *errno* set to \[EINPROGRESS\] and *fildes* being closed, or returns 0 to indicate successful completion; except that if POSIX_CLOSE_RESTART is defined as 0, then the option of returning -1 with *errno* set to \[EINTR\] and *fildes* remaining open shall not occur. If *close*() returns -1 with *errno* set to \[EINTR\], it is unspecified whether *fildes* can subsequently be passed to any function except *close*() or *posix_close*() without error. For all other error situations (except for \[EBADF\] where *fildes* was invalid), *fildes* shall be closed. If *fildes* was closed even though the close operation is incomplete, the close operation shall continue asynchronously and the process shall have no further ability to track the completion or final status of the close operation.
>
> When all file descriptors associated with a pipe or FIFO special file are closed, any data remaining in the pipe or FIFO shall be discarded.
>
> When all file descriptors associated with an open file description have been closed, the open file description shall be freed.
>
> If the link count of the file is 0, when all file descriptors associated with the file are closed, the space occupied by the file shall be freed and the file shall no longer be accessible.
>
> <sup>\[[XSI](javascript:open_code('XSI'))\]</sup> <img src="../images/opt-start.gif" data-border="0" alt="[Option Start]" /> If *fildes* refers to the manager side of a pseudo-terminal, and this is the last close, a SIGHUP signal shall be sent to the controlling process, if any, for which the subsidiary side of the pseudo-terminal is the controlling terminal. It is unspecified whether closing the manager side of the pseudo-terminal flushes all queued input and output. <img src="../images/opt-end.gif" data-border="0" alt="[Option End]" />
>
> When there is an outstanding cancelable asynchronous I/O operation against *fildes* when *close*() is called, that I/O operation may be canceled. An I/O operation that is not canceled completes as if the *close*() operation had not yet occurred. All operations that are not canceled shall complete as if the *close*() blocked until the operations completed. The *close*() operation itself need not block awaiting such I/O completion. Whether any I/O operation is canceled, and which I/O operation may be canceled upon *close*(), is implementation-defined.
>
> If a memory mapped file <sup>\[[SHM](javascript:open_code('SHM'))\]</sup> <img src="../images/opt-start.gif" data-border="0" alt="[Option Start]" />  or a shared memory object <img src="../images/opt-end.gif" data-border="0" alt="[Option End]" />  remains referenced at the last close (that is, a process has it mapped), then the entire contents of the memory object shall persist until the memory object becomes unreferenced. If this is the last close of a memory mapped file <sup>\[[SHM](javascript:open_code('SHM'))\]</sup> <img src="../images/opt-start.gif" data-border="0" alt="[Option Start]" />  or a shared memory object <img src="../images/opt-end.gif" data-border="0" alt="[Option End]" />  and the close results in the memory object becoming unreferenced, and the memory object has been unlinked, then the memory object shall be removed.
>
> When all file descriptors associated with a socket have been closed, the socket shall be destroyed. If the socket is in connection-mode, and the SO_LINGER option is set for the socket with non-zero linger time, and the socket has untransmitted data, then *close*() shall block for up to the current linger interval until all data is transmitted.
>
> The *posix_close*() function shall be equivalent to the *close*() function, except with the modifications based on the *flag* argument as described below. If *flag* is 0, then *posix_close*() shall not return -1 with *errno* set to \[EINTR\], which implies that *fildes* will always be closed (except for \[EBADF\], where *fildes* was invalid). If *flag* includes POSIX_CLOSE_RESTART and POSIX_CLOSE_RESTART is defined as a non-zero value, and *posix_close*() is interrupted by a signal that is to be caught, then *posix_close*() may return -1 with *errno* set to \[EINTR\], in which case *fildes* shall be left open; however, it is unspecified whether *fildes* can subsequently be passed to any function except *close*() or *posix_close*() without error. If *flag* is invalid, *posix_close*() may fail with errno set to \[EINVAL\], but shall otherwise behave as if *flag* had been 0 and close *fildes*.

#### <span id="tag_17_81_04"></span>RETURN VALUE

> Upon successful completion, 0 shall be returned; otherwise, -1 shall be returned and *errno* set to indicate the error.

#### <span id="tag_17_81_05"></span>ERRORS

> The *close*() and *posix_close*() functions shall fail if:
>
> \[EBADF\]
>
> The *fildes* argument is not a open file descriptor.
>
> \[EINPROGRESS\]
>
> The function was interrupted by a signal and *fildes* was closed but the close operation is continuing asynchronously.
>
> The *close*() and *posix_close*() functions may fail if:
>
> \[EINTR\]
>
> The function was interrupted by a signal, POSIX_CLOSE_RESTART is defined as non-zero, and (in the case of *posix_close*()) the *flag* argument included POSIX_CLOSE_RESTART, in which case *fildes* is still open.
>
> \[EIO\]
>
> An I/O error occurred while reading from or writing to the file system.
>
> The *posix_close*() function may fail if:
>
> \[EINVAL\]
>
> The value of the *flag* argument is invalid.
>
> The *close*() and *posix_close*() functions shall not return an \[EAGAIN\] or \[EWOULDBLOCK\] error. If POSIX_CLOSE_RESTART is zero, the *close*() function shall not return an \[EINTR\] error. The *posix_close*() function shall not return an \[EINTR\] error unless *flag* includes a non-zero POSIX_CLOSE_RESTART.

------------------------------------------------------------------------

<div class="box">

*The following sections are informative.*

</div>

#### <span id="tag_17_81_06"></span>EXAMPLES

> ##### <span id="tag_17_81_06_01"></span>Reassigning a File Descriptor
>
> The following example closes the file descriptor associated with standard output for the current process, re-assigns standard output to a new file descriptor, and closes the original file descriptor to clean up. This example assumes that the file descriptor 0 (which is the descriptor for standard input) is not closed.
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
> Incidentally, this is exactly what could be achieved using:
>
>     dup2(pfd, 1);
>     close(pfd);
>
> ##### <span id="tag_17_81_06_02"></span>Closing a File Descriptor
>
> In the following example, *close*() is used to close a file descriptor after an unsuccessful attempt is made to associate that file descriptor with a stream.
>
>     #include <stdio.h>
>     #include <unistd.h>
>     #include <stdlib.h>
>
>
>     #define LOCKFILE "/etc/ptmp"
>     ...
>     int pfd;
>     FILE *fpfd;
>     ...
>     if ((fpfd = fdopen (pfd, "w")) == NULL) {
>         close(pfd);
>         unlink(LOCKFILE);
>         exit(1);
>     }
>     ...

#### <span id="tag_17_81_07"></span>APPLICATION USAGE

> An application that had used the *stdio* routine [*fopen*()](../functions/fopen.html) to open a file should use the corresponding [*fclose*()](../functions/fclose.html) routine rather than *close*(). Once a file is closed, the file descriptor no longer exists, since the integer corresponding to it no longer refers to a file.
>
> Implementations may use file descriptors that must be inherited into child processes for the child process to remain conforming, such as for message catalog or tracing purposes. Therefore, an application that calls *close*() on an arbitrary integer risks non-conforming behavior, and *close*() can only portably be used on file descriptor values that the application has obtained through explicit actions, as well as the three file descriptors corresponding to the standard file streams. In multi-threaded parent applications, the practice of calling *close*() in a loop after [*fork*()](../functions/fork.html) and before an *[exec](../functions/exec.html)* call in order to avoid a race condition of leaking an unintended file descriptor into a child process, is therefore unsafe, and the race should instead be combatted by opening all file descriptors with the FD_CLOEXEC bit set unless the file descriptor is intended to be inherited across *[exec](../functions/exec.html)*.
>
> Usage of *close*() on file descriptors STDIN_FILENO, STDOUT_FILENO, or STDERR_FILENO should immediately be followed by an operation to reopen these file descriptors. Unexpected behavior will result if any of these file descriptors is left in a closed state (for example, an \[EBADF\] error from [*perror*()](../functions/perror.html)) or if an unrelated [*open*()](../functions/open.html) or similar call later in the application accidentally allocates a file to one of these well-known file descriptors. Furthermore, a *close*() followed by a reopen operation (e.g., [*open*()](../functions/open.html), [*dup*()](../functions/dup.html), etc.) is not atomic; [*dup2*()](../functions/dup2.html) should be used to change standard file descriptors.

#### <span id="tag_17_81_08"></span>RATIONALE

> The use of interruptible device close routines should be discouraged to avoid problems with the implicit closes of file descriptors, such as by *[exec](../functions/exec.html)*, process termination, or [*dup2*()](../functions/dup2.html). This volume of POSIX.1-2024 only intends to permit such behavior by specifying the \[EINTR\] error condition for *close*() and *posix_close*() with non-zero POSIX_CLOSE_RESTART, to allow applications a portable way to resume waiting for an event associated with the close operation (for example, a tape drive rewinding) after receiving an interrupt. This standard also permits implementations to define POSIX_CLOSE_RESTART to 0 if they do not choose to provide a way to restart an interrupted close action. Although the file descriptor is left open on \[EINTR\], it might no longer be usable; that is, passing it to any function except *close*() or *posix_close*() might result in an error such as \[EIO\]. If an application must guarantee that data will not be lost, it is recommended that the application use [*fsync*()](../functions/fsync.html) or [*fdatasync*()](../functions/fdatasync.html) prior to the close operation, rather than leaving the close operation to deal with pending I/O and risk an interrupt.
>
> Earlier versions of this standard left the state of *fildes* unspecified after errors such as \[EINTR\] and \[EIO\]; and implementations differed on whether *close*() left *fildes* open after \[EINTR\]. This was unsatisfactory once threads were introduced, since multi-threaded applications need to know whether *fildes* has been closed. Applications cannot blindly call *close*() again, because if *fildes* was closed by the first call another thread could have been allocated a file descriptor with the same value as *fildes*, which must not be closed by the first thread. On the other hand, the alternative of never retrying *close*() would lead to a file descriptor leak in implementations where *close*() did not close *fildes*, although such a leak may be harmless if the process is about to exit or the file descriptor is marked FD_CLOEXEC and the process is about to be replaced by *[exec](../functions/exec.html)*. This standard introduced *posix_close*() with a *flag* argument that allows a choice between the two possible error behaviors, and leaves it unspecified which of the two behaviors is implemented by *close*() (although it is guaranteed to be one of the two behaviors of *posix_close*(), rather than leaving things completely unspecified as in earlier versions of the standard).
>
> Note that the standard requires that *close*() and *posix_close*() must leave *fildes* open after \[EINTR\] (in the cases where \[EINTR\] is permitted) and must close the file descriptor regardless of all other errors (except \[EBADF\], where *fildes* is already invalid). In general, portable applications should only retry a *close*() after checking for \[EINTR\] (and on implementations where POSIX_CLOSE_RESTART is defined to be zero, this retry loop will be dead code), and risk a file descriptor leak if a retry loop is not attempted. It should also be noted that \[EINTR\] is only possible if *close*() can be interrupted; if no signal handlers are installed, then *close*() will not be interrupted. Conversely, if a single-threaded application can guarantee that no file descriptors are opened or closed in signal handlers, then a retry loop without checking for \[EINTR\] will be harmless (since the retry will fail with \[EBADF\]), but guaranteeing that no external libraries introduce the use of threading can be difficult. There are additional guarantees for applications which will only ever be used on systems where POSIX_CLOSE_RESTART is defined as 0. These observations should help in determining whether an application needs to have its *close*() calls audited for replacement with *posix_close*().
>
> It should also be noted that the requirement for *posix_close*() with a *flag* of 0 to always close *fildes*, even if an error is reported, is similar to the requirements on [*fclose*()](../functions/fclose.html) to always release the stream, even if an error is encountered while flushing data.
>
> Implementations that previously always closed *fildes* can meet the new requirements by translating \[EINTR\] to \[EINPROGRESS\] in *close*(); and may define POSIX_CLOSE_RESTART to 0 rather than having to add restart semantics. On the other hand, implementations that previously left *fildes* open on \[EINTR\] can map that to *posix_close*() with POSIX_CLOSE_RESTART, and must add the semantics of *posix_close*() when *flag* is 0; one possibility is by calling the original *close*() implementation, checking for failure, and on \[EINTR\], using actions similar to [*dup2*()](../functions/dup2.html) to replace the incomplete close operation with another file descriptor that can be closed immediately by another call to the original *close*(), all before returning to the application. Either way, *close*() should always map to one of the two behaviors of *posix_close*(), and implementations are encouraged to keep the behavior of *close*() unchanged so as not to break implementation-specific expectations of older applications that were relying on behavior not specified by older versions of this standard.
>
> The standard developers considered introducing a thread-local variable that *close*() would set to indicate whether it had closed *fildes* when returning -1. However, this was rejected in favor of the simpler solution of tightening *close*() to guarantee that *fildes* is closed except for \[EINTR\], and exposing a choice of whether to expect \[EINTR\] by adding *posix_close*(). Additionally, while the name *posix_close*() is new to this standard, it is reminiscent of at least one implementation that introduced an alternate system call named *close_nocancel*() in order to allow an application to choose whether restart semantics were desired.
>
> Another consideration was whether implementations might return \[EAGAIN\] as an extension and whether *close*() should be required to leave the file descriptor open in this case, since \[EAGAIN\] normally implies an operation should be retried. It seemed very unlikely that any implementation would have a legitimate reason to return \[EAGAIN\] or \[EWOULDBLOCK\], and therefore this requirement would mean applications have to include code for an error case that will never be used. Therefore *close*() is now forbidden from returning \[EAGAIN\] and \[EWOULDBLOCK\] errors.
>
> Note that the requirement for *close*() on a socket to block for up to the current linger interval is not conditional on the O_NONBLOCK setting.
>
> The standard developers rejected a proposal to add *closefrom*() to the standard. Because the standard permits implementations to use inherited file descriptors as a means of providing a conforming environment for the child process, it is not possible to standardize an interface that closes arbitrary file descriptors above a certain value while still guaranteeing a conforming environment.

#### <span id="tag_17_81_09"></span>FUTURE DIRECTIONS

> None.

#### <span id="tag_17_81_10"></span>SEE ALSO

> [*dup*()](../functions/dup.html#), [](../functions/exec.html#tag_17_129)[exec](../functions/exec.html), [*exit*()](../functions/exit.html#tag_17_130), [*fclose*()](../functions/fclose.html#), [*fopen*()](../functions/fopen.html#), [*fork*()](../functions/fork.html#), [*open*()](../functions/open.html#), [*perror*()](../functions/perror.html#), [*unlink*()](../functions/unlink.html#tag_17_649)
>
> XBD [*\<unistd.h\>*](../basedefs/unistd.h.html)

#### <span id="tag_17_81_11"></span>CHANGE HISTORY

> First released in Issue 1. Derived from Issue 1 of the SVID.

#### <span id="tag_17_81_12"></span>Issue 5

> The DESCRIPTION is updated for alignment with the POSIX Realtime Extension.

#### <span id="tag_17_81_13"></span>Issue 6

> The DESCRIPTION related to a STREAMS-based file or pseudo-terminal is marked as part of the XSI STREAMS Option Group.
>
> The following new requirements on POSIX implementations derive from alignment with the Single UNIX Specification:
>
> - The \[EIO\] error condition is added as an optional error.
>
> - The DESCRIPTION is updated to describe the state of the *fildes* file descriptor as unspecified if an I/O error occurs and an \[EIO\] error condition is returned.
>
> Text referring to sockets is added to the DESCRIPTION.
>
> The DESCRIPTION is updated for alignment with IEEE Std 1003.1j-2000 by specifying that shared memory objects and memory mapped files (and not typed memory objects) are the types of memory objects to which the paragraph on last closes applies.
>
> IEEE Std 1003.1-2001/Cor 1-2002, item XSH/TC1/D6/12 is applied, correcting the XSH shaded text relating to the manager side of a pseudo-terminal. The reason for the change is that the behavior of pseudo-terminals and regular terminals should be as much alike as possible in this case; the change achieves that and matches historical behavior.

#### <span id="tag_17_81_14"></span>Issue 7

> Functionality relating to the XSI STREAMS option is marked obsolescent.
>
> Functionality relating to the Asynchronous Input and Output and Memory Mapped Files options is moved to the Base.
>
> Austin Group Interpretation 1003.1-2001 \#139 is applied, clarifying that the requirement for *close*() on a socket to block for up to the current linger interval is not conditional on the O_NONBLOCK setting.
>
> POSIX.1-2008, Technical Corrigendum 1, XSH/TC1-2008/0059 \[419\], XSH/TC1-2008/0060 \[149\], and XSH/TC1-2008/0061 \[149\] are applied.
>
> POSIX.1-2008, Technical Corrigendum 2, XSH/TC2-2008/0069 \[555\] is applied.

#### <span id="tag_17_81_15"></span>Issue 8

> Austin Group Defect 529 is applied, adding the *posix_close*() function and changing requirements for the *close*() function relating to \[EINTR\].
>
> Austin Group Defect 768 is applied, adding OFD-owned file locks.
>
> Austin Group Defect 1330 is applied, removing obsolescent interfaces.
>
> Austin Group Defect 1466 is applied, changing the terminology used for pseudo-terminal devices.
>
> Austin Group Defect 1525 is applied, clarifying that a socket is not destroyed until all file descriptors associated with it have been closed.

<div class="box">

*End of informative text.*

</div>

------------------------------------------------------------------------

 
