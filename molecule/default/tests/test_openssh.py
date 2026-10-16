"""Testinfra tests for anxs-openssh role."""

# Written by molecule/default/prepare.yml. Only asking sshd what it resolved
# can tell whether the drop-in is live; its content is identical either way.
PROBE_USER = "sshdprobe"
PROBE_SPEC = f"user={PROBE_USER},host=molecule.invalid,addr=127.0.0.1"
PROBE_LISTEN = "permitlisten 127.0.0.1:22999"

# Rendered by molecule/default/converge.yml with
# openssh_enable_config_includes=true. Kept off /etc/ssh/sshd_config so the
# converged state stays the role default.
CANDIDATE_CONFIG = "/var/tmp/molecule-sshd-config-includes-enabled"
INCLUDE_DIRECTIVE = "Include /etc/ssh/sshd_config.d/*.conf"

SSHD = "/usr/sbin/sshd"


def directives(content):
    """Config lines that sshd actually acts on, in file order."""
    return [line.strip() for line in content.splitlines()
            if line.strip() and not line.strip().startswith("#")]


def test_sshd_package_installed(host):
    """Verify openssh-server is installed."""
    assert host.package("openssh-server").is_installed


def test_ssh_client_package_installed(host):
    """Verify openssh-client is installed."""
    assert host.package("openssh-client").is_installed


def test_sshd_config_exists(host):
    """Verify sshd_config exists with correct permissions."""
    f = host.file("/etc/ssh/sshd_config")
    assert f.exists
    assert f.is_file
    assert f.user == "root"
    assert f.group == "root"
    assert f.mode == 0o644


def test_ssh_config_exists(host):
    """Verify ssh_config exists with correct permissions."""
    f = host.file("/etc/ssh/ssh_config")
    assert f.exists
    assert f.is_file
    assert f.user == "root"
    assert f.group == "root"
    assert f.mode == 0o644


def test_sshd_config_no_removed_options(host):
    """Verify sshd_config does not contain options removed in OpenSSH 7.6+."""
    f = host.file("/etc/ssh/sshd_config")
    content = f.content_string
    for option in ["Protocol ", "UsePrivilegeSeparation ",
                    "KeyRegenerationInterval ", "ServerKeyBits ",
                    "UseLogin "]:
        assert option not in content, f"Removed option '{option.strip()}' found in sshd_config"


def test_ssh_config_no_removed_options(host):
    """Verify ssh_config does not contain options removed in OpenSSH 7.6+."""
    f = host.file("/etc/ssh/ssh_config")
    content = f.content_string
    for option in ["Protocol ", "UsePrivilegedPort ", "RSAAuthentication "]:
        assert option not in content, f"Removed option '{option.strip()}' found in ssh_config"


def test_sshd_config_has_modern_settings(host):
    """Verify sshd_config contains expected modern settings."""
    f = host.file("/etc/ssh/sshd_config")
    content = f.content_string
    assert "PermitRootLogin no" in content
    assert "PubkeyAuthentication yes" in content
    assert "PasswordAuthentication no" in content
    assert "UsePAM yes" in content


def test_sshd_config_no_weak_macs(host):
    """Verify sshd_config does not use weak MACs."""
    f = host.file("/etc/ssh/sshd_config")
    content = f.content_string
    for weak_mac in ["hmac-md5", "hmac-sha1,"]:
        assert weak_mac not in content, f"Weak MAC '{weak_mac}' found in sshd_config"


def test_ssh_config_no_weak_macs(host):
    """Verify ssh_config does not use weak MACs."""
    f = host.file("/etc/ssh/ssh_config")
    content = f.content_string
    for weak_mac in ["hmac-md5", "hmac-sha1,"]:
        assert weak_mac not in content, f"Weak MAC '{weak_mac}' found in ssh_config"


def test_host_keys_exist(host):
    """Verify ed25519 and ecdsa host keys exist."""
    for keytype in ["ecdsa", "ed25519"]:
        keyfile = host.file(f"/etc/ssh/ssh_host_{keytype}_key")
        assert keyfile.exists, f"Host key {keytype} not found"
        assert keyfile.user == "root"


def test_sshd_config_valid(host):
    """Verify sshd can parse the config without errors."""
    result = host.run("sshd -t")
    assert result.rc == 0, f"sshd -t failed: {result.stderr}"


def test_ssh_config_valid(host):
    """Verify ssh(1) can parse the client config without errors.

    Mirrors the validate: on the "Configure OpenSSH Client" task. An
    unparseable ssh_config breaks every outbound ssh, scp and rsync on the
    host, Ansible's own included.
    """
    result = host.run("ssh -G -F /etc/ssh/ssh_config config-validation.invalid")
    assert result.rc == 0, f"ssh -G failed: {result.stderr}"


def test_ssh_service_running(host):
    """Verify the daemon survived the config change.

    The role notifies a reload rather than a restart, so this also pins that
    the reload did not leave sshd down.
    """
    assert host.service("ssh").is_running


def test_ssh_service_reload_is_validated(host):
    """Verify ExecReload validates the config before signalling sshd.

    This is the property that makes reload safer than restart here.
    """
    result = host.run("systemctl show ssh --property=ExecReload")
    assert result.rc == 0, f"systemctl show ssh failed: {result.stderr}"
    assert "sshd -t" in result.stdout, (
        "ssh.service ExecReload does not validate the config first; "
        f"reload is no safer than restart here: {result.stdout}"
    )


# --- drop-in support ------------------------------------------------------


def test_default_config_emits_no_include(host):
    """Verify the role does not enable drop-ins by default."""
    content = host.file("/etc/ssh/sshd_config").content_string
    includes = [d for d in directives(content) if d.lower().startswith("include ")]
    assert includes == [], (
        f"sshd_config enables drop-ins by default: {includes}. "
        "openssh_enable_config_includes must be opt-in."
    )


def test_default_config_leaves_dropins_inert(host):
    """Verify a drop-in has no effect with the role's defaults.

    With no Include, sshd never reads sshd_config.d/, so the probe's Match
    block must not appear in the resolved config.
    """
    result = host.run(f"{SSHD} -T -C {PROBE_SPEC}")
    assert result.rc == 0, f"sshd -T failed: {result.stderr}"
    assert PROBE_LISTEN not in result.stdout, (
        "The probe drop-in reached the daemon with the Include disabled"
    )
    assert "permittty yes" in result.stdout, (
        f"Expected the global PermitTTY to win: {result.stdout}"
    )


def test_include_is_the_first_directive_when_enabled(host):
    """Verify the Include is emitted first, not merely emitted.

    sshd uses the first obtained value for each keyword, so an Include below
    the global settings is outvoted by every keyword this role sets.
    """
    content = host.file(CANDIDATE_CONFIG).content_string
    found = directives(content)
    assert found, "candidate sshd_config has no directives"
    assert found[0] == INCLUDE_DIRECTIVE, (
        f"Include must be the first directive, got: {found[:3]}"
    )
    includes = [d for d in found if d.lower().startswith("include ")]
    assert len(includes) == 1, f"expected exactly one Include, got {includes}"


def test_dropin_reaches_resolved_config_when_enabled(host):
    """Verify sshd -T actually reflects the drop-in once the Include is on."""
    result = host.run(f"{SSHD} -T -f {CANDIDATE_CONFIG} -C {PROBE_SPEC}")
    assert result.rc == 0, f"sshd -T failed: {result.stderr}"
    assert PROBE_LISTEN in result.stdout, (
        "With the Include enabled, sshd still does not see the drop-in: "
        f"{result.stdout}"
    )
    assert "permittty no" in result.stdout, (
        f"Drop-in PermitTTY did not win: {result.stdout}"
    )
