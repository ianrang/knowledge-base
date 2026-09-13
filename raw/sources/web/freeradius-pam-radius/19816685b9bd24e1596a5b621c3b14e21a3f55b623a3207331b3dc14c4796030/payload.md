# FreeRADIUS pam_radius — where the RADIUS client lives

- Source: https://github.com/FreeRADIUS/pam_radius
- Retrieved: 2026-09-13
- Extracted for: whether a remote shell server can use RADIUS without installing anything
  on that server.

## What the module is

> This is the PAM to RADIUS authentication module. It allows any Linux, OSX or Solaris
> machine to become a RADIUS client for authentication.

## Where it is installed

The module and its configuration are installed on the machine being logged into. The
project ships packaging targets for that host:

```
$ ./configure
$ make rpm
$ rpm -ivh rpmbuild/RPMS/x86_64/pam*.rpm
```

```
$ ./configure
$ make deb
$ dpkg -i ../libpam-radius-auth_*.deb
```

The README carries a "Configuration example for sshd+PAM" for both RedHat and Debian
variants, so the module is referenced from the SSH server's own PAM stack.

## Operational model

The local machine runs the PAM module, which talks to a separate RADIUS server. The
README states that the operator must "supply your own RADIUS server to perform the actual
authentication".
