> Source: <https://www.php.net/manual/en/security.cgi-bin.force-redirect.php>
> Retrieved: 2026-10-15. Original HTML: kept next to this file as `.source.html`.
> Converted to markdown by text extraction of `div#content`; wording is unchanged,
> whitespace, list markup and code fences were normalized.

## Case 2: using `cgi.force_redirect`

The configuration directive cgi.force_redirect prevents anyone from calling php directly with a URL like http://my.host/cgi-bin/php/secretdir/script.php. Instead, PHP will only parse in this mode if it has gone through a web server redirect rule.

Usually the redirection in the Apache configuration is done with the following directives:

```
Action php-script /cgi-bin/php
AddHandler php-script .php
```

This option has only been tested with the Apache web server, and relies on Apache to set the non-standard CGI environment variable REDIRECT_STATUS on redirected requests. If your web server does not support any way of telling if the request is direct or redirected, you cannot use this option and you must use one of the other ways of running the CGI version documented here.
