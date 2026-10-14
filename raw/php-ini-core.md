> Source: <https://www.php.net/manual/en/ini.core.php>
> Retrieved: 2026-10-15. Original HTML: kept next to this file as `.source.html`.
> Converted to markdown by text extraction of `div#content`; wording is unchanged,
> whitespace, list markup and code fences were normalized.

## Description of core php.ini directives

This list includes the core php.ini directives you can set to configure your PHP setup. Directives handled by extensions are listed and detailed at the extension documentation pages respectively; Information on the session directives for example can be found at the sessions page.

Note:

The defaults listed here are used when php.ini is not loaded; the values for the production and development php.ini may vary.

## Language Options

Language and Misc Configuration Options

**Name**

**Default**

**Changeable**

**Changelog**

short_open_tag "1" `INI_PERDIR`

precision "14" `INI_ALL`

serialize_precision "-1" `INI_ALL` Prior to PHP 7.1.0, the default value was 17.

disable_functions "" `INI_SYSTEM` only

disable_classes "" php.ini only Removed as of PHP 8.5.0

exit_on_timeout "" `INI_ALL`

expose_php "1" php.ini only

hard_timeout "2" `INI_SYSTEM` Available as of PHP 7.1.0.

zend.exception_ignore_args "0" `INI_ALL` Available as of PHP 7.4.0

zend.multibyte "0" `INI_ALL`

zend.script_encoding NULL `INI_ALL`

zend.detect_unicode NULL `INI_ALL`

zend.signal_check "0" `INI_SYSTEM`

zend.assertions "1" `INI_ALL` with restrictions

zend.exception_string_param_max_len "15" `INI_ALL` Available as of PHP 8.0.0.

Here's a short explanation of the configuration directives.

- `short_open_tag` bool

Tells PHP whether the short form (`<? ?>`) of PHP's open tag should be allowed. If you want to use PHP in combination with XML, you can disable this option in order to use `<?xml ?>` inline. Otherwise, you can print it with PHP, for example: `<?php echo '<?xml version="1.0"?>'; ?>`. Also, if disabled, you must use the long form of the PHP open tag (`<?php ?>`).

Note:

This directive does not affect the shorthand `<?=`, which is always available.

- `precision` int

The number of significant digits displayed in floating point numbers. `-1` means that an enhanced algorithm for rounding such numbers will be used.

- `serialize_precision` int

The number of significant digits stored while serializing floating point numbers. `-1` means that an enhanced algorithm for rounding such numbers will be used.

- `expose_php` bool

Exposes to the world that PHP is installed on the server, which includes the PHP version within the HTTP header (e.g., X-Powered-By: PHP/5.3.7).

- `disable_functions` string

This directive allows certain functions to be disabled. It takes a comma-delimited list of function names. As of PHP 8.0.0, disabling a function removes its definition, allowing userland to redefine it. Prior to PHP 8.0.0, disabling a function just prevented the function from being invoked.

Only internal functions can be disabled using this directive. User-defined functions are unaffected.

This directive must be set in php.ini. It cannot be set in httpd.conf.

Warning

This directive can be circumvented and should not be considered a sufficient security measure for shared hosting environments.

- `disable_classes` string

This directive allows certain classes to be disabled. It takes a comma-delimited list of class names. Disabling a class just prevents the class's instantiation.

Only internal classes can be disabled using this directive. User-defined classes are unaffected.

This directive must be set in php.ini. It cannot be set in httpd.conf.

Warning

This directive can be circumvented and should not be considered a sufficient security measure for shared hosting environments.

Warning

This feature has been REMOVED as of PHP 8.5.0.

- `zend.assertions` int

When set to `1`, assertion code will be generated and executed (development mode). When set to `0`, assertion code will be generated but it will be skipped (not executed) at runtime. When set to `-1`, assertion code will not be generated, making the assertions zero-cost (production mode).

Note:

If a process is started in production mode, zend.assertions cannot be changed at runtime, since the code for assertions was not generated.

If a process is started in development mode, zend.assertions cannot be set to `-1` at runtime.

- `zend.exception_string_param_max_len` int

The maximum length of string function arguments in stringified stack traces. Must range between `"0"` and `"1000000"`.

- `hard_timeout` int

When the timeout set in max_execution_time has been hit, the PHP runtime will tear down resources gracefully. If something gets stuck while this happens, the hard timeout will tick for the set amount of seconds. When the hard timeout is hit, PHP will exit ungracefully. When set to 0, the hard timeout will never activate.

When PHP stops from a hard timeout, it will look something like this:

```
Fatal error: Maximum execution time of 30+2 seconds exceeded (terminated) in Unknown on line 0
```

- `zend.exception_ignore_args` bool

Excludes arguments from stack traces generated from exceptions.

- `zend.multibyte` bool

Enables parsing of source files in multibyte encodings. Enabling zend.multibyte is required to use character encodings like SJIS, BIG5, etc that contain special characters in multibyte string data. ISO-8859-1 compatible encodings like UTF-8, EUC, etc do not require this option.

Enabling zend.multibyte requires the mbstring extension to be available.

- `zend.script_encoding` string

This value will be used unless a declare(encoding=...) directive appears at the top of the script. When ISO-8859-1 incompatible encoding is used, both zend.multibyte and zend.script_encoding must be used.

Literal strings will be transliterated from zend.script_encoding to mbstring.internal_encoding, as if mb_convert_encoding() would have been called.

- `zend.detect_unicode` bool

Check for BOM (Byte Order Mark) and see if the file contains valid multibyte characters. This detection is performed before processing of __halt_compiler(). Available only in Zend Multibyte mode.

- `zend.signal_check` bool

To check for replaced signal handlers on shutdown.

- `exit_on_timeout` bool

This is an Apache1 mod_php-only directive that forces an Apache child to exit if a PHP execution timeout occurred. Such a timeout causes an internal longjmp() call in Apache1 which can leave some extensions in an inconsistent state. By terminating the process any outstanding locks or memory will be cleaned up.

## Resource Limits

Resource Limits

**Name**

**Default**

**Changeable**

**Changelog**

memory_limit "128M" `INI_ALL`

max_memory_limit "-1" `INI_SYSTEM` Available as of PHP 8.5.0

Here's a short explanation of the configuration directives.

- `memory_limit` int

This sets the maximum amount of memory in bytes that a script is allowed to allocate. This helps prevent poorly written scripts for eating up all available memory on a server. Note that to have no memory limit, set this directive to `-1`.

When an int is used, the value is measured in bytes. Shorthand notation, as described in this FAQ, may also be used.

- `max_memory_limit` int

Available as of PHP 8.5.0. This startup-only setting controls the maximum value that memory_limit may be configured to, either at startup or at runtime (e.g. via ini_set()). Setting memory_limit to a value exceeding `max_memory_limit` results in a warning and the value being capped. Set to `-1` (the default) to impose no upper bound.

When an int is used, the value is measured in bytes. Shorthand notation, as described in this FAQ, may also be used.

See also: max_execution_time.

## Performance Tuning

Performance Tuning

**Name**

**Default**

**Changeable**

**Changelog**

realpath_cache_size "4M" `INI_SYSTEM` Prior to PHP 7.0.16 and 7.1.2, the default was `"16K"`

realpath_cache_ttl "120" `INI_SYSTEM`

Note:

Using open_basedir will disable the realpath cache.

Here's a short explanation of the configuration directives.

- `realpath_cache_size` int

Determines the size of the realpath cache to be used by PHP. This value should be increased on systems where PHP opens many files, to reflect the quantity of the file operations performed.

The size represents the total number of bytes in the path strings stored, plus the size of the data associated with the cache entry. This means that in order to store longer paths in the cache, the cache size must be larger. This value does not directly control the number of distinct paths that can be cached.

The size required for the cache entry data is system dependent.

- `realpath_cache_ttl` int

Duration of time (in seconds) for which to cache realpath information for a given file or directory. For systems with rarely changing files, consider increasing the value.

## Data Handling

Data Handling Configuration Options

**Name**

**Default**

**Changeable**

**Changelog**

arg_separator.output "&" `INI_ALL`

arg_separator.input "&" `INI_PERDIR`

variables_order "EGPCS" `INI_PERDIR`

request_order "" `INI_PERDIR`

auto_globals_jit "1" `INI_PERDIR`

register_argc_argv "1" `INI_PERDIR` Deprecated as of PHP 8.5.0

enable_post_data_reading "1" `INI_PERDIR`

post_max_size "8M" `INI_PERDIR`

auto_prepend_file NULL `INI_PERDIR`

auto_append_file NULL `INI_PERDIR`

default_mimetype "text/html" `INI_ALL`

default_charset "UTF-8" `INI_ALL`

input_encoding "" `INI_ALL`

output_encoding "" `INI_ALL`

internal_encoding "" `INI_ALL`

Here's a short explanation of the configuration directives.

- `arg_separator.output` string

The separator used in PHP generated URLs to separate arguments.

- `arg_separator.input` string

List of separator(s) used by PHP to parse input URLs into variables.

Note:

Every character in this directive is considered as separator!

- `variables_order` string

Sets the order of the EGPCS (`E`nvironment, `G`et, `P`ost, `C`ookie, and `S`erver) variable parsing. For example, if variables_order is set to `"SP"` then PHP will create the superglobals $_SERVER and $_POST, but not create $_ENV, $_GET, and $_COOKIE. Setting to "" means no superglobals will be set.

Warning

In both the CGI and FastCGI SAPIs, $_SERVER is also populated by values from the environment; `S` is always equivalent to `ES` regardless of the placement of `E` elsewhere in this directive.

Note:

The content and order of $_REQUEST is also affected by this directive.

- `request_order` string

This directive describes the order in which PHP registers GET, POST and Cookie variables into the _REQUEST array. Registration is done from left to right, newer values override older values.

If this directive is not set, variables_order is used for $_REQUEST contents.

Note that the default distribution php.ini files does not contain the `'C'` for cookies, due to security concerns.

- `auto_globals_jit` bool

When enabled, the SERVER, REQUEST, and ENV variables are created when they're first used (Just In Time) instead of when the script starts. If these variables are not used within a script, having this directive on will result in a performance gain.

Warning

Usage of SERVER, REQUEST, and ENV variables is checked during the compile time so using them through e.g. variable variables will not cause their initialization.

- `register_argc_argv` bool

Tells PHP whether to declare the argv & argc variables (that would contain the GET information).

See also command line.

Warning

This feature has been DEPRECATED as of PHP 8.5.0. Relying on this feature is highly discouraged.

Note:

Deriving `$_SERVER['argc']` and `$_SERVER['argv']` from the query string for non-CLI SAPIs has been deprecated. Configure `register_argc_argv=0` and switch to either $_GET or `$_SERVER['QUERY_STRING']` to access the information, after verifying that the usage is safe.

- `enable_post_data_reading` bool

Disabling this option causes $_POST and $_FILES not to be populated. The request body remains unconsumed in php://input and can be read manually or parsed via request_parse_body(). This can be useful to proxy requests or to process the POST data in a memory efficient fashion.

- `post_max_size` int

Sets max size of post data allowed. This setting also affects file upload. To upload large files, this value must be larger than upload_max_filesize.

Generally speaking, memory_limit should be larger than `post_max_size`.

When an int is used, the value is measured in bytes. Shorthand notation, as described in this FAQ, may also be used.

If the size of post data is greater than post_max_size, the $_POST and $_FILES superglobals are empty. This can be tracked in various ways, e.g. by passing the $_GET variable to the script processing the data, i.e. `<form action="edit.php?processed=1">`, and then checking if $_GET['processed'] is set.

Note:

PHP allows shortcuts for byte values, including K (kilo), M (mega) and G (giga). PHP will do the conversions automatically if you use any of these. Be careful not to exceed the 32 bit signed integer limit (if you're using 32bit versions) as it will cause your script to fail.

Changelog for `post_max_size`

**Version**

**Description**

5.3.4 `post_max_size` = 0 will not disable the limit when the content type is application/x-www-form-urlencoded or is not registered with PHP.

5.3.2 , 5.2.12 Allow unlimited post size by setting `post_max_size` to 0.

- `auto_prepend_file` string

Specifies the name of a file that is automatically parsed before the main file. The file is included as if it was called with the require function, so include_path is used.

The special value `none` disables auto-prepending.

- `auto_append_file` string

Specifies the name of a file that is automatically parsed after the main file. The file is included as if it was called with the require function, so include_path is used.

The special value `none` disables auto-appending.

Note:

If the script is terminated with exit(), auto-append will not occur.

- `default_mimetype` string

By default, PHP will output a media type using the Content-Type header. To disable this, simply set it to be empty.

PHP's built-in default media type is set to text/html.

- `default_charset` string

"UTF-8" is the default value and its value is used as the default character encoding for htmlentities(), html_entity_decode() and htmlspecialchars() if the `encoding` parameter is omitted. The value of `default_charset` will also be used to set the default character set for iconv functions if the `iconv.input_encoding`, `iconv.output_encoding` and `iconv.internal_encoding` configuration options are unset, and for mbstring functions if the `mbstring.http_input` `mbstring.http_output` `mbstring.internal_encoding` configuration option is unset.

All versions of PHP will use this value as the charset within the default Content-Type header sent by PHP if the header isn't overridden by a call to header().

Setting `default_charset` to an empty value is not recommended.

- `input_encoding` string

This setting is used for multibyte modules such as mbstring and iconv. Default is empty.

- `output_encoding` string

This setting is used for multibyte modules such as mbstring and iconv. Default is empty.

- `internal_encoding` string

This setting is used for multibyte modules such as mbstring and iconv. Default is empty. If empty, default_charset is used.

## Paths and Directories

Paths and Directories Configuration Options

**Name**

**Default**

**Changeable**

**Changelog**

include_path ".;/path/to/php/pear" `INI_ALL`

open_basedir NULL `INI_ALL`

doc_root NULL `INI_SYSTEM`

user_dir NULL `INI_SYSTEM`

user_ini.cache_ttl "300" `INI_SYSTEM`

user_ini.filename ".user.ini" `INI_SYSTEM`

extension_dir "/path/to/php" `INI_SYSTEM`

extension NULL php.ini only

zend_extension NULL php.ini only

cgi.check_shebang_line "1" `INI_SYSTEM`

cgi.discard_path "0" `INI_SYSTEM`

cgi.fix_pathinfo "1" `INI_SYSTEM`

cgi.force_redirect "1" `INI_SYSTEM`

cgi.nph "0" `INI_SYSTEM`

cgi.redirect_status_env NULL `INI_SYSTEM`

cgi.rfc2616_headers "0" `INI_ALL`

fastcgi.impersonate "0" `INI_SYSTEM`

fastcgi.logging "1" `INI_SYSTEM`

Here's a short explanation of the configuration directives.

- `include_path` string

Specifies a list of directories where the require, include, fopen(), file(), readfile() and file_get_contents() functions look for files. The format is like the system's PATH environment variable: a list of directories separated with a colon in Unix or semicolon in Windows.

PHP considers each entry in the include path separately when looking for files to include. It will check the first path, and if it doesn't find it, check the next path, until it either locates the included file or returns with an `E_WARNING` or an `E_ERROR`. You may modify or set your include path at runtime using set_include_path().

Example #1 Unix include_path

```
include_path=".:/php/includes"
```

Example #2 Windows include_path

```
include_path=".;c:\php\includes"
```

Using a `.` in the include path allows for relative includes as it means the current directory. However, it is more efficient to explicitly use `include './file'` than having PHP always check the current directory for every include.

Note:

`ENV` variables are also accessible in .ini files. As such it is possible to reference the home directory using `${LOGIN}` and `${USER}`.

Environment variables may vary between Server APIs as those environments may be different.

Example #3 Unix include_path using ${USER} env variable

```
include_path = ".:${USER}/pear/php"
```

- `open_basedir` string

Limit the files that can be accessed by PHP to the specified directory-tree, including the file itself.

When a script tries to access the filesystem, for example using include, or fopen(), the location of the file is checked. When the file is outside the specified directory-tree, PHP will refuse to access it. All symbolic links are resolved, so it's not possible to avoid this restriction with a symlink. If the file doesn't exist then the symlink couldn't be resolved and the filename is compared to (a resolved) open_basedir.

open_basedir can affect more than just filesystem functions; for example if `MySQL` is configured to use `mysqlnd` drivers, `LOAD DATA INFILE` will be affected by open_basedir. Much of the extended functionality of PHP uses `open_basedir` in this way.

The special value `.` indicates that the working directory of the script will be used as the base-directory. This is, however, a little dangerous as the working directory of the script can easily be changed with chdir().

In httpd.conf, open_basedir can be turned off (e.g. for some virtual hosts) the same way as any other configuration directive with "`php_admin_value open_basedir none`".

Under Windows, separate the directories with a semicolon. On all other systems, separate the directories with a colon. As an Apache module, open_basedir paths from parent directories are now automatically inherited.

The restriction specified with open_basedir is a directory name, not a prefix.

The default is to allow all files to be opened.

Note:

open_basedir can be tightened at run-time. This means that if open_basedir is set to `/www/` in php.ini a script can tighten the configuration to `/www/tmp/` at run-time with ini_set(). When listing several directories, you can use the `PATH_SEPARATOR` constant as a separator regardless of the operating system.

As of PHP 8.3.0, open_basedir no longer accepts a paths containing the parent directory (`..`) when set at runtime using ini_set().

Note:

Using open_basedir will set realpath_cache_size to `0` and thus disable the realpath cache.

Warning

open_basedir does not restrict access to Unix domain sockets. PHP socket functions such as stream_socket_client() and fsockopen() can connect to a Unix socket path (e.g. unix:///var/run/docker.sock) regardless of the open_basedir setting.

Caution

`open_basedir` is just an extra safety net, that is in no way comprehensive, and can therefore not be relied upon when security is needed.

- `doc_root` string

PHP's "root directory" on the server. Only used if non-empty. If PHP was not compiled with FORCE_REDIRECT, you should set doc_root if you are running PHP as a CGI under any web server (other than IIS). The alternative is to use the cgi.force_redirect configuration below.

- `user_ini.cache_ttl` int

- `user_ini.filename` string

- `user_dir` string

The base name of the directory used on a user's home directory for PHP files, for example public_html .

- `extension_dir` string

In what directory PHP should look for dynamically loadable extensions. It is recommended to specify an absolute path. See also: enable_dl, and dl().

- `extension` string

Which dynamically loadable extensions to load when PHP starts up.

- `zend_extension` string

Name of dynamically loadable Zend extension (for example XDebug) to load when PHP starts up.

- `cgi.check_shebang_line` bool

Controls whether CGI PHP checks for line starting with `#!` (shebang) at the top of the running script. This line might be needed if the script support running both as stand-alone script and via PHP CGI. PHP in CGI mode skips this line and ignores its content if this directive is turned on.

- `cgi.discard_path` bool

If this is enabled, the PHP CGI binary can safely be placed outside of the web tree and people will not be able to circumvent .htaccess security.

- `cgi.fix_pathinfo` bool

Provides real `PATH_INFO`/ `PATH_TRANSLATED` support for CGI. PHP's previous behaviour was to set `PATH_TRANSLATED` to `SCRIPT_FILENAME`, and to not grok what ` PATH_INFO` is. For more information on `PATH_INFO`, see the CGI specs. Setting this to `1` will cause PHP CGI to fix its paths to conform to the spec. A setting of zero causes PHP to behave as before. It is turned on by default. You should fix your scripts to use `SCRIPT_FILENAME` rather than `PATH_TRANSLATED`.

- `cgi.force_redirect` bool

cgi.force_redirect is necessary to provide security running PHP as a CGI under most web servers. Left undefined, PHP turns this on by default. You can turn it off at your own risk.

Note:

Windows Users: When using IIS this option must be turned off. For OmniHTTPD or Xitami the same applies.

- `cgi.nph` bool

If cgi.nph is enabled it will force cgi to always sent Status: 200 with every request.

- `cgi.redirect_status_env` string

If cgi.force_redirect is turned on, and you are not running under Apache or Netscape (iPlanet) web servers, you may need to set an environment variable name that PHP will look for to know it is OK to continue execution.

Note:

Setting this variable may cause security issues, know what you are doing first.

- `cgi.rfc2616_headers` bool

Tells PHP what type of headers to use when sending HTTP response code. If it is disabled, PHP sends a » RFC 3875 "Status:" header that is supported by Apache and other web servers. When this option is enabled, PHP will send » RFC 2616 compliant headers.

If this option is enabled, and you are running PHP in a CGI environment (e.g. PHP-FPM) you should not use standard RFC 2616 style HTTP status response headers, you should instead use their RFC 3875 equivalent e.g. instead of header("HTTP/1.0 404 Not found"); you should use header("Status: 404 Not Found");

Leave it disabled unless you know what you're doing.

- `fastcgi.impersonate` bool

FastCGI under IIS (on WINNT based OS) supports the ability to impersonate security tokens of the calling client. This allows IIS to define the security context that the request runs under. mod_fastcgi under Apache does not currently support this feature (03/17/2002). Enable if running under IIS. Default is disabled.

- `fastcgi.logging` bool

Turns on SAPI logging when using FastCGI. Default is to enable logging.

## File Uploads

File Uploads Configuration Options

**Name**

**Default**

**Changeable**

**Changelog**

file_uploads "1" `INI_SYSTEM`

upload_tmp_dir NULL `INI_SYSTEM`

max_input_nesting_level 64 `INI_PERDIR`

max_input_vars 1000 `INI_PERDIR`

upload_max_filesize "2M" `INI_PERDIR`

max_file_uploads 20 `INI_PERDIR`

Here's a short explanation of the configuration directives.

- `file_uploads` bool

Whether or not to allow HTTP file uploads. See also the upload_max_filesize, upload_tmp_dir, and post_max_size directives.

- `upload_tmp_dir` string

The temporary directory used for storing files when doing file upload. Must be writable by whatever user PHP is running as. If not specified PHP will use the system's default.

If the directory specified here is not writable, PHP falls back to the system default temporary directory. If open_basedir is on, then the system default directory must be allowed for an upload to succeed.

- `upload_max_filesize` int

The maximum size of an uploaded file.

post_max_size must be larger than this value.

When an int is used, the value is measured in bytes. Shorthand notation, as described in this FAQ, may also be used.

- `max_file_uploads` int

The maximum number of files allowed to be uploaded simultaneously. Upload fields left blank on submission do not count towards this limit.

## General SQL

General SQL Configuration Options

**Name**

**Default**

**Changeable**

**Changelog**

sql.safe_mode "0" `INI_SYSTEM` Removed as of PHP 7.2.0

Here's a short explanation of the configuration directives.

- `sql.safe_mode` bool

If turned on, database connection functions that specify default values will use those values in place of any user-supplied arguments. For details on the default values, see the documentation for the relevant connection functions.

Warning

This feature has been REMOVED as of PHP 7.2.0.

## Windows Specific

Windows Specific Configuration Options

**Name**

**Default**

**Changeable**

**Changelog**

windows.show_crt_warning "0" `INI_ALL`

Here's a short explanation of the configuration directives.

- `windows.show_crt_warning` bool

This directive shows the Windows CRT warnings when enabled.
