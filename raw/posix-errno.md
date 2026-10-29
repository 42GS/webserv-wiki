> Source: <https://pubs.opengroup.org/onlinepubs/9799919799/functions/errno.html>
> Retrieved: 2026-10-29. Original HTML: kept next to this file as `.source.html`.
> Converted with pandoc 3.10 (`-f html -t gfm --wrap=none`, `pandoc/opengroup-body.lua`).

The Open Group Base Specifications Issue 8\
IEEE Std 1003.1-2024\
Copyright © 2001-2024 The IEEE and The Open Group

------------------------------------------------------------------------

<span id="top"></span> <span id="errno"></span> <span id="tag_17_128"></span>

#### <span id="tag_17_128_01"></span>NAME

> errno — error return value

#### <span id="tag_17_128_02"></span>SYNOPSIS

> `#include <errno.h>`

#### <span id="tag_17_128_03"></span>DESCRIPTION

> The lvalue to which the macro *errno* expands is used by many functions to return error values.
>
> Many functions provide an error number in *errno*, which has type **int** and is defined in [*\<errno.h\>*](../basedefs/errno.h.html). The value of *errno* in the initial thread shall be zero at program startup (the initial value of *errno* in other threads is an indeterminate value) and shall otherwise be defined only after a call to a function for which it is explicitly stated to be set and until it is changed by the next function call or if the application assigns it a value. The value of *errno* should only be examined when it is indicated to be valid by a function's return value. Applications shall obtain the definition of *errno* by the inclusion of [*\<errno.h\>*](../basedefs/errno.h.html). No function in this volume of POSIX.1-2024 shall set *errno* to 0. The setting of *errno* after a successful call to a function is unspecified unless the description of that function specifies that *errno* shall not be modified.
>
> If the macro definition is suppressed in order to access an actual object, or a program defines an identifier with the name *errno*, the behavior is undefined.
>
> The symbolic values stored in *errno* are documented in the ERRORS sections on all relevant pages.

#### <span id="tag_17_128_04"></span>RETURN VALUE

> None.

#### <span id="tag_17_128_05"></span>ERRORS

> None.

------------------------------------------------------------------------

<div class="box">

*The following sections are informative.*

</div>

#### <span id="tag_17_128_06"></span>EXAMPLES

> None.

#### <span id="tag_17_128_07"></span>APPLICATION USAGE

> Previously both POSIX and X/Open documents were more restrictive than the ISO C standard in that they required *errno* to be defined as an external variable, whereas the ISO C standard required only that *errno* be defined as a modifiable lvalue with type **int**.
>
> An application that needs to examine the value of *errno* to determine the error should set it to 0 before a function call, then inspect it before a subsequent function call.

#### <span id="tag_17_128_08"></span>RATIONALE

> None.

#### <span id="tag_17_128_09"></span>FUTURE DIRECTIONS

> None.

#### <span id="tag_17_128_10"></span>SEE ALSO

> [*2.3 Error Numbers*](../functions/V2_chap02.html#tag_16_03)
>
> XBD [*\<errno.h\>*](../basedefs/errno.h.html)

#### <span id="tag_17_128_11"></span>CHANGE HISTORY

> First released in Issue 1. Derived from Issue 1 of the SVID.

#### <span id="tag_17_128_12"></span>Issue 5

> The following sentence is deleted from the DESCRIPTION: "The value of *errno* is 0 at program start-up, but is never set to 0 by any XSI function".\
>
> The DESCRIPTION also no longer states that conforming implementations may support the declaration:
>
>     extern int errno;

#### <span id="tag_17_128_13"></span>Issue 6

> Obsolescent text regarding defining *errno* as:
>
>     extern int errno
>
> is removed.
>
> Text regarding no function setting *errno* to zero to indicate an error is changed to no function shall set *errno* to zero. This is for alignment with the ISO/IEC 9899:1999 standard.
>
> IEEE Std 1003.1-2001/Cor 2-2004, item XSH/TC2/D6/23 is applied, adding text to the DESCRIPTION stating that the setting of *errno* after a successful call to a function is unspecified unless the description of the function requires that it will not be modified.

#### <span id="tag_17_128_14"></span>Issue 8

> Austin Group Defect 1302 is applied, aligning this macro with the ISO/IEC 9899:2018 standard.

<div class="box">

*End of informative text.*

</div>

------------------------------------------------------------------------

 
