> Source: <https://pubs.opengroup.org/onlinepubs/9799919799/functions/write.html>
> Retrieved: 2026-10-29. Original HTML: kept next to this file as `.source.html`.
> Converted with pandoc 3.10 (`-f html -t gfm --wrap=none`, `pandoc/opengroup-body.lua`).

The Open Group Base Specifications Issue 8\
IEEE Std 1003.1-2024\
Copyright © 2001-2024 The IEEE and The Open Group

------------------------------------------------------------------------

<span id="top"></span> <span id="write"></span> <span id="tag_17_699"></span>

#### <span id="tag_17_699_01"></span>NAME

> pwrite, write — write on a file

#### <span id="tag_17_699_02"></span>SYNOPSIS

> `#include <`[`unistd.h`](../basedefs/unistd.h.html)`>`\
> \
> `ssize_t pwrite(int`` `*`fildes`*`, const void *`*`buf`*`, size_t`` `*`nbyte`*`,`\
> `       off_t`` `*`offset`*`);`\
> `ssize_t write(int`` `*`fildes`*`, const void *`*`buf`*`, size_t`` `*`nbyte`*`);`\

#### <span id="tag_17_699_03"></span>DESCRIPTION

> The *write*() function shall attempt to write *nbyte* bytes from the buffer pointed to by *buf* to the file associated with the open file descriptor, *fildes*.
>
> Before any action described below is taken, and if *nbyte* is zero and the file is a regular file, the *write*() function may detect and return errors as described below. In the absence of errors, or if error detection is not performed, the *write*() function shall return zero and have no other results. If *nbyte* is zero and the file is not a regular file, the results are unspecified.
>
> On a regular file or other file capable of seeking, the actual writing of data shall proceed from the position in the file indicated by the file offset associated with *fildes*. Before successful return from *write*(), the file offset shall be incremented by the number of bytes actually written. On a regular file, if the position of the last byte written is greater than or equal to the length of the file, the length of the file shall be set to this position plus one.
>
> On a file not capable of seeking, writing shall always take place starting at the current position. The value of a file offset associated with such a device is undefined.
>
> If the O_APPEND flag of the file status flags is set, the file offset shall be set to the end of the file prior to each write and no intervening file modification operation shall occur between changing the file offset and the write operation.
>
> If a *write*() requests that more bytes be written than there is room for (for example, the file size limit of the process or the physical end of a medium), only as many bytes as there is room for shall be written. For example, suppose there is space for 20 bytes more in a file before reaching a limit. A write of 512 bytes will return 20. The next write of a non-zero number of bytes would give a failure return (except as noted below).
>
> If the request would cause the file size to exceed the soft file size limit for the process and there is no room for any bytes to be written, the request shall fail <sup>\[[XSI](javascript:open_code('XSI'))\]</sup> <img src="../images/opt-start.gif" data-border="0" alt="[Option Start]" />  and the implementation shall generate a SIGXFSZ signal for the thread. <img src="../images/opt-end.gif" data-border="0" alt="[Option End]" />
>
> If *write*() is interrupted by a signal before it writes any data, it shall return -1 with *errno* set to \[EINTR\].
>
> If *write*() is interrupted by a signal after it successfully writes some data, it shall return the number of bytes written.
>
> If the value of *nbyte* is greater than {SSIZE_MAX}, the result is implementation-defined.
>
> After a *write*() to a regular file has successfully returned:
>
> - Any successful [*read*()](../functions/read.html) from each byte position in the file that was modified by that write shall return the data specified by the *write*() for that position until such byte positions are again modified.
>
> - Any subsequent successful *write*() to the same byte position in the file shall overwrite that file data.
>
> \
>
> Write requests to a pipe or FIFO shall be handled in the same way as a regular file with the following exceptions:
>
> - There is no file offset associated with a pipe or FIFO, hence each write request shall append to the end of the pipe or FIFO.
>
> - Write requests of {PIPE_BUF} bytes or less shall not be interleaved with data from other threads performing write operations on the same pipe or FIFO. Writes of greater than {PIPE_BUF} bytes may have data interleaved, on arbitrary boundaries, with write operations by other threads, whether or not the O_NONBLOCK flag of the file status flags is set.
>
> - If the O_NONBLOCK flag is clear, a write request may cause the thread to block, but on normal completion it shall return *nbyte*.
>
> - If the O_NONBLOCK flag is set, *write*() requests shall be handled differently, in the following ways:
>
>   - The *write*() function shall not block the thread.
>
>   - A write request for {PIPE_BUF} or fewer bytes shall have the following effect: if there is sufficient space available in the pipe or FIFO, *write*() shall transfer all the data and return the number of bytes requested. Otherwise, *write*() shall transfer no data and return -1 with *errno* set to \[EAGAIN\].
>
>   - A write request for more than {PIPE_BUF} bytes shall cause one of the following:
>
>     - When at least one byte can be written, transfer what it can and return the number of bytes written. When all data previously written to the pipe or FIFO is read, it shall transfer at least {PIPE_BUF} bytes.
>
>     - When no data can be written, transfer no data, and return -1 with *errno* set to \[EAGAIN\].
>
> When attempting to write to a file descriptor (other than a pipe or FIFO) that supports non-blocking writes and cannot accept the data immediately:
>
> - If the O_NONBLOCK flag is clear, *write*() shall block the calling thread until the data can be accepted.
>
> - If the O_NONBLOCK flag is set, *write*() shall not block the thread. If some data can be written without blocking the thread, *write*() shall write what it can and return the number of bytes written. Otherwise, it shall return -1 and set *errno* to \[EAGAIN\].
>
> Upon successful completion, where *nbyte* is greater than 0, *write*() shall mark for update the last data modification and last file status change timestamps of the file, and if the file is a regular file, the S_ISUID and S_ISGID bits of the file mode may be cleared.
>
> For regular files, no data transfer shall occur past the offset maximum established in the open file description associated with *fildes*.
>
> If *fildes* refers to a socket, *write*() shall be equivalent to [*send*()](../functions/send.html) with no flags set.
>
> <sup>\[[SIO](javascript:open_code('SIO'))\]</sup> <img src="../images/opt-start.gif" data-border="0" alt="[Option Start]" /> If the O_DSYNC bit has been set, write I/O operations on the file descriptor shall complete as defined by synchronized I/O data integrity completion.
>
> If the O_SYNC bit has been set, write I/O operations on the file descriptor shall complete as defined by synchronized I/O file integrity completion. <img src="../images/opt-end.gif" data-border="0" alt="[Option End]" />
>
> <sup>\[[SHM](javascript:open_code('SHM'))\]</sup> <img src="../images/opt-start.gif" data-border="0" alt="[Option Start]" /> If *fildes* refers to a shared memory object, the result of the *write*() function is unspecified. <img src="../images/opt-end.gif" data-border="0" alt="[Option End]" />
>
> <sup>\[[TYM](javascript:open_code('TYM'))\]</sup> <img src="../images/opt-start.gif" data-border="0" alt="[Option Start]" /> If *fildes* refers to a typed memory object, the result of the *write*() function is unspecified. <img src="../images/opt-end.gif" data-border="0" alt="[Option End]" />
>
> The *pwrite*() function shall be equivalent to *write*(), except that it writes into a given position and does not change the file offset (regardless of whether O_APPEND is set). The first three arguments to *pwrite*() are the same as *write*() with the addition of a fourth argument *offset* for the desired position inside the file. An attempt to perform a *pwrite*() on a file that is incapable of seeking shall result in an error.

#### <span id="tag_17_699_04"></span>RETURN VALUE

> Upon successful completion, these functions shall return the number of bytes actually written to the file associated with *fildes*. This number shall never be greater than *nbyte*. Otherwise, -1 shall be returned and *errno* set to indicate the error.

#### <span id="tag_17_699_05"></span>ERRORS

> These functions shall fail if:
>
> \[EAGAIN\]
>
> The file is neither a pipe, nor a FIFO, nor a socket, the O_NONBLOCK flag is set for the file descriptor, and the thread would be delayed in the *write*() operation.
>
> \[EBADF\]
>
> The *fildes* argument is not a valid file descriptor open for writing.
>
> \[EFBIG\]
>
> An attempt was made to write a file that exceeds the implementation-defined maximum file size and there was no room for any bytes to be written.
>
> \[EFBIG\]
>
> An attempt was made to write a file that exceeds the file size limit of the process, and there was no room for any bytes to be written. <sup>\[[XSI](javascript:open_code('XSI'))\]</sup> <img src="../images/opt-start.gif" data-border="0" alt="[Option Start]" />  A SIGXFSZ signal shall also be generated for the thread. <img src="../images/opt-end.gif" data-border="0" alt="[Option End]" />
>
> \[EFBIG\]
>
> The file is a regular file, *nbyte* is greater than 0, and the starting position is greater than or equal to the offset maximum established in the open file description associated with *fildes*.
>
> \[EINTR\]
>
> The write operation was terminated due to the receipt of a signal, and no data was transferred.
>
> \[EIO\]
>
> The process is a member of a background process group attempting to write to its controlling terminal, TOSTOP is set, the calling thread is not blocking SIGTTOU, the process is not ignoring SIGTTOU, and the process group of the process is orphaned. This error may also be returned under implementation-defined conditions.
>
> \[ENOSPC\]
>
> There was no free space remaining on the device containing the file.
>
> The *pwrite*() function shall fail if:
>
> \[EINVAL\]
>
> The file is a regular file or block special file, and the *offset* argument is negative. The file offset shall remain unchanged.
>
> \[ESPIPE\]
>
> The file is incapable of seeking.
>
> The *write*() function shall fail if:
>
> \[EAGAIN\]
>
> The file is a pipe or FIFO, the O_NONBLOCK flag is set for the file descriptor, and the thread would be delayed in the write operation.
>
> \[EAGAIN\] or \[EWOULDBLOCK\]
>
> The file is a socket, the O_NONBLOCK flag is set for the file descriptor, and the thread would be delayed in the write operation.
>
> \[ECONNRESET\]
>
> A write was attempted on a socket that is not connected.
>
> \[EPIPE\]
>
> An attempt is made to write to a pipe or FIFO that is not open for reading by any process, or that only has one end open. A SIGPIPE signal shall also be sent to the thread.
>
> \[EPIPE\]
>
> A write was attempted on a socket that is shut down for writing, or is no longer connected. In the latter case, if the socket is of type SOCK_STREAM, a SIGPIPE signal shall also be sent to the thread.
>
> These functions may fail if:
>
> \[EIO\]
>
> A physical I/O error has occurred.
>
> \[ENOBUFS\]
>
> Insufficient resources were available in the system to perform the operation.
>
> \[ENXIO\]
>
> A request was made of a nonexistent device, or the request was outside the capabilities of the device.
>
> The *write*() function may fail if:
>
> \[EACCES\]
>
> A write was attempted on a socket and the calling process does not have appropriate privileges.
>
> \[ENETDOWN\]
>
> A write was attempted on a socket and the local network interface used to reach the destination is down.
>
> \[ENETUNREACH\]
>
> A write was attempted on a socket and no route to the network is present.

------------------------------------------------------------------------

<div class="box">

*The following sections are informative.*

</div>

#### <span id="tag_17_699_06"></span>EXAMPLES

> ##### <span id="tag_17_699_06_01"></span>Writing from a Buffer
>
> The following example writes data from the buffer pointed to by *buf* to the file associated with the file descriptor *fd*.
>
>     #include <sys/types.h>
>     #include <string.h>
>     ...
>     char buf[20];
>     size_t nbytes;
>     ssize_t bytes_written;
>     int fd;
>     ...
>     strcpy(buf, "This is a test\n");
>     nbytes = strlen(buf);
>
>
>     bytes_written = write(fd, buf, nbytes);
>     ...

#### <span id="tag_17_699_07"></span>APPLICATION USAGE

> None.

#### <span id="tag_17_699_08"></span>RATIONALE

> See also the RATIONALE section in [*read*()](../functions/read.html).
>
> An attempt to write to a pipe or FIFO has several major characteristics:
>
> - *Atomic/non-atomic*: A write is atomic if the whole amount written in one operation is not interleaved with data from any other thread. This is useful when there are multiple writers sending data to a single reader. Applications need to know how large a write request can be expected to be performed atomically. This maximum is called {PIPE_BUF}. This volume of POSIX.1-2024 does not say whether write requests for more than {PIPE_BUF} bytes are atomic, but requires that writes of {PIPE_BUF} or fewer bytes shall be atomic.
>
> - *Blocking/immediate*: Blocking is only possible with O_NONBLOCK clear. If there is enough space for all the data requested to be written immediately, the implementation should do so. Otherwise, the calling thread may block; that is, pause until enough space is available for writing. The effective size of a pipe or FIFO (the maximum amount that can be written in one operation without blocking) may vary dynamically, depending on the implementation, so it is not possible to specify a fixed value for it.
>
> - *Complete/partial/deferred*: A write request:
>
>       int fildes;
>       size_t nbyte;
>       ssize_t ret;
>       char *buf;
>
>
>       ret = write(fildes, buf, nbyte);
>
>   may return:
>
>   Complete
>
>   *ret*=*nbyte*
>
>   Partial
>
>   *ret*\<*nbyte*
>
>   This shall never happen if *nbyte*\<={PIPE_BUF}. If it does happen (with *nbyte*\>{PIPE_BUF}), this volume of POSIX.1-2024 does not guarantee atomicity, even if *ret*\<={PIPE_BUF}, because atomicity is guaranteed according to the amount *requested*, not the amount *written*.
>
>   Deferred:
>
>   *ret*=-1, *errno*=\[EAGAIN\]
>
>   This error indicates that a later request may succeed. It does not indicate that it *shall* succeed, even if *nbyte*\<={PIPE_BUF}, because if no process reads from the pipe or FIFO, the write never succeeds. An application could usefully count the number of times \[EAGAIN\] is caused by a particular value of *nbyte*\>{PIPE_BUF} and perhaps do later writes with a smaller value, on the assumption that the effective size of the pipe or FIFO may have decreased.
>
>   Partial and deferred writes are only possible with O_NONBLOCK set.
>
> The relations of these properties are shown in the following tables:
>
> <table data-border="1" data-cellpadding="3" data-align="center">
> <thead>
> <tr data-valign="top">
> <th colspan="4" style="text-align: center;"><p><strong>Write to a Pipe or FIFO with O_NONBLOCK <em>clear</em></strong></p></th>
> </tr>
> </thead>
> <tbody>
> <tr data-valign="top">
> <th style="text-align: center;"><p><strong>Immediately Writable:</strong></p></th>
> <th style="text-align: center;"><p><strong>None</strong></p></th>
> <th style="text-align: center;"><p><strong>Some</strong></p></th>
> <th style="text-align: center;"><p><em>nbyte</em></p></th>
> </tr>
> &#10;<tr data-valign="top">
> <td style="text-align: left;"><p><em>nbyte</em>&lt;={PIPE_BUF}</p></td>
> <td style="text-align: left;"><p>Atomic blocking <em>nbyte</em></p></td>
> <td style="text-align: left;"><p>Atomic blocking <em>nbyte</em></p></td>
> <td style="text-align: left;"><p>Atomic immediate <em>nbyte</em></p></td>
> </tr>
> <tr data-valign="top">
> <td style="text-align: left;"><p><em>nbyte</em>&gt;{PIPE_BUF}</p></td>
> <td style="text-align: left;"><p>Blocking <em>nbyte</em></p></td>
> <td style="text-align: left;"><p>Blocking <em>nbyte</em></p></td>
> <td style="text-align: left;"><p>Blocking <em>nbyte</em></p></td>
> </tr>
> </tbody>
> </table>
>
> If the O_NONBLOCK flag is clear, a write request shall block if the amount writable immediately is less than that requested. If the flag is set (by [*fcntl*()](../functions/fcntl.html)), a write request shall never block.
>
> <table data-border="1" data-cellpadding="3" data-align="center">
> <thead>
> <tr data-valign="top">
> <th colspan="4" style="text-align: center;"><p><strong>Write to a Pipe or FIFO with O_NONBLOCK <em>set</em></strong></p></th>
> </tr>
> </thead>
> <tbody>
> <tr data-valign="top">
> <th style="text-align: center;"><p><strong>Immediately Writable:</strong></p></th>
> <th style="text-align: center;"><p><strong>None</strong></p></th>
> <th style="text-align: center;"><p><strong>Some</strong></p></th>
> <th style="text-align: center;"><p><em>nbyte</em></p></th>
> </tr>
> &#10;<tr data-valign="top">
> <td style="text-align: left;"><p><em>nbyte</em>&lt;={PIPE_BUF}</p></td>
> <td style="text-align: left;"><p>-1, [EAGAIN]</p></td>
> <td style="text-align: left;"><p>-1, [EAGAIN]</p></td>
> <td style="text-align: left;"><p>Atomic <em>nbyte</em></p></td>
> </tr>
> <tr data-valign="top">
> <td style="text-align: left;"><p><em>nbyte</em>&gt;{PIPE_BUF}</p></td>
> <td style="text-align: left;"><p>-1, [EAGAIN]</p></td>
> <td style="text-align: left;"><p>&lt;<em>nbyte</em> or -1, [EAGAIN]</p></td>
> <td style="text-align: left;"><p>&lt;=<em>nbyte</em> or -1, [EAGAIN]</p></td>
> </tr>
> </tbody>
> </table>
>
> There is no exception regarding partial writes when O_NONBLOCK is set. With the exception of writing to an empty pipe or FIFO, this volume of POSIX.1-2024 does not specify exactly when a partial write is performed since that would require specifying internal details of the implementation. Every application should be prepared to handle partial writes when O_NONBLOCK is set and the requested amount is greater than {PIPE_BUF}, just as every application should be prepared to handle partial writes on other kinds of file descriptors.
>
> The intent of forcing writing at least one byte if any can be written is to assure that each write makes progress if there is any room in the pipe or FIFO. If the pipe or FIFO is empty, {PIPE_BUF} bytes must be written; if not, at least some progress must have been made.
>
> Where this volume of POSIX.1-2024 requires -1 to be returned and *errno* set to \[EAGAIN\], most historical implementations return zero (with the O_NDELAY flag set, which is the historical predecessor of O_NONBLOCK, but is not itself in this volume of POSIX.1-2024). The error indications in this volume of POSIX.1-2024 were chosen so that an application can distinguish these cases from end-of-file. While *write*() cannot receive an indication of end-of-file, [*read*()](../functions/read.html) can, and the two functions have similar return values. Also, some existing systems (for example, Eighth Edition) permit a write of zero bytes to mean that the reader should get an end-of-file indication; for those systems, a return value of zero from *write*() indicates a successful write of an end-of-file indication.
>
> Implementations are allowed, but not required, to perform error checking for *write*() requests of zero bytes.
>
> The concept of a {PIPE_MAX} limit (indicating the maximum number of bytes that can be written to a pipe or FIFO in a single operation) was considered, but rejected, because this concept would unnecessarily limit application writing.
>
> See also the discussion of O_NONBLOCK in [*read*()](../functions/read.html).
>
> Writes can be serialized with respect to other reads and writes. If a [*read*()](../functions/read.html) of file data can be proven (by any means) to occur after a *write*() of the data, it must reflect that *write*(), even if the calls are made by different threads. A similar requirement applies to multiple write operations to the same file position. This is needed to guarantee the propagation of data from *write*() calls to subsequent [*read*()](../functions/read.html) calls. This requirement is particularly significant for networked file systems, where some caching schemes violate these semantics.
>
> Note that this is specified in terms of [*read*()](../functions/read.html) and *write*(). The XSI extensions [*readv*()](../functions/readv.html) and [*writev*()](../functions/writev.html) also obey these semantics. A new "high-performance" write analog that did not follow these serialization requirements would also be permitted by this wording. This volume of POSIX.1-2024 is also silent about any effects of application-level caching (such as that done by *stdio*).
>
> This volume of POSIX.1-2024 does not specify the value of the file offset after an error is returned; there are too many cases. For programming errors, such as \[EBADF\], the concept is meaningless since no file is involved. For errors that are detected immediately, such as \[EAGAIN\], clearly the pointer should not change. After an interrupt or hardware error, however, an updated value would be very useful and is the behavior of many implementations.
>
> This volume of POSIX.1-2024 does not specify the behavior of concurrent writes to a regular file from multiple threads, except that each write is atomic (see [*2.9.7 Thread Interactions with File Operations*](../functions/V2_chap02.html#tag_16_09_07)). Applications should use some form of concurrency control.
>
> This volume of POSIX.1-2024 intentionally does not specify any *pwrite*() errors related to pipes, FIFOs, and sockets other than \[ESPIPE\].

#### <span id="tag_17_699_09"></span>FUTURE DIRECTIONS

> None.

#### <span id="tag_17_699_10"></span>SEE ALSO

> [*chmod*()](../functions/chmod.html#tag_17_72), [*creat*()](../functions/creat.html#), [*dup*()](../functions/dup.html#), [*fcntl*()](../functions/fcntl.html#), [*getrlimit*()](../functions/getrlimit.html#), [*lseek*()](../functions/lseek.html#), [*open*()](../functions/open.html#), [*pipe*()](../functions/pipe.html#), [*read*()](../functions/read.html#tag_17_476), [*writev*()](../functions/writev.html#)
>
> XBD [*\<limits.h\>*](../basedefs/limits.h.html), [*\<sys/uio.h\>*](../basedefs/sys_uio.h.html), [*\<unistd.h\>*](../basedefs/unistd.h.html)

#### <span id="tag_17_699_11"></span>CHANGE HISTORY

> First released in Issue 1. Derived from Issue 1 of the SVID.

#### <span id="tag_17_699_12"></span>Issue 5

> The DESCRIPTION is updated for alignment with the POSIX Realtime Extension and the POSIX Threads Extension.
>
> Large File Summit extensions are added.
>
> The *pwrite*() function is added.

#### <span id="tag_17_699_13"></span>Issue 6

> The DESCRIPTION states that the *write*() function does not block the thread. Previously this said "process" rather than "thread".
>
> The DESCRIPTION and ERRORS sections are updated so that references to STREAMS are marked as part of the XSI STREAMS Option Group.
>
> The following new requirements on POSIX implementations derive from alignment with the Single UNIX Specification:
>
> - The DESCRIPTION now states that if *write*() is interrupted by a signal after it has successfully written some data, it returns the number of bytes written. In the POSIX.1-1988 standard, it was optional whether *write*() returned the number of bytes written, or whether it returned -1 with *errno* set to \[EINTR\]. This is a FIPS requirement.
> - The following changes are made to support large files:
>   - For regular files, no data transfer occurs past the offset maximum established in the open file description associated with the *fildes*.
>   - A second \[EFBIG\] error condition is added.
> - The \[EIO\] error condition is added.
> - The \[EPIPE\] error condition is added for when a pipe has only one end open.
> - The \[ENXIO\] optional error condition is added.
>
> Text referring to sockets is added to the DESCRIPTION.
>
> The following changes were made to align with the IEEE P1003.1a draft standard:
>
> - The effect of reading zero bytes is clarified.
>
> The DESCRIPTION is updated for alignment with IEEE Std 1003.1j-2000 by specifying that *write*() results are unspecified for typed memory objects.
>
> The following error conditions are added for operations on sockets: \[EAGAIN\], \[EWOULDBLOCK\], \[ECONNRESET\], \[ENOTCONN\], and \[EPIPE\].
>
> The \[EIO\] error is made optional.
>
> The \[ENOBUFS\] error is added for sockets.
>
> The following error conditions are added for operations on sockets: \[EACCES\], \[ENETDOWN\], and \[ENETUNREACH\].
>
> The [*writev*()](../functions/writev.html) function is split out into a separate reference page.
>
> IEEE Std 1003.1-2001/Cor 2-2004, item XSH/TC2/D6/146 is applied, updating text in the ERRORS section from "a SIGPIPE signal is generated to the calling process" to "a SIGPIPE signal shall also be sent to the thread".
>
> IEEE Std 1003.1-2001/Cor 2-2004, item XSH/TC2/D6/147 is applied, making a correction to the RATIONALE.

#### <span id="tag_17_699_14"></span>Issue 7

> The *pwrite*() function is moved from the XSI option to the Base.
>
> Functionality relating to the XSI STREAMS option is marked obsolescent.
>
> SD5-XSH-ERN-160 is applied, updating the DESCRIPTION to clarify the requirements for the *pwrite*() function, and to change the use of the phrase "file pointer" to "file offset".
>
> POSIX.1-2008, Technical Corrigendum 1, XSH/TC1-2008/0742 \[219\], XSH/TC1-2008/0743 \[215\], XSH/TC1-2008/0744 \[79\], and XSH/TC1-2008/0745 \[215\] are applied.
>
> POSIX.1-2008, Technical Corrigendum 2, XSH/TC2-2008/0401 \[676,710\] and XSH/TC2-2008/0402 \[966\] are applied.

#### <span id="tag_17_699_15"></span>Issue 8

> Austin Group Defect 308 is applied, clarifying the handling of \[EFBIG\] errors.
>
> Austin Group Defect 1330 is applied, removing obsolescent interfaces.
>
> Austin Group Defect 1430 is applied, clarifying that requirements relating to data interleaving on pipes and FIFOs apply to write operations in other threads, not just other processes, and changing some uses of "pipe" to "pipe or FIFO".
>
> Austin Group Defect 1669 is applied, removing XSI shading from part of the \[EFBIG\] error relating to the file size limit for the process.

<div class="box">

*End of informative text.*

</div>

------------------------------------------------------------------------

 
