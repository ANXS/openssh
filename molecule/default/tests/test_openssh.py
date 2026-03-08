"""Testinfra tests for anxs-openssh role."""


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
