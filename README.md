## [ANXS](https://github.com/ANXS) - openssh

[![CI Status](https://img.shields.io/github/actions/workflow/status/anxs/openssh/ci.yml)](https://github.com/ANXS/openssh/actions/workflows/ci.yml)
[![Maintenance](https://img.shields.io/maintenance/yes/2026.svg)](https://github.com/ANXS/openssh)
[![Ansible Role](https://img.shields.io/ansible/role/d/anxs/openssh)](https://galaxy.ansible.com/ui/standalone/roles/ANXS/openssh/)
[![License](https://img.shields.io/github/license/ANXS/openssh)](https://github.com/ANXS/openssh/blob/master/LICENSE)

Ansible role for installing and configuring the OpenSSH client and server. Ships with hardened defaults (public-key only, no root login, modern key exchange and MAC algorithms) and generates ed25519 and ECDSA host keys on first run. Per-distribution overrides handle algorithm differences across OpenSSH versions.

## Requirements & Dependencies

* Ansible 2.12 or higher.
* Ubuntu 20.04+ or Debian 11+.

## Variables

SSH server and client configuration is managed by the semi free-form dicts, which allow you to set any OpenSSH variable. A default (per-OS) set is provided, and this maybe partially, or fully, overrriden.

* `openssh_server_settings` Server defaults that override `sshd_config` options.
* `openssh_client_settings` Client defaults that override `ssh_config` options.
* `openssh_hostkey_types` (defaults to `["ecdsa", "ed25519"]`) list of host key types to generate.

Notable server defaults out of the box:

* `PermitRootLogin: "no"`, `PasswordAuthentication: "no"`, `PubkeyAuthentication: "yes"`
* Only SHA-2 and ETM MACs (no hmac-md5, no hmac-sha1)
* KexAlgorithms limited to curve25519 and DH group16/18
* Certificate-aware HostKeyAlgorithms with ed25519 preferred

## Testing

Tests use [Molecule](https://github.com/ansible/molecule) with Docker and [Testinfra](https://testinfra.readthedocs.io/). Run the full suite with `make test`, or target a specific platform (e.g. `make test-ubuntu2404`).

The test suite verifies package installation, config file permissions, absence of deprecated SSHv1-era options, modern security settings, rejection of weak MACs, host key generation, and `sshd -t` config validation. Tests run across Ubuntu 20.04, 22.04, 24.04, and Debian 11, 12.

## Note on AI Usage

This project has been developed with AI assistance. Contributions making use of AI generated content are welcome, however they _must_ be human reviewed prior to submission as pull requests, or issues. All contributors must be able to fully explain and defend any AI generated code, documentation, issues, or tests they submit. Contributions making use of AI must have this explicitly declared in the pull request or issue. This also applies to utilization of AI for reviewing of pull requests.

## Feedback, bug-reports, requests, ...

Are all [welcome](https://github.com/ANXS/openssh/issues)!
