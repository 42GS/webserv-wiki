> Source: <https://pubs.opengroup.org/onlinepubs/9799919799/functions/read.html>
> Retrieved: 2026-10-29. Original HTML: kept next to this file as `.source.html`.
> Converted with pandoc 3.10 (`-f html -t gfm --wrap=none`, `pandoc/opengroup-body.lua`).

The Open Group Base Specifications Issue 8\
IEEE Std 1003.1-2024\
Copyright © 2001-2024 The IEEE and The Open Group

------------------------------------------------------------------------

<span id="top"></span> <span id="read"></span> <span id="tag_17_476"></span>

#### <span id="tag_17_476_01"></span>NAME

> pread, read — read from a file

#### <span id="tag_17_476_02"></span>SYNOPSIS

> `#include <`[`unistd.h`](../basedefs/unistd.h.html)`>`\
> \
> `ssize_t pread(int`` `*`fildes`*`, void *`*`buf`*`, size_t`` `*`nbyte`*`, off_t`` `*`offset`*`);`\
> `ssize_t read(int`` `*`fildes`*`, void *`*`buf`*`, size_t`` `*`nbyte`*`);`\

#### <span id="tag_17_476_03"></span>DESCRIPTION

> The *read*() function shall attempt to read *nbyte* bytes from the file associated with the open file descriptor, *fildes*, into the buffer pointed to by *buf*. The behavior of multiple concurrent reads on the same pipe, FIFO, or terminal device is unspecified.
>
> Before any action described below is taken, and if *nbyte* is zero, the *read*() function may detect and return errors as described below. In the absence of errors, or if error detection is not performed, the *read*() function shall return zero and have no other results.
>
> On files that support seeking (for example, a regular file), the *read*() shall start at a position in the file given by the file offset associated with *fildes*. The file offset shall be incremented by the number of bytes actually read.
>
> Files that do not support seeking—for example, terminals—always read from the current position. The value of a file offset associated with such a file is undefined.
>
> No data transfer shall occur past the current end-of-file. If the starting position is at or after the end-of-file, 0 shall be returned. If the file refers to a device special file, the result of subsequent *read*() requests is implementation-defined.
>
> If the value of *nbyte* is greater than {SSIZE_MAX}, the result is implementation-defined.
>
> When attempting to read from an empty pipe or FIFO:
>
> - If no process has the pipe open for writing, *read*() shall return 0 to indicate end-of-file.
>
> - If some process has the pipe open for writing and O_NONBLOCK is set, *read*() shall return -1 and set *errno* to \[EAGAIN\].
>
> - If some process has the pipe open for writing and O_NONBLOCK is clear, *read*() shall block the calling thread until some data is written or the pipe is closed by all processes that had the pipe open for writing.
>
> When attempting to read a file (other than a pipe or FIFO) that supports non-blocking reads and has no data currently available:
>
> - If O_NONBLOCK is set, *read*() shall return -1 and set *errno* to \[EAGAIN\].
>
> - If O_NONBLOCK is clear, *read*() shall block the calling thread until some data becomes available.
>
> - The use of the O_NONBLOCK flag has no effect if there is some data available.
>
> The *read*() function reads data previously written to a file. If any portion of a regular file prior to the end-of-file has not been written, *read*() shall return bytes with value 0. For example, [*lseek*()](../functions/lseek.html) allows the file offset to be set beyond the end of existing data in the file. If data is later written at this point, subsequent reads in the gap between the previous end of data and the newly written data shall return bytes with value 0 until data is written into the gap.
>
> Upon successful completion, where *nbyte* is greater than 0, *read*() shall mark for update the last data access timestamp of the file, and shall return the number of bytes read. This number shall never be greater than *nbyte*. The value returned may be less than *nbyte* if the number of bytes left in the file is less than *nbyte*, if the *read*() request was interrupted by a signal, or if the file is a pipe or FIFO or special file and has fewer than *nbyte* bytes immediately available for reading. For example, a *read*() from a file associated with a terminal may return one typed line of data.
>
> If a *read*() is interrupted by a signal before it reads any data, it shall return -1 with *errno* set to \[EINTR\].
>
> If a *read*() is interrupted by a signal after it has successfully read some data, it shall return the number of bytes read.
>
> For regular files, no data transfer shall occur past the offset maximum established in the open file description associated with *fildes*.
>
> If *fildes* refers to a socket, *read*() shall be equivalent to [*recv*()](../functions/recv.html) with no flags set.
>
> <sup>\[[SIO](javascript:open_code('SIO'))\]</sup> <img src="../images/opt-start.gif" data-border="0" alt="[Option Start]" /> If the O_DSYNC and O_RSYNC bits have been set, read I/O operations on the file descriptor shall complete as defined by synchronized I/O data integrity completion. If the O_SYNC and O_RSYNC bits have been set, read I/O operations on the file descriptor shall complete as defined by synchronized I/O file integrity completion. <img src="../images/opt-end.gif" data-border="0" alt="[Option End]" />
>
> <sup>\[[SHM](javascript:open_code('SHM'))\]</sup> <img src="../images/opt-start.gif" data-border="0" alt="[Option Start]" /> If *fildes* refers to a shared memory object, the result of the *read*() function is unspecified. <img src="../images/opt-end.gif" data-border="0" alt="[Option End]" />
>
> <sup>\[[TYM](javascript:open_code('TYM'))\]</sup> <img src="../images/opt-start.gif" data-border="0" alt="[Option Start]" /> If *fildes* refers to a typed memory object, the result of the *read*() function is unspecified. <img src="../images/opt-end.gif" data-border="0" alt="[Option End]" />
>
> The *pread*() function shall be equivalent to *read*(), except that it shall read from a given position in the file without changing the file offset. The first three arguments to *pread*() are the same as *read*() with the addition of a fourth argument *offset* for the desired position inside the file. An attempt to perform a *pread*() on a file that is incapable of seeking shall result in an error.

#### <span id="tag_17_476_04"></span>RETURN VALUE

> Upon successful completion, these functions shall return a non-negative integer indicating the number of bytes actually read. Otherwise, the functions shall return -1 and set *errno* to indicate the error.

#### <span id="tag_17_476_05"></span>ERRORS

> These functions shall fail if:
>
> \[EAGAIN\]
>
> The file is neither a pipe, nor a FIFO, nor a socket, the O_NONBLOCK flag is set for the file descriptor, and the thread would be delayed in the read operation.
>
> \[EBADF\]
>
> The *fildes* argument is not a valid file descriptor open for reading.
>
> \[EINTR\]
>
> The read operation was terminated due to the receipt of a signal, and no data was transferred.
>
> \[EIO\]
>
> The process is a member of a background process group attempting to read from its controlling terminal, and either the calling thread is blocking SIGTTIN or the process is ignoring SIGTTIN or the process group of the process is orphaned. This error may also be generated for implementation-defined reasons.
>
> \[EISDIR\]
>
> <sup>\[[XSI](javascript:open_code('XSI'))\]</sup> <img src="../images/opt-start.gif" data-border="0" alt="[Option Start]" /> The *fildes* argument refers to a directory and the implementation does not allow the directory to be read using *read*() or *pread*(). The [*readdir*()](../functions/readdir.html) function should be used instead. <img src="../images/opt-end.gif" data-border="0" alt="[Option End]" />
>
> \[EOVERFLOW\]
>
> The file is a regular file, *nbyte* is greater than 0, the starting position is before the end-of-file, and the starting position is greater than or equal to the offset maximum established in the open file description associated with *fildes*.
>
> The *pread*() function shall fail if:
>
> \[EINVAL\]
>
> The file is a regular file or block special file, and the *offset* argument is negative. The file offset shall remain unchanged.
>
> \[ESPIPE\]
>
> The file is incapable of seeking.
>
> \
>
> The *read*() function shall fail if:
>
> \[EAGAIN\]
>
> The file is a pipe or FIFO, the O_NONBLOCK flag is set for the file descriptor, and the thread would be delayed in the read operation.
>
> \[EAGAIN\] or \[EWOULDBLOCK\]
>
> The file is a socket, the O_NONBLOCK flag is set for the file descriptor, and the thread would be delayed in the read operation.
>
> \[ECONNRESET\]
>
> A read was attempted on a socket and the connection was forcibly closed by its peer.
>
> \[ENOTCONN\]
>
> A read was attempted on a socket that is not connected.
>
> \[ETIMEDOUT\]
>
> A read was attempted on a socket and a transmission timeout occurred.
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
> \[ENOMEM\]
>
> Insufficient memory was available to fulfill the request.
>
> \[ENXIO\]
>
> A request was made of a nonexistent device, or the request was outside the capabilities of the device.

------------------------------------------------------------------------

<div class="box">

*The following sections are informative.*

</div>

#### <span id="tag_17_476_06"></span>EXAMPLES

> ##### <span id="tag_17_476_06_01"></span>Reading Data into a Buffer
>
> The following example reads data from the file associated with the file descriptor *fd* into the buffer pointed to by *buf*.
>
>     #include <sys/types.h>
>     #include <unistd.h>
>     ...
>     char buf[20];
>     size_t nbytes;
>     ssize_t bytes_read;
>     int fd;
>     ...
>     nbytes = sizeof(buf);
>     bytes_read = read(fd, buf, nbytes);
>     ...

#### <span id="tag_17_476_07"></span>APPLICATION USAGE

> None.

#### <span id="tag_17_476_08"></span>RATIONALE

> This volume of POSIX.1-2024 does not specify the value of the file offset after an error is returned; there are too many cases. For programming errors, such as \[EBADF\], the concept is meaningless since no file is involved. For errors that are detected immediately, such as \[EAGAIN\], clearly the offset should not change. After an interrupt or hardware error, however, an updated value would be very useful and is the behavior of many implementations.
>
> Note that a *read*() of zero bytes does not modify the last data access timestamp. A *read*() that requests more than zero bytes, but returns zero, is required to modify the last data access timestamp.
>
> Implementations are allowed, but not required, to perform error checking for *read*() requests of zero bytes.
>
> ##### <span id="tag_17_476_08_01"></span>Input and Output
>
> The use of I/O with large byte counts has always presented problems. Ideas such as *lread*() and *lwrite*() (using and returning **long**s) were considered at one time. The current solution is to use abstract types on the ISO C standard function to *read*() and [*write*()](../functions/write.html). The abstract types can be declared so that existing functions work, but can also be declared so that larger types can be represented in future implementations. It is presumed that whatever constraints limit the maximum range of **size_t** also limit portable I/O requests to the same range. This volume of POSIX.1-2024 also limits the range further by requiring that the byte count be limited so that a signed return value remains meaningful. Since the return type is also a (signed) abstract type, the byte count can be defined by the implementation to be larger than an **int** can hold.
>
> The standard developers considered adding atomicity requirements to a pipe or FIFO, but recognized that due to the nature of pipes and FIFOs there could be no guarantee of atomicity of reads of {PIPE_BUF} or any other size that would be an aid to applications portability.
>
> This volume of POSIX.1-2024 requires that no action be taken for *read*() or [*write*()](../functions/write.html) when *nbyte* is zero. This is not intended to take precedence over detection of errors (such as invalid buffer pointers or file descriptors). This is consistent with the rest of this volume of POSIX.1-2024, but the phrasing here could be misread to require detection of the zero case before any other errors. A value of zero is to be considered a correct value, for which the semantics are a no-op.
>
> I/O is intended to be atomic to ordinary files and pipes and FIFOs. Atomic means that all the bytes from a single operation that started out together end up together, without interleaving from other I/O operations. It is a known attribute of terminals that this is not honored, and terminals are explicitly (and implicitly permanently) excepted, making the behavior unspecified. The behavior for other device types is also left unspecified, but the wording is intended to imply that future standards might choose to specify atomicity (or not).
>
> There were recommendations to add format parameters to *read*() and [*write*()](../functions/write.html) in order to handle networked transfers among heterogeneous file system and base hardware types. Such a facility may be required for support by the OSI presentation of layer services. However, it was determined that this should correspond with similar C-language facilities, and that is beyond the scope of this volume of POSIX.1-2024. The concept was suggested to the developers of the ISO C standard for their consideration as a possible area for future work.
>
> In 4.3 BSD, a *read*() or [*write*()](../functions/write.html) that is interrupted by a signal before transferring any data does not by default return an \[EINTR\] error, but is restarted. In 4.2 BSD, 4.3 BSD, and the Eighth Edition, there is an additional function, [*select*()](../functions/select.html), whose purpose is to pause until specified activity (data to read, space to write, and so on) is detected on specified file descriptors. It is common in applications written for those systems for [*select*()](../functions/select.html) to be used before *read*() in situations (such as keyboard input) where interruption of I/O due to a signal is desired.
>
> The issue of which files or file types are interruptible is considered an implementation design issue. This is often affected primarily by hardware and reliability issues.
>
> There are no references to actions taken following an "unrecoverable error". It is considered beyond the scope of this volume of POSIX.1-2024 to describe what happens in the case of hardware errors.
>
> Earlier versions of this standard allowed two very different behaviors with regard to the handling of interrupts. In order to minimize the resulting confusion, it was decided that POSIX.1-2024 should support only one of these behaviors. Historical practice on AT&T-derived systems was to have *read*() and [*write*()](../functions/write.html) return -1 and set *errno* to \[EINTR\] when interrupted after some, but not all, of the data requested had been transferred. However, the US Department of Commerce FIPS 151-1 and FIPS 151-2 require the historical BSD behavior, in which *read*() and [*write*()](../functions/write.html) return the number of bytes actually transferred before the interrupt. If -1 is returned when any data is transferred, it is difficult to recover from the error on a seekable device and impossible on a non-seekable device. Most new implementations support this behavior. The behavior required by POSIX.1-2024 is to return the number of bytes transferred.
>
> POSIX.1-2024 does not specify when an implementation that buffers *read*()s actually moves the data into the user-supplied buffer, so an implementation may choose to do this at the latest possible moment. Therefore, an interrupt arriving earlier may not cause *read*() to return a partial byte count, but rather to return -1 and set *errno* to \[EINTR\].
>
> Consideration was also given to combining the two previous options, and setting *errno* to \[EINTR\] while returning a short count. However, not only is there no existing practice that implements this, it is also contradictory to the idea that when *errno* is set, the function responsible shall return -1.
>
> This volume of POSIX.1-2024 intentionally does not specify any *pread*() errors related to pipes, FIFOs, and sockets other than \[ESPIPE\].

#### <span id="tag_17_476_09"></span>FUTURE DIRECTIONS

> None.

#### <span id="tag_17_476_10"></span>SEE ALSO

> [*fcntl*()](../functions/fcntl.html#), [*lseek*()](../functions/lseek.html#), [*open*()](../functions/open.html#), [*pipe*()](../functions/pipe.html#), [*readv*()](../functions/readv.html#)
>
> XBD [*11. General Terminal Interface*](../basedefs/V1_chap11.html#tag_11), [*\<sys/uio.h\>*](../basedefs/sys_uio.h.html), [*\<unistd.h\>*](../basedefs/unistd.h.html)

#### <span id="tag_17_476_11"></span>CHANGE HISTORY

> First released in Issue 1. Derived from Issue 1 of the SVID.

#### <span id="tag_17_476_12"></span>Issue 5

> The DESCRIPTION is updated for alignment with the POSIX Realtime Extension and the POSIX Threads Extension.
>
> Large File Summit extensions are added.
>
> The *pread*() function is added.

#### <span id="tag_17_476_13"></span>Issue 6

> The DESCRIPTION and ERRORS sections are updated so that references to STREAMS are marked as part of the XSI STREAMS Option Group.
>
> The following new requirements on POSIX implementations derive from alignment with the Single UNIX Specification:
>
> - The DESCRIPTION now states that if *read*() is interrupted by a signal after it has successfully read some data, it returns the number of bytes read. In Issue 3, it was optional whether *read*() returned the number of bytes read, or whether it returned -1 with *errno* set to \[EINTR\]. This is a FIPS requirement.
>
> - In the DESCRIPTION, text is added to indicate that for regular files, no data transfer occurs past the offset maximum established in the open file description associated with *fildes*. This change is to support large files.
>
> - The \[EOVERFLOW\] mandatory error condition is added.
>
> - The \[ENXIO\] optional error condition is added.
>
> Text referring to sockets is added to the DESCRIPTION.
>
> The following changes were made to align with the IEEE P1003.1a draft standard:
>
> - The effect of reading zero bytes is clarified.
>
> The DESCRIPTION is updated for alignment with IEEE Std 1003.1j-2000 by specifying that *read*() results are unspecified for typed memory objects.
>
> New RATIONALE is added to explain the atomicity requirements for input and output operations.
>
> The following error conditions are added for operations on sockets: \[EAGAIN\], \[ECONNRESET\], \[ENOTCONN\], and \[ETIMEDOUT\].
>
> The \[EIO\] error is made optional.
>
> The following error conditions are added for operations on sockets: \[ENOBUFS\] and \[ENOMEM\].
>
> The [*readv*()](../functions/readv.html) function is split out into a separate reference page.
>
> IEEE Std 1003.1-2001/Cor 2-2004, item XSH/TC2/D6/108 is applied, updating the \[EAGAIN\] error in the ERRORS section from "the process would be delayed" to "the thread would be delayed".
>
> IEEE Std 1003.1-2001/Cor 2-2004, item XSH/TC2/D6/109 is applied, making an editorial correction in the RATIONALE section.

#### <span id="tag_17_476_14"></span>Issue 7

> The *pread*() function is moved from the XSI option to the Base.
>
> Functionality relating to the XSI STREAMS option is marked obsolescent.
>
> Changes are made related to support for finegrained timestamps.
>
> POSIX.1-2008, Technical Corrigendum 1, XSH/TC1-2008/0480 \[218\], XSH/TC1-2008/0481 \[79\], XSH/TC1-2008/0482 \[218\], XSH/TC1-2008/0483 \[218\], XSH/TC1-2008/0484 \[218\], and XSH/TC1-2008/0485 \[218,428\] are applied.
>
> POSIX.1-2008, Technical Corrigendum 2, XSH/TC2-2008/0302 \[710\] and XSH/TC2-2008/0303 \[676,710\] are applied.

#### <span id="tag_17_476_15"></span>Issue 8

> Austin Group Defect 1330 is applied, removing obsolescent interfaces.

<div class="box">

*End of informative text.*

</div>

------------------------------------------------------------------------

 
