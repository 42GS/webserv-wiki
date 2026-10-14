> Source: <https://pubs.opengroup.org/onlinepubs/9799919799/functions/fcntl.html>
> Retrieved: 2026-10-15. Original HTML: kept next to this file as `.source.html`.
> Converted to markdown by text extraction of `div#content`; wording is unchanged,
> whitespace, list markup and code fences were normalized.

The Open Group Base Specifications Issue 8 IEEE Std 1003.1-2024 Copyright © 2001-2024 The IEEE and The Open Group

<a id="top"></a>

<a id="fcntl"></a>

<a id="tag_17_139"></a>

<a id="tag_17_139_01"></a>

#### NAME

fcntl — file control

<a id="tag_17_139_02"></a>

#### SYNOPSIS

`#include <fcntl.h> int fcntl(int fildes, int cmd, ...); `

<a id="tag_17_139_03"></a>

#### DESCRIPTION

The fcntl() function shall perform the operations described below on open files. The fildes argument is a file descriptor.

The available values for cmd are defined in <fcntl.h> and are as follows:

- F_DUPFD

- Return a new file descriptor which shall be allocated as described in 2.6 File Descriptor Allocation, except that it shall be the lowest numbered available file descriptor greater than or equal to the third argument, arg, taken as an integer of type int. The new file descriptor shall refer to the same open file description as the original file descriptor, and shall share any locks. The FD_CLOEXEC and FD_CLOFORK flags associated with the new file descriptor shall be cleared.

- F_DUPFD_CLOEXEC

- Like F_DUPFD, but the FD_CLOEXEC flag associated with the new file descriptor shall be set.

- F_DUPFD_CLOFORK

- Like F_DUPFD, but the FD_CLOFORK flag associated with the new file descriptor shall be set.

- F_GETFD

- Get the file descriptor flags defined in <fcntl.h> that are associated with the file descriptor fildes. File descriptor flags are associated with a single file descriptor and do not affect other file descriptors that refer to the same file.

- F_SETFD

- Set the file descriptor flags defined in <fcntl.h>, that are associated with fildes, to the third argument, arg, taken as type int. If the FD_CLOEXEC flag in the third argument is set, the file descriptor shall be closed upon successful execution of an exec family function [SPN] and in the new process image created by posix_spawn() or posix_spawnp(); otherwise, the file descriptor shall remain open. If the FD_CLOFORK flag in the third argument is set, the file descriptor shall not be inherited by any child process created from a process that has the file descriptor open; otherwise, the file descriptor shall be inherited.

- F_GETFL

- Get the file status flags and file access modes, defined in <fcntl.h>, for the file description associated with fildes. The file access modes can be extracted from the return value using the mask O_ACCMODE, which is defined in <fcntl.h>. File status flags and file access modes are associated with the file description and do not affect other file descriptors that refer to the same file with different open file descriptions. The flags returned may include non-standard file status flags which the application did not set, provided that these additional flags do not alter the behavior of a conforming application.

- F_SETFL

- Set the file status flags, defined in <fcntl.h>, for the file description associated with fildes from the corresponding bits in the third argument, arg, taken as type int. Bits corresponding to the file access mode and the file creation flags, as defined in <fcntl.h>, that are set in arg shall be ignored. If any bits in arg other than those mentioned here are changed by the application, the result is unspecified. If fildes does not support non-blocking operations, it is unspecified whether the O_NONBLOCK flag will be ignored.

- F_GETOWN

- If fildes refers to a socket, get the process ID or process group ID specified to receive SIGURG signals when out-of-band data is available. Positive values shall indicate a process ID; negative values, other than -1, shall indicate a process group ID; the value zero shall indicate that no SIGURG signals are to be sent. If fildes does not refer to a socket, the results are unspecified.

- F_SETOWN

- If fildes refers to a socket, atomically set the process ID or process group ID specified to receive SIGURG signals when out-of-band data is available, using the value of the third argument, arg, taken as type int. Positive values shall indicate a process ID; negative values, other than -1, shall indicate a process group ID; the value zero shall indicate that no SIGURG signals are to be sent. If fildes does not refer to a socket, the results are unspecified.

- F_GETOWN_EX

- If fildes refers to a socket, get the process ID or process group ID specified to receive SIGURG signals when out-of-band data is available, by setting the type and pid members of the f_owner_ex structure pointed to by the third argument, arg. The value of type shall be F_OWNER_PID or F_OWNER_PGRP to indicate that pid contains a process ID or a process group ID, respectively. The value of pid shall be zero if no SIGURG signals are to be sent. If fildes does not refer to a socket, the results are unspecified.

- F_SETOWN_EX

If fildes refers to a socket, set the process ID or process group ID specified to receive SIGURG signals when out-of-band data is available, using the value of the third argument, arg, taken as type pointer to struct f_owner_ex. The type and pid members of this structure shall be used as follows:

A pid value of zero shall indicate that no SIGURG signals are to be sent.

A type value of F_OWNER_PID and a positive pid value shall indicate that SIGURG signals are to be sent to the process ID specified in pid.

A type value of F_OWNER_PGRP and a positive pid value shall indicate that SIGURG signals are to be sent to the process group ID specified in pid.

If fildes does not refer to a socket, the results are unspecified.

For F_SETOWN and F_SETOWN_EX, each time a SIGURG signal is sent to the specified process or process group, permission checks equivalent to those performed by kill() shall be performed, as if kill() were called by a process with the same real user ID, effective user ID, and privileges that the process calling fcntl() has at the time of the call; if the kill() call would fail, no signal shall be sent. These permission checks may also be performed by the fcntl() call. If the process specified by arg later terminates, or the process group specified by arg later becomes empty, while still being specified to receive SIGURG signals when out-of-band data is available from fildes, then no signals shall be sent to any subsequently created process that has the same process ID or process group ID, regardless of permission; it is unspecified whether this is achieved by the equivalent of a fcntl(fildes, F_SETOWN, 0) call at the time the process terminates or is waited for or the process group becomes empty, or by other means.

The following values for cmd are available for advisory record locking. Record locking shall be supported for regular files, and may be supported for other files.

- F_GETLK

- Get any lock which blocks the process-owned file lock description pointed to by the third argument, arg, taken as a pointer to type struct flock, defined in <fcntl.h>. The information retrieved shall overwrite the information passed to fcntl() in the structure flock. If no lock is found that would prevent this lock from being created, then the structure shall be left unchanged except for the lock type in l_type which shall be set to F_UNLCK.

- F_SETLK

- Set or clear a process-owned file lock according to the lock description pointed to by the third argument, arg, taken as a pointer to type struct flock, defined in <fcntl.h>. F_SETLK can establish shared (or read) locks (F_RDLCK) or exclusive (or write) locks (F_WRLCK), as well as remove either type of lock (F_UNLCK). F_RDLCK, F_WRLCK, and F_UNLCK are defined in <fcntl.h>. If a shared or exclusive lock cannot be set, fcntl() shall return immediately with a return value of -1.

- F_SETLKW

- This command shall be equivalent to F_SETLK except that if a shared or exclusive lock is blocked by other locks, the thread shall wait until the request can be satisfied. If a signal that is to be caught is received while fcntl() is waiting for a region, fcntl() shall be interrupted. Upon return from the signal handler, fcntl() shall return -1 with errno set to [EINTR], and the lock operation shall not be done.

- F_OFD_GETLK

- Get any lock which blocks the OFD-owned file lock description pointed to by the third argument, arg, taken as a pointer to type struct flock, defined in <fcntl.h>; the application shall ensure that the l_pid member of the structure pointed to by arg is set to 0 on input. The information retrieved shall overwrite the information passed to fcntl() in the structure flock. If no lock is found that would prevent this lock from being created, then the structure shall be left unchanged except for the lock type in l_type which shall be set to F_UNLCK.

- F_OFD_SETLK

- Set or clear an OFD-owned file lock according to the lock description pointed to by the third argument, arg, taken as a pointer to type struct flock, defined in <fcntl.h>; the application shall ensure that the l_pid member of the structure pointed to by arg is set to 0 on input. F_OFD_SETLK can establish shared (or read) locks (F_RDLCK) or exclusive (or write) locks (F_WRLCK), as well as remove either type of lock (F_UNLCK). F_RDLCK, F_WRLCK, and F_UNLCK are defined in <fcntl.h>. If a shared or exclusive lock cannot be set, fcntl() shall return immediately with a return value of -1.

- F_OFD_SETLKW

- This command shall be equivalent to F_OFD_SETLK except that if a shared or exclusive lock is blocked by other locks, the thread shall wait until the request can be satisfied. If a signal that is to be caught is received while fcntl() is waiting for a region, fcntl() shall be interrupted. Upon return from the signal handler, fcntl() shall return -1 with errno set to [EINTR], and the lock operation shall not be done.

Additional implementation-defined values for cmd may be defined in <fcntl.h>. Their names shall start with F_.

When a shared lock is set on a segment of a file, other processes can set shared process-owned locks, and other open file descriptions can be used to set shared OFD-owned locks, on that segment or a portion of it. A shared process-owned lock shall prevent any other process from setting an exclusive process-owned lock, and shall prevent any exclusive OFD-owned lock from being set, on any portion of the protected area. A shared OFD-owned lock shall prevent any other open file description from being used to set an exclusive OFD-owned lock, and shall prevent any exclusive process-owned lock from being set, on any portion of the protected area. A request for a shared lock shall fail if the file descriptor is not open for reading.

An exclusive process-owned lock shall prevent any other process from setting a shared or exclusive process-owned lock, and shall prevent any shared or exclusive OFD-owned lock from being set, on any portion of the protected area. An exclusive OFD-owned lock shall prevent any other open file description from being used to set a shared or exclusive OFD-owned lock, and shall prevent any shared or exclusive process-owned lock from being set, on any portion of the protected area. A request for an exclusive lock shall fail if the file descriptor is not open for writing.

The structure flock describes the type (l_type), starting offset (l_whence), relative offset (l_start), size (l_len), and process ID (l_pid) of the segment of the file to be affected.

The value of l_whence is SEEK_SET, SEEK_CUR, or SEEK_END, to indicate that the relative offset l_start bytes shall be measured from the start of the file, current position, or end of the file, respectively. The value of l_len is the number of consecutive bytes to be locked. The value of l_len may be negative (where the definition of off_t permits negative values of l_len). On input, the l_pid field shall be ignored for F_GETLK, F_SETLK and F_SETLKW; the application shall ensure that it is set to zero for F_OFD_GETLK, F_OFD_SETLK and F_OFD_SETLKW. It is set by F_GETLK and F_OFD_GETLK when identifying a blocking lock. After a successful F_GETLK or F_OFD_GETLK request, when a blocking lock is found, the values returned in the flock structure shall be as follows:

- l_type

- Type of blocking lock found.

- l_whence

- SEEK_SET.

- l_start

- Start of the blocking lock.

- l_len

- Length of the blocking lock.

- l_pid

- Process ID of the process that holds the blocking lock if the blocking lock is a process-owned file lock, or (pid_t)-1 if the blocking lock is an OFD-owned file lock.

If the command is F_SETLKW or F_OFD_SETLKW and the thread needs to wait for a blocking lock to be released, then the range of bytes to be locked shall be determined before the fcntl() function blocks. If the file size or file descriptor seek offset change while fcntl() is blocked, this shall not affect the range of bytes locked.

If l_len is positive, the area affected shall start at l_start and end at l_start+l_len-1. If l_len is negative, the area affected shall start at l_start+l_len and end at l_start-1. Locks may start and extend beyond the current end of a file, but shall not extend before the beginning of the file. A lock shall be set to extend to the largest possible value of the file offset for that file by setting l_len to 0. If such a lock also has l_start set to 0 and l_whence is set to SEEK_SET, the whole file shall be locked.

Each byte in the file can be locked either with one or more shared locks (F_RDLCK) or with one exclusive lock (F_WRLCK).

Before a successful return from an F_SETLK or an F_SETLKW request when the calling process has previously existing process-owned locks on bytes in the region specified by the request, the previous shared or exclusive lock for each byte in the specified region shall be replaced by the new shared or exclusive lock. An F_SETLK or an F_SETLKW request (respectively) shall fail or block when another process has existing process-owned locks, or any open file description (including the one associated with fildes) has existing OFD-owned locks, on bytes in the specified region and any of those locks conflicts with the requested lock.

Before a successful return from an F_OFD_SETLK or an F_OFD_SETLKW request when the open file description associated with fildes has previously existing OFD-owned locks on bytes in the region specified by the request, the previous shared or exclusive lock for each byte in the specified region shall be replaced by the new shared or exclusive lock. An F_OFD_SETLK or an F_OFD_SETLKW request (respectively) shall fail or block when another open file description has existing OFD-owned locks, or any process (including the calling process) has existing process-owned locks, on bytes in the specified region and any of those locks conflicts with the requested lock.

All process-owned locks associated with a file for a given process shall be removed when any file descriptor for that file is closed by that process (even if via a different open file description) or the process holding that file descriptor terminates. Process-owned locks shall not be inherited by a child process.

All OFD-owned locks associated with a given open file description shall be removed when all file descriptors associated with that open file description have been closed (either directly or as a side-effect of, for example, process termination or FD_CLOEXEC). OFD-owned locks shall be shared across all file descriptors that are associated with the owning open file description, regardless of which process holds the file descriptor.

A potential for deadlock occurs if a process or thread controlling a locked region is put to sleep by attempting to lock a region that has an existing conflicting lock. If the system detects that sleeping until a locked region is unlocked would cause a deadlock, fcntl() shall fail with an [EDEADLK] error. Deadlock detection may differ between process-owned locks and OFD-owned locks.

[XSI] The interaction between fcntl() and lockf() locks is unspecified.

An unlock (F_UNLCK) request in which l_len is non-zero and the offset of the last byte of the requested segment is the maximum value for an object of type off_t, when the process (for F_SETLK and F_SETLKW) or open file description (for F_OFD_SETLK and F_OFD_SETLKW) has an existing lock in which l_len is 0 and which includes the last byte of the requested segment, shall be treated as a request to unlock from the start of the requested segment with an l_len equal to 0. Otherwise, an unlock (F_UNLCK) request shall attempt to unlock only the requested segment.

[SHM] When the file descriptor fildes refers to a shared memory object, the behavior of fcntl() shall be the same as for a regular file except the effect of the following values for the argument cmd is unspecified: F_SETFL, F_GETLK, F_SETLK, F_SETLKW, F_OFD_GETLK, F_OFD_SETLK, and F_OFD_SETLKW.

[TYM] If fildes refers to a typed memory object, the result of the fcntl() function is unspecified.

<a id="tag_17_139_04"></a>

#### RETURN VALUE

Upon successful completion, the value returned shall depend on cmd as follows:

- F_DUPFD

- A new file descriptor.

- F_DUPFD_CLOEXEC

- A new file descriptor.

- F_DUPFD_CLOFORK

- A new file descriptor.

- F_GETFD

- Value of flags defined in <fcntl.h>. The return value shall not be negative.

- F_SETFD

- Value other than -1.

- F_GETFL

- Value of file status flags and access modes. The return value shall not be negative.

- F_SETFL

- Value other than -1.

- F_GETLK

- Value other than -1.

- F_SETLK

- Value other than -1.

- F_SETLKW

- Value other than -1.

- F_OFD_GETLK

- Value other than -1.

- F_OFD_SETLK

- Value other than -1.

- F_OFD_SETLKW

- Value other than -1.

- F_GETOWN

- Value of the socket owner process or process group; this shall not be -1.

- F_SETOWN

- Value other than -1.

- F_GETOWN_EX

- Value other than -1.

- F_SETOWN_EX

- Value other than -1.

Otherwise, -1 shall be returned and errno set to indicate the error.

<a id="tag_17_139_05"></a>

#### ERRORS

The fcntl() function shall fail if:

- [EACCES] or [EAGAIN]

- The cmd argument is F_SETLK, the type of lock (l_type) is a shared (F_RDLCK) or exclusive (F_WRLCK) lock, and the requested lock cannot be set because it is blocked by an existing lock on the file.

- [EAGAIN]

- The cmd argument is F_OFD_SETLK, the type of lock (l_type) is a shared (F_RDLCK) or exclusive (F_WRLCK) lock, and the requested lock cannot be set because it is blocked by an existing lock on the file.

- [EBADF]

- The fildes argument is not a valid open file descriptor; or the argument cmd is F_SETLK, F_SETLKW, F_OFD_SETLK, or F_OFD_SETLKW, the type of lock, l_type, is a shared lock (F_RDLCK), and fildes is not a valid file descriptor open for reading, or the type of lock, l_type, is an exclusive lock (F_WRLCK), and fildes is not a valid file descriptor open for writing.

- [EINTR]

- The cmd argument is F_SETLKW or F_OFD_SETLKW and the function was interrupted by a signal.

- [EINVAL]

- The cmd argument is invalid; or the cmd argument is F_DUPFD, F_DUPFD_CLOEXEC, or F_DUPFD_CLOFORK and arg is negative or is greater than or equal to {OPEN_MAX}; or the cmd argument is F_SETOWN_EX and the type member of the f_owner_ex structure pointed to by arg is invalid, or the pid member is negative and the type member is F_OWNER_PID or F_OWNER_PGRP; or the cmd argument is F_GETLK, F_SETLK, F_SETLKW, F_OFD_GETLK, F_OFD_SETLK, or F_OFD_SETLKW and the data pointed to by arg is not valid, or fildes refers to a file that does not support locking.

- [EMFILE]

- The argument cmd is F_DUPFD, F_DUPFD_CLOEXEC, or F_DUPFD_CLOFORK and all file descriptors available to the process are currently open, or no file descriptors greater than or equal to arg are available.

- [ENOLCK]

- The argument cmd is F_SETLK, F_SETLKW, F_OFD_SETLK, or F_OFD_SETLKW and satisfying the lock or unlock request would result in the number of locked regions in the system exceeding a system-imposed limit.

- [EOVERFLOW]

- One of the values to be returned cannot be represented correctly.

- [EOVERFLOW]

- The cmd argument is F_GETLK, F_SETLK, F_SETLKW, F_OFD_GETLK, F_OFD_SETLK, or F_OFD_SETLKW and the smallest or, if l_len is non-zero, the largest offset of any byte in the requested segment cannot be represented correctly in an object of type off_t.

- [ESRCH]

- The cmd argument is F_SETOWN or F_SETOWN_EX and no process or process group can be found corresponding to that specified by arg.

The fcntl() function may fail if:

- [EDEADLK]

- The cmd argument is F_SETLKW or F_OFD_SETLKW, the type of lock (l_type) is a shared (F_RDLCK) or exclusive (F_WRLCK) lock, the requested lock is blocked by an existing lock on the file, and the system determines that waiting for that lock to be released would cause a deadlock.

- [EINVAL]

- The cmd argument is F_SETOWN and the value of arg is positive and is not valid as a process ID or the value of arg is negative and its absolute value is not valid as a process group ID; or the cmd argument is F_SETOWN_EX, the value of the type member of the f_owner_ex structure pointed to by arg is F_OWNER_PID, and the value of the pid member is not valid as a process ID; or the cmd argument is F_SETOWN_EX, the value of the type member of the f_owner_ex structure pointed to by arg is F_OWNER_PGRP, and the value of the pid member is not valid as a process group ID.

- [EPERM]

- The cmd argument is F_SETOWN or F_SETOWN_EX and the calling process does not have permission to send a SIGURG signal to any process specified by arg.

The following sections are informative.

<a id="tag_17_139_06"></a>

#### EXAMPLES

<a id="tag_17_139_06_01"></a>

Locking and Unlocking a File

The following example demonstrates how to place a lock on bytes 100 to 109 of a file and then later remove it. F_SETLK is used to perform a non-blocking lock request so that the process does not have to wait if an incompatible lock is held by another process; instead the process can take some other action.

```
#include <stdlib.h>
#include <unistd.h>
#include <fcntl.h>
#include <errno.h>
#include <stdio.h>
 
int
main(int argc, char *argv[])
{
    int fd;
    struct flock fl;
 
    fd = open("testfile", O_RDWR);
    if (fd == -1)
        /* Handle error */;
 
    /* Make a non-blocking request to place a write lock
       on bytes 100-109 of testfile */
 
    fl.l_type = F_WRLCK;
    fl.l_whence = SEEK_SET;
    fl.l_start = 100;
    fl.l_len = 10;
 
    if (fcntl(fd, F_SETLK, &fl) == -1) {
        if (errno == EACCES || errno == EAGAIN) {
            printf("Already locked by another process\n");
 
            /* We cannot get the lock at the moment */
 
        } else {
            /* Handle unexpected error */;
        }
    } else { /* Lock was granted... */
 
        /* Perform I/O on bytes 100 to 109 of file */
 
        /* Unlock the locked bytes */
 
        fl.l_type = F_UNLCK;
        fl.l_whence = SEEK_SET;
        fl.l_start = 100;
        fl.l_len = 10;
        if (fcntl(fd, F_SETLK, &fl) == -1)
            /* Handle error */;
    }
    exit(EXIT_SUCCESS);
} /* main */
```

<a id="tag_17_139_06_02"></a>

Setting the Close-on-Exec Flag

The following example demonstrates how to set the close-on-exec flag for the file descriptor fd.

```
#include <unistd.h>
#include <fcntl.h>
...
    int flags;
 
    flags = fcntl(fd, F_GETFD);
    if (flags == -1)
        /* Handle error */;
    flags |= FD_CLOEXEC;
    if (fcntl(fd, F_SETFD, flags) == -1)
        /* Handle error */;"
```

<a id="tag_17_139_07"></a>

#### APPLICATION USAGE

The arg values to F_GETFD, F_SETFD, F_GETFL, and F_SETFL all represent flag values to allow for future growth. Applications using these functions should do a read-modify-write operation on them, rather than assuming that only the values defined by this volume of POSIX.1-2024 are valid. It is a common error to forget this, particularly in the case of F_SETFD. Some implementations set additional file status flags to advise the application of default behavior, even though the application did not request these flags.

In order to set both FD_CLOEXEC and FD_CLOFORK when duplicating a file descriptor, applications should use F_DUPFD_CLOFORK to obtain the new file descriptor with FD_CLOFORK already set, and then use F_SETFD to set the FD_CLOEXEC flag on the new descriptor. (The alternative of first using F_DUPFD_CLOEXEC and then setting FD_CLOFORK with F_SETFD has a timing window where another thread could create a child process which inherits the new descriptor because FD_CLOFORK has not yet been set.)

The FD_CLOFORK flag takes effect for all child processes, not just those created using fork() or _Fork().

On implementations where process IDs can be greater than {INT_MAX}, F_SETOWN cannot be used with process IDs greater than {INT_MAX} or process group IDs greater than {INT_MAX}+1 because the value is passed to fcntl() in an argument of type int. In this situation, F_SETOWN_EX should be used instead.

Similarly, if a process ID greater than {INT_MAX} or a process group ID greater than {INT_MAX}+1 has been set to receive SIGURG signals (using F_SETOWN_EX), F_GETOWN cannot be used to obtain the value because fcntl() returns the value as type int and will thus give an [EOVERFLOW] error for such values. F_GETOWN_EX should be used instead.

Note that the convention of negating a process group ID is only used with F_SETOWN and F_GETOWN; the pid member of the f_owner_ex structure used with F_SETOWN_EX and F_GETOWN_EX is not negated when it specifies a process group ID.

On systems which do not perform permission checks at the time of an fcntl() call with F_SETOWN or F_SETOWN_EX, if the permission checks performed at the time the signal is sent disallow sending the signal to any process, the process that called fcntl() has no way of discovering that this has happened. A call to kill() with signal 0 can be used as a prior check of permissions, although this is no guarantee that permission will be granted at the time a signal is sent, since the target process(es) could change user IDs or privileges in the meantime.

Record-locking should not be used in combination with buffered standard I/O streams (see 2.5 Standard I/O Streams). Instead, non-buffered I/O should be used. Unexpected results may occur in processes that do buffering in the user address space. The process may later read/write data which is/was locked. Functions that operate on standard I/O streams are the most common source of such buffering.

<a id="tag_17_139_08"></a>

#### RATIONALE

The ellipsis in the SYNOPSIS is the syntax specified by the ISO C standard for a variable number of arguments. It is used because System V uses pointers for the implementation of file locking functions.

This volume of POSIX.1-2024 permits concurrent read and write access to file data using the fcntl() function; this is a change from the 1984 /usr/group standard and early proposals. Without concurrency controls, this feature may not be fully utilized without occasional loss of data.

Data losses occur in several ways. One case occurs when several processes try to update the same record, without sequencing controls; several updates may occur in parallel and the last writer "wins". Another case is a bit-tree or other internal list-based database that is undergoing reorganization. Without exclusive use to the tree segment by the updating process, other reading processes chance getting lost in the database when the index blocks are split, condensed, inserted, or deleted. While fcntl() is useful for many applications, it is not intended to be overly general and does not handle the bit-tree example well.

This facility is only required for regular files because it is not appropriate for many devices such as terminals and network connections.

Since fcntl() works with "any file descriptor associated with that file, however it is obtained", the file descriptor may have been inherited through a fork() or exec operation and thus may affect a file that another process also has open.

The use of the open file description to identify what to lock requires extra calls and presents problems if several processes are sharing an open file description, but there are too many implementations of the existing mechanism for this volume of POSIX.1-2024 to use different specifications.

Another consequence of this model is that closing any file descriptor for a given file (whether or not it is the same open file description that created the lock) causes the locks on that file to be relinquished for that process. Equivalently, any close for any file/process pair relinquishes the locks owned on that file for that process. But note that while an open file description may be shared through fork(), locks are not inherited through fork(). Yet locks may be inherited through one of the exec functions.

The identification of a machine in a network environment is outside the scope of this volume of POSIX.1-2024. Thus, an l_sysid member, such as found in System V, is not included in the locking structure.

Changing of lock types can result in a previously locked region being split into smaller regions.

Mandatory locking was a major feature of the 1984 /usr/group standard.

For advisory file record locking to be effective, all processes that have access to a file must cooperate and use the advisory mechanism before doing I/O on the file. Enforcement-mode record locking is important when it cannot be assumed that all processes are cooperating. For example, if one user uses an editor to update a file at the same time that a second user executes another process that updates the same file and if only one of the two processes is using advisory locking, the processes are not cooperating. Enforcement-mode record locking would protect against accidental collisions.

Secondly, advisory record locking requires a process using locking to bracket each I/O operation with lock (or test) and unlock operations. With enforcement-mode file and record locking, a process can lock the file once and unlock when all I/O operations have been completed. Enforcement-mode record locking provides a base that can be enhanced; for example, with sharable locks. That is, the mechanism could be enhanced to allow a process to lock a file so other processes could read it, but none of them could write it.

Mandatory locks were omitted for several reasons:

Mandatory lock setting was done by multiplexing the set-group-ID bit in most implementations; this was confusing, at best.

The relationship to file truncation as supported in 4.2 BSD was not well specified.

Any publicly readable file could be locked by anyone. Many historical implementations keep the password database in a publicly readable file. A malicious user could thus prohibit logins. Another possibility would be to hold open a long-distance telephone line.

Some demand-paged historical implementations offer memory mapped files, and enforcement cannot be done on that type of file.

Since sleeping on a region is interrupted with any signal, alarm() may be used to provide a timeout facility in applications requiring it. This is useful in deadlock detection. Since implementation of full deadlock detection is not always feasible, the [EDEADLK] error was made optional.

The F_SETOWN_EX and F_GETOWN_EX values for cmd and the associated f_owner_ex structure were adopted from the GNU C library. In addition to the values F_OWNER_PID and F_OWNER_PGRP for the type member, this also has F_OWNER_TID to specify that the pid member contains a thread ID. However, this relies on thread IDs being representable in a pid_t and so was not included in POSIX.1-2024. The aim of adding F_SETOWN_EX and F_GETOWN_EX was to address the inability of F_SETOWN and F_GETOWN to handle process IDs greater than {INT_MAX} and process group IDs greater than {INT_MAX}+1, and this need is satisfied without including F_OWNER_TID.

<a id="tag_17_139_09"></a>

#### FUTURE DIRECTIONS

None.

<a id="tag_17_139_10"></a>

#### SEE ALSO

alarm(), close(), exec, kill(), open(), sigaction()

XBD <fcntl.h>, <signal.h>

<a id="tag_17_139_11"></a>

#### CHANGE HISTORY

First released in Issue 1. Derived from Issue 1 of the SVID.

<a id="tag_17_139_12"></a>

#### Issue 5

The DESCRIPTION is updated for alignment with the POSIX Realtime Extension and the POSIX Threads Extension.

Large File Summit extensions are added.

<a id="tag_17_139_13"></a>

#### Issue 6

In the SYNOPSIS, the optional include of the <sys/types.h> header is removed.

The following new requirements on POSIX implementations derive from alignment with the Single UNIX Specification:

The requirement to include <sys/types.h> has been removed. Although <sys/types.h> was required for conforming implementations of previous POSIX specifications, it was not required for UNIX applications.

In the DESCRIPTION, sentences describing behavior when l_len is negative are now mandated, and the description of unlock (F_UNLOCK) when l_len is non-negative is mandated.

In the ERRORS section, the [EINVAL] error condition has the case mandated when the cmd is invalid, and two [EOVERFLOW] error conditions are added.

The F_GETOWN and F_SETOWN values are added for sockets.

The following changes were made to align with the IEEE P1003.1a draft standard:

Clarification is added that the extent of the bytes locked is determined prior to the blocking action.

The DESCRIPTION is updated for alignment with IEEE Std 1003.1j-2000 by specifying that fcntl() results are unspecified for typed memory objects.

The normative text is updated to avoid use of the term "must" for application requirements.

IEEE Std 1003.1-2001/Cor 2-2004, item XSH/TC2/D6/29 is applied, adding the example to the EXAMPLES section.

<a id="tag_17_139_14"></a>

#### Issue 7

Austin Group Interpretation 1003.1-2001 #150 is applied, clarifying the file status flags returned when cmd is F_GETFL.

Austin Group Interpretation 1003.1-2001 #171 is applied, adding support to set the FD_CLOEXEC flag atomically at open(), and adding the F_DUPFD_CLOEXEC flag.

The optional <unistd.h> header is removed from this function, since <fcntl.h> now defines SEEK_SET, SEEK_CUR, and SEEK_END as part of the Base.

POSIX.1-2008, Technical Corrigendum 1, XSH/TC1-2008/0116 [141] is applied.

POSIX.1-2008, Technical Corrigendum 2, XSH/TC2-2008/0105 [835], XSH/TC2-2008/0106 [677], XSH/TC2-2008/0107 [484], XSH/TC2-2008/0108 [675], and XSH/TC2-2008/0109 [675,677] are applied.

<a id="tag_17_139_15"></a>

#### Issue 8

Austin Group Defect 695 is applied, adding an atomicity requirement to the F_SETOWN operation.

Austin Group Defects 768 and 1671 are applied, adding OFD-owned file locks.

Austin Group Defect 1203 is applied, changing some wording in the RETURN VALUE section to use "shall".

Austin Group Defects 1274 and 1670 are applied, adding F_GETOWN_EX and F_SETOWN_EX.

Austin Group Defect 1318 is applied, adding FD_CLOFORK and F_DUPFD_CLOFORK.

End of informative text.
