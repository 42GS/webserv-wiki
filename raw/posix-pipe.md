> Source: <https://pubs.opengroup.org/onlinepubs/9799919799/functions/pipe.html>
> Retrieved: 2026-10-29. Original HTML: kept next to this file as `.source.html`.
> Converted with pandoc 3.10 (`-f html -t gfm --wrap=none`, `pandoc/opengroup-body.lua`).

The Open Group Base Specifications Issue 8\
IEEE Std 1003.1-2024\
Copyright © 2001-2024 The IEEE and The Open Group

------------------------------------------------------------------------

<span id="top"></span> <span id="pipe"></span> <span id="tag_17_377"></span>

#### <span id="tag_17_377_01"></span>NAME

> pipe, pipe2 — create an interprocess channel

#### <span id="tag_17_377_02"></span>SYNOPSIS

> `#include <`[`unistd.h`](../basedefs/unistd.h.html)`>`\
> \
> `int pipe(int`` `*`fildes`*`[2]);`\
> `int pipe2(int`` `*`fildes`*`[2], int`` `*`flag`*`);`\

#### <span id="tag_17_377_03"></span>DESCRIPTION

> The *pipe*() function shall create a pipe and place two file descriptors, one each into the arguments *fildes*\[0\] and *fildes*\[1\], that refer to the open file descriptions for the read and write ends of the pipe, respectively. The file descriptors shall be allocated as described in [*2.6 File Descriptor Allocation*](../functions/V2_chap02.html#tag_16_06). The FD_CLOEXEC and FD_CLOFORK flags shall be clear on both file descriptors. The O_NONBLOCK flag shall be clear on both open file descriptions. (The [*fcntl*()](../functions/fcntl.html) function can be used to set this flag.)
>
> Data can be written to the file descriptor *fildes*\[1\] and read from the file descriptor *fildes*\[0\]. A read on the file descriptor *fildes*\[0\] shall access data written to the file descriptor *fildes*\[1\] on a first-in-first-out basis. It is unspecified whether *fildes*\[0\] is also open for writing and whether *fildes*\[1\] is also open for reading.
>
> A process has the pipe open for reading (correspondingly writing) if it has a file descriptor open that refers to the read end, *fildes*\[0\] (write end, *fildes*\[1\]).
>
> The pipe's user ID shall be set to the effective user ID of the calling process.
>
> The pipe's group ID shall be set to the effective group ID of the calling process.
>
> Upon successful completion, *pipe*() shall mark for update the last data access, last data modification, and last file status change timestamps of the pipe.
>
> The *pipe2*() function shall be equivalent to the *pipe*() function, except that the state of O_NONBLOCK on the new file descriptions and FD_CLOEXEC and FD_CLOFORK on the new file descriptors shall be determined solely by the *flag* argument, which can be constructed from a bitwise-inclusive OR of flags from the following list (provided by [*\<fcntl.h\>*](../basedefs/fcntl.h.html)):
>
> O_CLOEXEC
>
> Atomically set the FD_CLOEXEC flag on both new file descriptors.
>
> O_CLOFORK
>
> Atomically set the FD_CLOFORK flag on both new file descriptors.
>
> O_NONBLOCK
>
> Set the O_NONBLOCK file status flag on both new file descriptions.

#### <span id="tag_17_377_04"></span>RETURN VALUE

> Upon successful completion, 0 shall be returned; otherwise, -1 shall be returned and *errno* set to indicate the error, no file descriptors shall be allocated and the contents of *fildes* shall be left unmodified.

#### <span id="tag_17_377_05"></span>ERRORS

> The *pipe*() and *pipe2*() functions shall fail if:
>
> \[EMFILE\]
>
> All, or all but one, of the file descriptors available to the process are currently open.
>
> \[ENFILE\]
>
> The number of simultaneously open files in the system would exceed a system-imposed limit.
>
> The *pipe2*() function may fail if:
>
> \[EINVAL\]
>
> The value of the *flag* argument is invalid.

------------------------------------------------------------------------

<div class="box">

*The following sections are informative.*

</div>

#### <span id="tag_17_377_06"></span>EXAMPLES

> ##### <span id="tag_17_377_06_01"></span>Using a Pipe to Pass Data Between a Parent Process and a Child Process
>
> The following example demonstrates the use of a pipe to transfer data between a parent process and a child process. Error handling is excluded, but otherwise this code demonstrates good practice when using pipes: after the [*fork*()](../functions/fork.html) the two processes close the unused ends of the pipe before they commence transferring data.
>
>     #include <stdlib.h>
>     #include <unistd.h>
>     ...
>
>
>     int fildes[2];
>     const int BSIZE = 100;
>     char buf[BSIZE];
>     ssize_t nbytes;
>     int status;
>
>
>     status = pipe(fildes);
>     if (status == -1 ) {
>         /* an error occurred */
>         ...
>     }
>
>
>     switch (fork()) {
>     case -1: /* Handle error */
>         break;
>
>
>     case 0:  /* Child - reads from pipe */
>         close(fildes[1]);                       /* Write end is unused */
>         nbytes = read(fildes[0], buf, BSIZE);   /* Get data from pipe */
>         /* At this point, a further read would see end-of-file ... */
>         close(fildes[0]);                       /* Finished with pipe */
>         exit(EXIT_SUCCESS);
>
>
>     default:  /* Parent - writes to pipe */
>         close(fildes[0]);                       /* Read end is unused */
>         write(fildes[1], "Hello world\n", 12);  /* Write data on pipe */
>         close(fildes[1]);                       /* Child will see EOF */
>         exit(EXIT_SUCCESS);
>     }

#### <span id="tag_17_377_07"></span>APPLICATION USAGE

> None.

#### <span id="tag_17_377_08"></span>RATIONALE

> The wording carefully avoids using the verb "to open" in order to avoid any implication of use of [*open*()](../functions/open.html); see also [*write*()](../functions/write.html).
>
> The O_CLOEXEC and O_CLOFORK flags of *pipe2*() are necessary to avoid a data race in multi-threaded applications. Without O_CLOFORK, a file descriptor is leaked into a child process created by one thread in the window between another thread creating a file descriptor with *pipe*() and then using [*fcntl*()](../functions/fcntl.html) to set the FD_CLOFORK flag. Without O_CLOEXEC, a file descriptor intentionally inherited by child processes is similarly leaked into an executed program if FD_CLOEXEC is not set atomically.
>
> Since pipes are often used for communication between a parent and child process, O_CLOFORK has to be used with care in order for the pipe to be usable. If the parent will be writing and the child will be reading, O_CLOFORK should be used when creating the pipe, and then [*fcntl*()](../functions/fcntl.html) should be used to clear FD_CLOFORK for the read side of the pipe. This prevents the write side from leaking into other children, ensuring the child will get end-of-file when the parent closes the write side (although the read side can still be leaked). If the parent will be reading and the child will be writing, there is no way to prevent the write side being leaked (short of preventing other threads from creating child processes) in order to ensure the parent gets end-of-file when the child closes the write side, and so the two processes should use an alternative method of indicating the end of communications.
>
> Arranging for FD_CLOEXEC to be set appropriately is more straightforward. The parent should use O_CLOEXEC when creating the pipe and the child should clear FD_CLOEXEC on the side to be passed to the new program before calling an *[exec](../functions/exec.html)* family function to execute it.
>
> The O_NONBLOCK flag is for convenience in avoiding additional [*fcntl*()](../functions/fcntl.html) calls.

#### <span id="tag_17_377_09"></span>FUTURE DIRECTIONS

> None.

#### <span id="tag_17_377_10"></span>SEE ALSO

> [*2.6 File Descriptor Allocation*](../functions/V2_chap02.html#tag_16_06), [*fcntl*()](../functions/fcntl.html#), [*read*()](../functions/read.html#tag_17_476), [*write*()](../functions/write.html#tag_17_699)
>
> XBD [*\<fcntl.h\>*](../basedefs/fcntl.h.html), [*\<unistd.h\>*](../basedefs/unistd.h.html)

#### <span id="tag_17_377_11"></span>CHANGE HISTORY

> First released in Issue 1. Derived from Issue 1 of the SVID.

#### <span id="tag_17_377_12"></span>Issue 6

> The following new requirements on POSIX implementations derive from alignment with the Single UNIX Specification:
>
> - The DESCRIPTION is updated to indicate that certain dispositions of *fildes*\[0\] and *fildes*\[1\] are unspecified.
>
> IEEE Std 1003.1-2001/Cor 2-2004, item XSH/TC2/D6/65 is applied, adding the example to the EXAMPLES section.\

#### <span id="tag_17_377_13"></span>Issue 7

> SD5-XSH-ERN-156 is applied, updating the DESCRIPTION to state the setting of the pipe's user ID and group ID.
>
> Changes are made related to support for finegrained timestamps.
>
> POSIX.1-2008, Technical Corrigendum 2, XSH/TC2-2008/0247 \[835\] and XSH/TC2-2008/0248 \[467,835\] are applied.

#### <span id="tag_17_377_14"></span>Issue 8

> Austin Group Defects 411, 1318, and 1577 are applied, adding *pipe2*() and FD_CLOFORK.
>
> Austin Group Defect 1576 is applied, adding the word "respectively".

<div class="box">

*End of informative text.*

</div>

------------------------------------------------------------------------

 
