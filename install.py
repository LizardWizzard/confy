import argparse
import subprocess
from pathlib import Path
import textwrap

CONFIGS = Path(__file__) / "configs"


def run(cmd: str):
    subprocess.check_call(cmd, shell=True)


def clone_to(repo: str, to: Path):
    repo_name = Path(repo).stem
    dest = to / repo_name
    run(f"git clone --depth=1 {repo} {dest}")


def wget_to(url: str, to: Path):
    file_name = Path(url).name
    dest = to / file_name
    run(f"wget {url} {dest}")


def link(src: Path, dst: Path):
    run(f"ln -s {src} {dst}")


def link_home(file: Path):
    dst = Path(f"~/{file.name}")
    link(file, dst)


def install_zsh():
    # Install zsh package
    run("sudo dnf install zsh")

    # Link config file
    link_home(CONFIGS / ".zshrc")

    # set as default shell
    run("sudo dnf install util-linux-user")
    run("chsh -s $(which zsh)")

    # Create directory for plugins
    run("mkdir ~/.zsh")

    # Install powerlevel10k
    clone_to("https://github.com/romkatv/powerlevel10k.git", "~/.zsh")
    # Install powerlevel10k config
    link_home(CONFIGS / ".p10k.zsh")

    # Install syntax highlighting
    clone_to("https://github.com:zdharma/fast-syntax-highlighting.git", "~/.zsh")

    # Install completions
    wget_to(
        "https://raw.githubusercontent.com/robbyrussell/oh-my-zsh/master/lib/completion.zsh",
        "~/.zsh",
    )

    # Install autosuggestions
    clone_to("https://github.com/zsh-users/zsh-autosuggestions.git", "~/.zsh")

    # Install history
    wget_to(
        "https://raw.githubusercontent.com/robbyrussell/oh-my-zsh/master/lib/history.zsh",
        "~/.zsh",
    )

    # Install keybindings
    wget_to(
        "https://raw.githubusercontent.com/robbyrussell/oh-my-zsh/master/lib/key-bindings.zsh",
        "~/.zsh",
    )


def install_py():
    # Install pyenv
    run("curl https://pyenv.run | bash")
    run("sudo dnf install bzip2-devel sqlite-devel libffi-devel")

    # Install poetry
    run("curl -sSL https://install.python-poetry.org | python3 -")


def install_rust():
    run("curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh")


def install_misc():
    tools = " ".join(["exa", "fzf", "ripgrep", "dua-cli", "git-delta"])
    run(f"sudo dnf install {tools}")

    # Install Just
    run("sudo dnf install just")
    run("just --completions zsh > ~/.zsh/just.zsh")


def install_gitconfig():
    link_home(CONFIGS / ".gitconfig")


def install_gdbconfig():
    link_home(CONFIGS / ".gdbinit")


def install_vbox():
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

    run("dnf install kubectl")


def install():
    install_zsh()

    install_py()

    install_rust()

    install_misc()

    install_gitconfig()

    install_gdbconfig()

    install_vbox()

    install_vagrant()

    install_kubectl()


# TODO helix
# TODO rust, rust tools (look at ~/.cargo/bin)


def update():
    pass


def main():
    parser = argparse.ArgumentParser("migrator")
    sub = parser.add_subparsers(title="commands", dest="subparser_name")

    install_parser = sub.add_parser(
        "install",
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
