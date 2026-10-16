## [ANXS](https://github.com/ANXS) - openssh

[![CI Status](https://img.shields.io/github/actions/workflow/status/anxs/openssh/ci.yml)](https://github.com/ANXS/openssh/actions/workflows/ci.yml)
[![Maintenance](https://img.shields.io/maintenance/yes/2026.svg)](https://github.com/ANXS/openssh)
[![Ansible Role](https://img.shields.io/ansible/role/d/anxs/openssh)](https://galaxy.ansible.com/ui/standalone/roles/ANXS/openssh/)
[![License](https://img.shields.io/github/license/ANXS/openssh)](https://github.com/ANXS/openssh/blob/master/LICENSE)

Ansible role for installing and configuring the OpenSSH client and server. Ships with hardened defaults (public-key only, no root login, modern key exchange and MAC algorithms) and generates ed25519 and ECDSA host keys on first run. Per-distribution overrides handle algorithm differences across OpenSSH versions.

## Requirements & Dependencies

* Ansible 2.12 or higher.
* Ubuntu 20.04+ or Debian 12+.

## Variables

SSH server and client configuration is managed by the semi free-form dicts, which allow you to set any OpenSSH variable. A default (per-OS) set is provided, and this maybe partially, or fully, overrriden.

* `openssh_server_settings` Server defaults that override `sshd_config` options.
* `openssh_client_settings` Client defaults that override `ssh_config` options.
* `openssh_hostkey_types` (defaults to `["ecdsa", "ed25519"]`) list of host key types to generate.
* `openssh_enable_config_includes` (defaults to `false`) emit an `Include` for `/etc/ssh/sshd_config.d/*.conf`. See [Drop-in configuration](#drop-in-configuration) before enabling it.
* `openssh_config_includes_path` (defaults to `/etc/ssh/sshd_config.d/*.conf`) glob used by that `Include`.

## Drop-in configuration

By default this role writes an `sshd_config` with **no `Include` directive**, so
files under `/etc/ssh/sshd_config.d/` are not read. Anything another role drops
there is inert: the file is present, has the content you expect, passes
`sshd -t`, and changes nothing. Setting `openssh_enable_config_includes: true`
emits the `Include` and makes those files live.

Enabling the `Include` activates every file already in that directory
on the target host, not just the one you happen to care
about. `sshd_config(5)`: "for each keyword, the first obtained value
will be used". The role therefore renders the `Include` as the
**first** directive in the file. An `Include` appended below the
role's global settings is outvoted by every keyword the role sets.

OpenSSH ANDs the `sshd_config` `PermitListen` list with the
`permitlisten=` list in `authorized_keys` (`check_rfwd_permission()`
in `channels.c`), so a `Match User` block that names one forwarded
port will refuse every other port that user forwards the moment the
`Include` goes live. Reverse tunnels a potential casualty, and the
symptom looks like a client fault rather than a config change. Check
any `Match` blocks in `sshd_config.d/` against what those users
actually forward.

## Config validation and reloads

Both config tasks validate the candidate file before it is installed, so a bad
value fails the play instead of breaking the host:

* `sshd_config` is checked with `/usr/sbin/sshd -t -f %s`. Without this, an
  unparseable config is written and the service is signalled, and on a host
  reached only over ssh that is the host.
* `ssh_config` is checked with `/usr/bin/ssh -G -F %s <placeholder>`. There is
  no daemon to notify for the client config, but an unparseable `ssh_config`
  breaks every outbound `ssh`, `scp` and `rsync` on the host, Ansible's own
  connections included. `ssh -G` only parses and prints; `-F` makes it read
  the candidate file alone, and no network traffic is generated.

`sshd -t` is not a pure parser: it refuses to run without a loadable host key
or the privilege separation directory. Host keys are therefore generated, and
`/run/sshd` created, before either config is templated.

A config change notifies **`Reload ssh`**, not a restart. On Debian and Ubuntu
`ssh.service` runs `/usr/sbin/sshd -t` in both `ExecStartPre` and `ExecReload`.
A restart stops sshd first, so a config it will not accept leaves the daemon
down; a reload runs the same check while sshd is still serving, and a bad
config aborts the reload with the previous config still live. Reload also keeps
established sessions, so a converge does not disconnect the operator running
it. Directives read only at startup -- `Port`, `ListenAddress`,
`AddressFamily` -- are not picked up by a reload; a `Restart ssh` handler is
still defined for those, and nothing in the role notifies it.

Notable server defaults out of the box:

* `PermitRootLogin: "no"`, `PasswordAuthentication: "no"`, `PubkeyAuthentication: "yes"`
* Only SHA-2 and ETM MACs (no hmac-md5, no hmac-sha1)
* KexAlgorithms limited to curve25519 and DH group16/18
* Certificate-aware HostKeyAlgorithms with ed25519 preferred

## Testing

Tests use [Molecule](https://github.com/ansible/molecule) with Docker
and [Testinfra](https://testinfra.readthedocs.io/). Run the full suite
with `make test`, or target a specific platform (e.g. `make
test-ubuntu2404`).

The test suite verifies package installation, config file permissions,
absence of deprecated SSHv1-era options, modern security settings,
rejection of weak MACs, host key generation, and `sshd -t` config
validation. Tests run across Ubuntu 20.04, 22.04, 24.04, and Debian
12, 13.

Drop-in behaviour is checked by asking sshd what it resolved rather than by
reading files, because the inert-drop-in defect is invisible to a file-content
assertion by construction -- the drop-in is correct either way, it just is not
read. The scenario writes a probe drop-in with a `Match User` block, then
asserts that `sshd -T -C user=...` does **not** reflect it with the role's
defaults, and does reflect it once the `Include` is enabled. The connection
spec passed to `-C` is complete (`user`, `host`, `addr`): sshd only evaluates
`Match` blocks for a complete spec, so an incomplete one silently reports
global values and would make the test pass for the wrong reason. The converge
also asserts that the `Include` is rendered first rather than merely present,
that `validate:` refuses a deliberately broken config without writing it or
notifying the handler, and that `ExecReload` validates before signalling.

## Note on AI Usage

This project has been developed with AI assistance. Contributions
making use of AI generated content are welcome, however they _must_ be
human reviewed prior to submission as pull requests, or issues. All
contributors must be able to fully explain and defend any AI generated
code, documentation, issues, or tests they submit. Contributions
making use of AI must have this explicitly declared in the pull
request or issue. This also applies to utilization of AI for reviewing
of pull requests.

## Feedback, bug-reports, requests, ...

Are all [welcome](https://github.com/ANXS/openssh/issues)!
