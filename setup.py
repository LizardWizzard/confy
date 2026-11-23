import argparse
import enum
import re
import subprocess
import sys
from pathlib import Path
import textwrap
import time

CONFIGS = Path(__file__).parent / "configs"
ZSH_HOME = Path("~/.zsh")
CLAUDE_HOME = Path("~/.claude")


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

    if settings.is_symlink():
        settings.unlink()
    elif settings.exists():
        stamp = time.strftime("%Y%m%d-%H%M%S")
        settings.rename(settings.with_name(f"settings.json.pre-confy-{stamp}"))

    link(CONFIGS / "claude-settings.json", Path("~/.claude/settings.json"))


def install(args):
    install_pre()

    install_zsh()

    install_py()

    install_rust()

    install_misc()

    install_gitconf()

    install_gdbconf()

    install_kubectl()

    install_vim()

    install_helix()

    install_vscode()

    install_claude()


def update():
    run("sudo dnf update -y")
    run("cargo install-update -a")
    run("rustup update")


class InstallStage(enum.Enum):
    ALL = "all"
    ZSH = "zsh"
    PY = "py"
    RUST = "rust"
    MISC = "misc"
    GITCONF = "gitconf"
    CLAUDE = "claude"


def main():
    parser = argparse.ArgumentParser("migrator")
    sub = parser.add_subparsers(title="commands", dest="subparser_name")

    install_parser = sub.add_parser(
        "install",
    )
    install_parser.add_argument("--stage", default="all", required=False)

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
