import argparse
import re
import subprocess
import sys
from pathlib import Path
import textwrap
import time
import tomllib

CONFIGS = Path(__file__).parent / "configs"
ZSH_HOME = Path("~/.zsh")
CLAUDE_HOME = Path("~/.claude")
CODEX_HOME = Path("~/.codex")

# Shared by both agents (telegram/desktop notifications, session memory limit).
# herdr-agent-state.sh is managed by herdr itself and stays out of the repo.
AGENT_HOOK_SCRIPTS = ["telegram-notify.sh", "desktop-notify.sh", "session-memlimit.sh"]

# model_providers.<name>.experimental_bearer_token in an existing codex
# config.toml is migrated into the keyring under (service, account).
CODEX_TOKEN_KEYRINGS = {
    "ZAI": ("zai", "codex"),
    "deepseek": ("aitunnel", "codex"),
}


def run(cmd: str):
    subprocess.check_call(cmd, shell=True, stdout=subprocess.PIPE)


def clone_to(repo: str, to: Path):
    repo_name = Path(repo).stem
    dest = to / repo_name
    run(f"git clone --depth=1 {repo} {dest}")


def curl_to(url: str, to: Path):
    file_name = Path(url).name
    dest = to / file_name
    run(f"curl {url} > {dest}")


def link(src: Path, dst: Path, sudo: bool = False):
    if sudo:
        run(f"sudo ln -s {src} {dst}")
    else:
        run(f"ln -s {src} {dst}")


def link_home(path: Path):
    dst = Path(f"~/{path.name}")
    link(path, dst)


def dnf_install(*args):
    pkgs = " ".join(args)
    run(f"sudo dnf install -y {pkgs}")


def install_pre():
    dnf_install(
        "which",
        "git",
        "'dnf-command(copr)'",
        "gcc",
        "libgit2-devel",
        "libcurl-devel",
        "libssh2-devel",
        "openssl-devel",
        "pkg-config",
        "ncurses-devel",
        "readline-devel",
        "lzma-sdk-devel",
        "tk-devel",
    )


def install_zsh():
    # Install zsh package
    dnf_install("zsh")

    # Link config file
    link_home(CONFIGS / ".zshrc")

    # set as default shell
    dnf_install("util-linux-user")
    run("which zsh")
    run("chsh -s $(which zsh)")

    # Create directory for plugins
    run(f"mkdir {ZSH_HOME}")

    # Install powerlevel10k
    clone_to("https://github.com/romkatv/powerlevel10k.git", ZSH_HOME)
    # Install powerlevel10k config
    link_home(CONFIGS / ".p10k.zsh")

    # Install syntax highlighting
    clone_to("https://github.com/zdharma/fast-syntax-highlighting.git", ZSH_HOME)

    # Install completions
    curl_to(
        "https://raw.githubusercontent.com/robbyrussell/oh-my-zsh/master/lib/completion.zsh",
        ZSH_HOME,
    )

    # Install autosuggestions
    clone_to("https://github.com/zsh-users/zsh-autosuggestions.git", ZSH_HOME)

    # Install history
    curl_to(
        "https://raw.githubusercontent.com/robbyrussell/oh-my-zsh/master/lib/history.zsh",
        ZSH_HOME,
    )

    # Install keybindings
    curl_to(
        "https://raw.githubusercontent.com/robbyrussell/oh-my-zsh/master/lib/key-bindings.zsh",
        ZSH_HOME,
    )


def install_py():
    # Install pyenv
    run("curl https://pyenv.run | bash")
    dnf_install("bzip2-devel", "sqlite-devel", "libffi-devel")

    # Install poetry
    run("curl -sSL https://install.python-poetry.org | python3 -")


def install_rust():
    # Install rust with rustup
    run("curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh -s -- -y")

    # Install tools
    tools = [
        "cargo-asm",
        "cargo-bloat",
        "cargo-nextest",
        "cargo-update",
        "flamegraph",
    ]
    for tool in tools:
        # Full path because shell config with PATH adjustments is not applied yet
        run(f"~/.cargo/bin/cargo install {tool}")


def install_misc():
    dnf_install(
        "exa",
        "fzf",
        "ripgrep",
        "dua-cli",
        "git-delta",
        "htop",
    )

    # Install Just
    dnf_install("just")
    run("just --completions zsh > ~/.zsh/just.zsh")

    dnf_install("vim")


def install_gitconf():
    link_home(CONFIGS / ".gitconfig")


def install_gdbconf():
    link_home(CONFIGS / ".gdbinit")


def install_vbox():
    return
    # Add repo
    script = textwrap.dedent(
        """
        cat <<EOF | sudo tee /etc/yum.repos.d/virtualbox.repo
        [virtualbox]
        name=Fedora $releasever - $basearch - VirtualBox
        baseurl=http://download.virtualbox.org/virtualbox/rpm/fedora/36/\$basearch
        enabled=1
        gpgcheck=1
        repo_gpgcheck=1
        gpgkey=https://www.virtualbox.org/download/oracle_vbox.asc
        EOF
    """
    )
    run(script)

    # Install package
    run("sudo dnf install VirtualBox-6.1")

    # To operate vbox without sudo
    run("sudo usermod -a -G vboxusers $USER")
    run("newgrp vboxusers")
    run("id $USER")


def install_vagrant():
    return
    run("dnf install vagrant")


def install_kubectl():
    script = textwrap.dedent(
        """
        cat <<EOF | sudo tee /etc/yum.repos.d/kubernetes.repo
        [kubernetes]
        name=Kubernetes
        baseurl=https://packages.cloud.google.com/yum/repos/kubernetes-el7-x86_64
        enabled=1
        gpgcheck=1
        repo_gpgcheck=1
        gpgkey=https://packages.cloud.google.com/yum/doc/yum-key.gpg https://packages.cloud.google.com/yum/doc/rpm-package-key.gpg
        EOF
    """
    )
    run(script)

    dnf_install("kubectl")


def install_vim():
    dnf_install("vim")

    link_home(CONFIGS / ".vimrc")


def install_helix():
    run("sudo dnf copr enable varlad/helix -y")
    dnf_install("helix")

    run("mkdir -p ~/.config/helix/")
    link(CONFIGS / "helix.toml", Path("~/.config/helix/config.toml"))
    # do the same for root
    # run("sudo mkdir -p /root/.config/helix/")
    # link(
    #     CONFIGS / "helix.toml", Path("/home/root/.config/helix/config.toml"), sudo=True
    # )


def install_vscode():
    run("sudo rpm --import https://packages.microsoft.com/keys/microsoft.asc")
    run("sudo sh -c 'echo -e \"[code]\nname=Visual Studio Code\nbaseurl=https://packages.microsoft.com/yumrepos/vscode\nenabled=1\ngpgcheck=1\ngpgkey=https://packages.microsoft.com/keys/microsoft.asc\" > /etc/yum.repos.d/vscode.repo'")
    run("dnf check-update")
    run("sudo dnf install code")

    lines = (CONFIGS / "vs-code-extensions.txt").read_text().splitlines()
    for line in lines:
        run(f"code --install-extension {line}")


def backup_and_link(src: Path, dst: Path):
    """Replace dst with a symlink to src, backing up a real file if present."""
    if dst.is_symlink():
        dst.unlink()
    elif dst.exists():
        stamp = time.strftime("%Y%m%d-%H%M%S")
        dst.rename(dst.with_name(f"{dst.name}.pre-confy-{stamp}"))
    link(src, dst)


def install_agent_hooks(hooks_dir: Path):
    hooks_dir = hooks_dir.expanduser()
    run(f"mkdir -p {hooks_dir}")
    for name in AGENT_HOOK_SCRIPTS:
        backup_and_link(CONFIGS / "agent-hooks" / name, hooks_dir / name)


def install_claude_skills(skills_dir: Path):
    # One directory per skill under configs/claude-skills/<name>/SKILL.md,
    # linked like the hook scripts.
    skills_dir = skills_dir.expanduser()
    run(f"mkdir -p {skills_dir}")
    for skill_dir in sorted((CONFIGS / "claude-skills").iterdir()):
        if (skill_dir / "SKILL.md").is_file():
            backup_and_link(skill_dir, skills_dir / skill_dir.name)


def save_claude_token(settings: Path):
    # The token lives in the Secret Service keyring (gnome-keyring on GNOME,
    # KWallet's Secret Service bridge on KDE). settings.json reaches it via
    # apiKeyHelper pointing at the lookup script this writes.
    script = (CLAUDE_HOME / "api-key.sh").expanduser()
    if script.exists():
        return

    token = None
    if settings.is_file():
        match = re.search(r'"ANTHROPIC_AUTH_TOKEN"\s*:\s*"([^"]+)"', settings.read_text())
        if match:
            token = match.group(1)
            assert re.fullmatch(r"[\w.-]+", token), f"unexpected token format: {token}"

    if token is None:
        sys.exit(
            f"{script} is missing. Store the token in the keyring, then create {script}:\n"
            '  printf %s "TOKEN" | secret-tool store --label="Z.ai Claude Code token"'
            " service zai account claude-code\n"
            f"  printf '#!/bin/sh\\nsecret-tool lookup service zai account claude-code\\n' > {script} && chmod 700 {script}"
        )

    run(
        f'secret-tool store --label="Z.ai Claude Code token" service zai account claude-code <<< "{token}"'
    )
    script.write_text(
        "#!/bin/sh\nsecret-tool lookup service zai account claude-code\n"
    )
    script.chmod(0o700)


def install_claude():
    settings = (CLAUDE_HOME / "settings.json").expanduser()
    save_claude_token(settings)

    backup_and_link(CONFIGS / "claude-settings.json", settings)
    install_agent_hooks(CLAUDE_HOME / "hooks")
    install_claude_skills(CLAUDE_HOME / "skills")


def save_codex_tokens(config: Path):
    # Migrate inline experimental_bearer_token values from an existing codex
    # config.toml into the Secret Service keyring; the synced config has codex
    # fetch them itself via [model_providers.<id>.auth] -> secret-tool lookup.
    if not config.is_file():
        return
    with config.open("rb") as f:
        try:
            data = tomllib.load(f)
        except tomllib.TOMLDecodeError:
            return
    for name, provider in data.get("model_providers", {}).items():
        entry = CODEX_TOKEN_KEYRINGS.get(name)
        token = provider.get("experimental_bearer_token")
        if entry is None or not token:
            continue
        service, account = entry
        assert re.fullmatch(r"[\w.-]+", token), f"unexpected token format for {name}"
        run(
            f'secret-tool store --label="codex {name} token" '
            f'service {service} account {account} <<< "{token}"'
        )


def check_codex_tokens():
    # A missing keyring entry is not fatal for codex itself: it starts and then
    # retries forever on "Reconnecting... waiting for network". Fail here with
    # the fix instead.
    missing = []
    for name, (service, account) in CODEX_TOKEN_KEYRINGS.items():
        found = subprocess.run(
            ["secret-tool", "lookup", "service", service, "account", account],
            capture_output=True,
            text=True,
        ).stdout
        if not found.strip():
            missing.append((name, service, account))
    if missing:
        lines = "\n".join(
            f'  printf %s "TOKEN" | secret-tool store --label="codex {name} token"'
            f" service {service} account {account}"
            for name, service, account in missing
        )
        sys.exit("No token in the keyring for: " + ", ".join(n for n, _, _ in missing) + "\n" + lines)


def install_codex():
    config = (CODEX_HOME / "config.toml").expanduser()
    save_codex_tokens(config)

    check_codex_tokens()

    backup_and_link(CONFIGS / "codex-config.toml", config)
    backup_and_link(CONFIGS / "codex-hooks.json", (CODEX_HOME / "hooks.json").expanduser())
    # Z.ai serves its own catalog (model_catalog_url in the provider). The
    # DeepSeek models come from a file, used by the `codex -p deepseek` layer.
    backup_and_link(CONFIGS / "codex-deepseek.config.toml", (CODEX_HOME / "deepseek.config.toml").expanduser())
    backup_and_link(CONFIGS / "codex-models-deepseek.json", (CODEX_HOME / "models-deepseek.json").expanduser())
    install_agent_hooks(CODEX_HOME / "hooks")


STAGES = {
    "all": [
        install_pre,
        install_zsh,
        install_py,
        install_rust,
        install_misc,
        install_gitconf,
        install_gdbconf,
        install_kubectl,
        install_vim,
        install_helix,
        install_vscode,
        install_claude,
        install_codex,
    ],
    "zsh": [install_zsh],
    "py": [install_py],
    "rust": [install_rust],
    "misc": [install_misc],
    "gitconf": [install_gitconf],
    "gdbconf": [install_gdbconf],
    "kubectl": [install_kubectl],
    "vim": [install_vim],
    "helix": [install_helix],
    "vscode": [install_vscode],
    "claude": [install_claude],
    "codex": [install_codex],
}


def install(args):
    handlers = STAGES.get(args.stage)
    if handlers is None:
        sys.exit(f"unknown stage: {args.stage} (known: {', '.join(STAGES)})")
    for handler in handlers:
        handler()


def update():
    run("sudo dnf update -y")
    run("cargo install-update -a")
    run("rustup update")


def main():
    parser = argparse.ArgumentParser("migrator")
    sub = parser.add_subparsers(title="commands", dest="subparser_name")

    install_parser = sub.add_parser(
        "install",
    )
    install_parser.add_argument(
        "--stage", default="all", required=False, choices=sorted(STAGES)
    )

    update_parser = sub.add_parser("update")

    args = parser.parse_args()

    handlers = {
        "install": install,
        "update": update,
    }

    handler = handlers.get(args.subparser_name)
    if handler:
        handler(args)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
