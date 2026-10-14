> Source: <https://pubs.opengroup.org/onlinepubs/9799919799/functions/poll.html>
> Retrieved: 2026-10-15. Original HTML: kept next to this file as `.source.html`.
> Converted to markdown by text extraction of `div#content`; wording is unchanged,
> whitespace, list markup and code fences were normalized.

The Open Group Base Specifications Issue 8 IEEE Std 1003.1-2024 Copyright © 2001-2024 The IEEE and The Open Group

<a id="top"></a>

<a id="poll"></a>

<a id="tag_17_378"></a>

<a id="tag_17_378_01"></a>

#### NAME

poll, ppoll — input/output multiplexing

<a id="tag_17_378_02"></a>

#### SYNOPSIS

`#include <poll.h> int poll(struct pollfd fds[], nfds_t nfds, int timeout); int ppoll(struct pollfd fds[], nfds_t nfds,        const struct timespec *restrict timeout,        const sigset_t *restrict sigmask); `

<a id="tag_17_378_03"></a>

#### DESCRIPTION

The ppoll() function provides applications with a mechanism for multiplexing input/output over a set of file descriptors. For each member of the array pointed to by fds, ppoll() shall examine the given file descriptor for the event(s) specified in events. The number of pollfd structures in the fds array is specified by nfds. The ppoll() function shall identify those file descriptors on which an application can make an attempt to read or write data without blocking, or on which certain events have occurred.

The poll() function shall be equivalent to the ppoll() function, except as follows:

For the poll() function, the timeout period is given in milliseconds in an argument of type int, whereas for the ppoll() function the timeout period is given in seconds and nanoseconds via an argument of type pointer to struct timespec. A timeout of -1 for poll() shall be equivalent to passing a null pointer for the timeout for ppoll().

The poll() function has no sigmask argument; it shall behave as ppoll() does when sigmask is a null pointer.

The fds argument specifies the file descriptors to be examined and the events of interest for each file descriptor. It is a pointer to an array with one member for each open file descriptor of interest. The array's members are pollfd structures within which fd specifies an open file descriptor and events and revents are bitmasks constructed by OR'ing a combination of the following event flags:

- POLLIN

- The file descriptor is ready for reading data other than high-priority data.

- POLLRDNORM

- The file descriptor is ready for reading normal data.

- POLLRDBAND

- The file descriptor is ready for reading priority data.

- POLLPRI

- The file descriptor is ready for reading high-priority data.

- POLLOUT

- The file descriptor is ready for writing normal data.

- POLLWRNORM

- Equivalent to POLLOUT.

- POLLWRBAND

- The file descriptor is ready for writing priority data.

- POLLERR

- An error condition is present on the file descriptor. All error conditions that arise solely from the state of the object underlying the open file description and would be diagnosed by a return of -1 from a read() or write() call on the file descriptor shall be reported as a POLLERR event. This flag is only valid in the revents bitmask; it shall be ignored in the events member.

- POLLHUP

- A device has been disconnected, or a pipe or FIFO has been closed by the last process that had it open for writing. Once set, the hangup state of a FIFO shall persist until some process opens the FIFO for writing or until all read-only file descriptors for the FIFO are closed. This event and POLLOUT are mutually-exclusive. However, this event and POLLIN, POLLRDNORM, POLLRDBAND, or POLLPRI are not mutually-exclusive. This flag is only valid in the revents bitmask; it shall be ignored in the events member.

- POLLNVAL

- The specified fd value is not an open file descriptor. This flag is only valid in the revents member; it shall be ignored in the events member.

A file descriptor shall be considered ready for reading when a call to an input function with O_NONBLOCK clear would not block, whether or not the function would transfer data successfully. (The function might return data, an end-of-file indication, or an error other than one indicating that it is blocked, and in each of these cases the descriptor is considered ready for reading.) A file descriptor shall be considered ready for writing when a call to an output function with O_NONBLOCK clear would not block, whether or not the function would transfer data successfully. How much data could be written without blocking depends upon the object underlying the open file description and its current state.

The significance and semantics of normal, priority, and high-priority data are file and device-specific. The semantics of device disconnection are device-specific.

If the value of fd is less than 0, events shall be ignored, and revents shall be set to 0 in that entry on return from poll() or ppoll().

In each pollfd structure, poll() or ppoll() shall clear the revents member, except that where the application requested a report on a condition by setting one of the bits of events listed above, poll() or ppoll() shall set the corresponding bit in revents if the requested condition is true. In addition, poll() or ppoll() shall set the POLLHUP, POLLERR, and POLLNVAL flag in revents if the condition is true, even if the application did not set the corresponding bit in events.

The timeout argument controls how long the poll() or ppoll() function shall wait before timing out. If the timeout argument is positive for poll() or not a null pointer for ppoll(), it specifies a maximum interval to wait for the poll to complete. If the specified time interval expires without any of the defined events having occurred, the function shall return. If the timeout argument is -1 for poll() or a null pointer for ppoll(), then the call shall block indefinitely until at least one descriptor meets the specified criteria or until the call is interrupted. To effect a poll, the application shall ensure that the timeout argument for poll() is 0, or for ppoll() is not a null pointer and points to a zero-valued timespec structure.

Implementations may place limitations on the maximum timeout interval supported. All implementations shall support a maximum timeout interval of at least 31 days for ppoll(). If the timeout argument specifies a timeout interval greater than the implementation-defined maximum value, the maximum value shall be used as the actual timeout value. Implementations may also place limitations on the granularity of timeout intervals. If the requested timeout interval requires a finer granularity than the implementation supports, the actual timeout interval shall be rounded up to the next supported value.

The poll() and ppoll() functions shall not be affected by the O_NONBLOCK flag.

The poll() and ppoll() functions shall support regular files, terminal and pseudo-terminal devices, FIFOs, pipes, and sockets. The behavior of poll() and ppoll() on elements of fds that refer to other types of file is unspecified.

Regular files shall always poll TRUE for reading and writing.

A file descriptor for a socket that is listening for connections shall indicate that it is ready for reading, once connections are available. A file descriptor for a socket that is connecting asynchronously shall indicate that it is ready for writing, once a connection has been established.

Provided the application does not perform any action that results in unspecified or undefined behavior, the value of the fd and events members of each element of fds shall not be modified by poll() or ppoll().

If sigmask is not a null pointer, the ppoll() function shall replace the signal mask of the caller by the set of signals pointed to by sigmask before examining the descriptors, and shall restore the signal mask of the calling thread before returning. If a signal is unmasked as a result of the signal mask being altered by ppoll(), and a signal-catching function is called for that signal during the execution of the ppoll() function, and SA_RESTART is clear for the interrupting signal, then

If none of the defined events have occurred on any selected file descriptor, ppoll() shall immediately fail with the [EINTR] error after the signal-catching function returns.

If one or more of the defined events have occurred, it is unspecified whether ppoll() behaves the same as if none of the events had occurred (failing with [EINTR] as above) or behaves the same as if it was not interrupted (returning the total number of pollfd structures that have selected events).

If a thread is canceled during a ppoll() call, it is unspecified whether the signal mask in effect when executing the registered cleanup functions is the original signal mask or the signal mask installed as part of the ppoll() call.

<a id="tag_17_378_04"></a>

#### RETURN VALUE

Upon successful completion, a non-negative value shall be returned. A positive value shall indicate the total number of pollfd structures that have selected events (that is, those for which the revents member is non-zero). A value of 0 shall indicate that the call timed out and no file descriptors have been selected. Upon failure, -1 shall be returned and errno set to indicate the error.

<a id="tag_17_378_05"></a>

#### ERRORS

The poll() and ppoll() functions shall fail if:

- [EAGAIN]

- The allocation of internal data structures failed but a subsequent request may succeed.

- [EINTR]

- A signal was caught during poll() or ppoll().

- [EINVAL]

- The nfds argument is greater than {OPEN_MAX}.

The ppoll() function shall fail if:

- [EINVAL]

- An invalid timeout interval was specified.

The following sections are informative.

<a id="tag_17_378_06"></a>

#### EXAMPLES

None.

<a id="tag_17_378_07"></a>

#### APPLICATION USAGE

Other than the difference in the precision of the requested timeout, the following ppoll() call:

```
ready = ppoll(&fds, nfds, tmo_p, &sigmask);
```

is equivalent to atomically executing the following calls:

```
sigset_t origmask;
int timeout;
 
timeout = (tmo_p == NULL) ? -1 :
    (tmo_p->tv_sec * 1000 + tmo_p->tv_nsec / 1000000);
pthread_sigmask(SIG_SETMASK, &sigmask, &origmask);
ready = poll(&fds, nfds, timeout);
pthread_sigmask(SIG_SETMASK, &origmask, NULL);
```

When a poll() or ppoll() call indicates a file descriptor is ready for reading, this means that if an attempt to read data had been made at the time that the status of the file descriptor was checked, it would have returned at least one byte of data, an end-of-file indication, or an error, without blocking (even if O_NONBLOCK is clear). When a poll() or ppoll() call indicates that a file descriptor is ready for writing, this means that if an attempt to write one byte of data had been made at the time that the status of the file descriptor was checked, it would have written that byte or returned an error, without blocking. However, if an attempt to write more than one byte had been made, it might have blocked (if O_NONBLOCK is clear). In both cases, by the time the call returns and a subsequent I/O operation is attempted, the state of the file descriptor might have changed (for example, because another thread read or wrote some data) and, if O_NONBLOCK is clear, there is no guarantee that the operation will not block (unless it would not block for some other reason, such as setting MIN=0 and TIME=0 for a terminal in non-canonical mode). Therefore it is recommended that applications always set O_NONBLOCK on file descriptors whose readiness for I/O they query with poll() or ppoll().

The error conditions specified for read() and write() that are reported as POLLERR events are only those that arise solely from the state of the object underlying the open file description. They do not include, for example, [EAGAIN] as this relates to the state of the open file description not (solely) the object underlying it.

Application writers should note that repeating a poll() or ppoll() call which indicated that I/O was possible on one or more of the file descriptors given, without causing some change to the state, either by altering the fds array or causing appropriate input or output to occur on at least one file descriptor indicated as ready, will result in "busy waiting"—a subsequent call will always return immediately indicating the same (or perhaps more) events as the previous one.

<a id="tag_17_378_08"></a>

#### RATIONALE

The POLLHUP event does not occur for FIFOs just because the FIFO is not open for writing. It only occurs when the FIFO is closed by the last writer and persists until some process opens the FIFO for writing or until all read-only file descriptors for the FIFO are closed.

Code which wants to avoid the ambiguity of the signal mask for thread cancellation handlers can install an additional cancellation handler which resets the signal mask to the expected value:

```
void cleanup(void *arg)
{
    sigset_t *ss = (sigset_t *) arg;
    pthread_sigmask(SIG_SETMASK, ss, NULL);
}
int call_ppoll(struct pollfd fds[], nfds_t nfds,
    const struct timespec *restrict timeout,
    const sigset_t *restrict sigmask)
{
    sigset_t oldmask;
    int result;
    pthread_sigmask(SIG_SETMASK, NULL, &oldmask);
    pthread_cleanup_push(cleanup, &oldmask);
    result = ppoll(fds, nfds, timeout, sigmask);
    pthread_cleanup_pop(0);
    return result;
}
```

<a id="tag_17_378_09"></a>

#### FUTURE DIRECTIONS

None.

<a id="tag_17_378_10"></a>

#### SEE ALSO

pselect(), read(), write()

XBD <poll.h>

<a id="tag_17_378_11"></a>

#### CHANGE HISTORY

First released in Issue 4, Version 2.

<a id="tag_17_378_12"></a>

#### Issue 5

Moved from X/OPEN UNIX extension to BASE.

The description of POLLWRBAND is updated.

<a id="tag_17_378_13"></a>

#### Issue 6

Text referring to sockets is added to the DESCRIPTION.

Functionality relating to the XSI STREAMS Option Group is marked.

The Open Group Corrigendum U055/3 is applied, updating the DESCRIPTION of POLLWRBAND.

IEEE Std 1003.1-2001/Cor 2-2004, item XSH/TC2/D6/66 is applied, correcting the spacing in the EXAMPLES section.

<a id="tag_17_378_14"></a>

#### Issue 7

Austin Group Interpretation 1003.1-2001 #209 is applied, clarifying the POLLHUP event.

The poll() function is moved from the XSI option to the Base.

Functionality relating to the XSI STREAMS option is marked obsolescent.

POSIX.1-2008, Technical Corrigendum 2, XSH/TC2-2008/0249 [623] and XSH/TC2-2008/0250 [683] are applied.

<a id="tag_17_378_15"></a>

#### Issue 8

Austin Group Defect 1263 is applied, adding ppoll().

Austin Group Defect 1330 is applied, removing obsolescent interfaces.

Austin Group Defect 1448 is applied, aligning the wording relating to file descriptor readiness with pselect() and changing the APPLICATION USAGE section.

End of informative text.
