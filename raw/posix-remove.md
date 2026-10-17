> Source: <https://pubs.opengroup.org/onlinepubs/9799919799/functions/remove.html>
> Retrieved: 2026-10-17. Original HTML: kept next to this file as `.source.html`.
> Converted with pandoc 3.10 (`-f html -t gfm --wrap=none`, `pandoc/opengroup-body.lua`).

The Open Group Base Specifications Issue 8\
IEEE Std 1003.1-2024\
Copyright © 2001-2024 The IEEE and The Open Group

------------------------------------------------------------------------

<span id="top"></span> <span id="remove"></span> <span id="tag_17_487"></span>

#### <span id="tag_17_487_01"></span>NAME

> remove — remove a file

#### <span id="tag_17_487_02"></span>SYNOPSIS

> `#include <`[`stdio.h`](../basedefs/stdio.h.html)`>`\
> \
> `int remove(const char *`*`path`*`);`\

#### <span id="tag_17_487_03"></span>DESCRIPTION

> <div class="box">
>
> <sup>\[[CX](javascript:open_code('CX'))\]</sup> <img src="../images/opt-start.gif" data-border="0" alt="[Option Start]" /> The functionality described on this reference page is aligned with the ISO C standard. Any conflict between the requirements described here and the ISO C standard is unintentional. This volume of POSIX.1-2024 defers to the ISO C standard. <img src="../images/opt-end.gif" data-border="0" alt="[Option End]" />
>
> </div>
>
> The *remove*() function shall cause the file named by the pathname pointed to by *path* to be no longer accessible by that name. A subsequent attempt to open that file using that name shall fail, unless it is created anew.
>
> <sup>\[[CX](javascript:open_code('CX'))\]</sup> <img src="../images/opt-start.gif" data-border="0" alt="[Option Start]" /> If *path* does not name a directory, *remove*(*path*) shall be equivalent to *unlink*(*path*).
>
> If *path* names a directory, *remove*(*path*) shall be equivalent to *rmdir*(*path*). <img src="../images/opt-end.gif" data-border="0" alt="[Option End]" />

#### <span id="tag_17_487_04"></span>RETURN VALUE

> <sup>\[[CX](javascript:open_code('CX'))\]</sup> <img src="../images/opt-start.gif" data-border="0" alt="[Option Start]" /> Refer to [*rmdir*()](../functions/rmdir.html#tag_17_493) or [*unlink*()](../functions/unlink.html#tag_17_649). <img src="../images/opt-end.gif" data-border="0" alt="[Option End]" />

#### <span id="tag_17_487_05"></span>ERRORS

> <sup>\[[CX](javascript:open_code('CX'))\]</sup> <img src="../images/opt-start.gif" data-border="0" alt="[Option Start]" /> Refer to [*rmdir*()](../functions/rmdir.html#tag_17_493) or [*unlink*()](../functions/unlink.html#tag_17_649). <img src="../images/opt-end.gif" data-border="0" alt="[Option End]" />

------------------------------------------------------------------------

<div class="box">

*The following sections are informative.*

</div>

#### <span id="tag_17_487_06"></span>EXAMPLES

> ##### <span id="tag_17_487_06_01"></span>Removing Access to a File
>
> The following example shows how to remove access to a file named **/home/cnd/old_mods**.
>
>     #include <stdio.h>
>
>
>     int status;
>     ...
>     status = remove("/home/cnd/old_mods");

#### <span id="tag_17_487_07"></span>APPLICATION USAGE

> None.

#### <span id="tag_17_487_08"></span>RATIONALE

> None.

#### <span id="tag_17_487_09"></span>FUTURE DIRECTIONS

> None.

#### <span id="tag_17_487_10"></span>SEE ALSO

> [*rmdir*()](../functions/rmdir.html#tag_17_493), [*unlink*()](../functions/unlink.html#tag_17_649)
>
> XBD [*\<stdio.h\>*](../basedefs/stdio.h.html)

#### <span id="tag_17_487_11"></span>CHANGE HISTORY

> First released in Issue 3. Included for alignment with the POSIX.1-1988 standard and the ISO C standard.

#### <span id="tag_17_487_12"></span>Issue 6

> Extensions beyond the ISO C standard are marked.\
>
> The following new requirements on POSIX implementations derive from alignment with the Single UNIX Specification:
>
> - The DESCRIPTION, RETURN VALUE, and ERRORS sections are updated so that if *path* is not a directory, *remove*() is equivalent to [*unlink*()](../functions/unlink.html), and if it is a directory, it is equivalent to [*rmdir*()](../functions/rmdir.html).

<div class="box">

*End of informative text.*

</div>

------------------------------------------------------------------------

 
