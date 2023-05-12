## Desktop

### asusctl

Written in Rust!

Follow instructions https://asus-linux.org/wiki/fedora-guide/#fedora-36-setup

Set up keyboard RGB backlight:
```bash
asusctl led-mode breathe -c 4682B4 -C 008B8B -s low
```

### Install Chrome

Install RPM via Software

### Dash to dock:

```bash
sudo dnf install gnome-extensions-app gnome-shell-extension-dash-to-dock
```
Search for dash to dock in Extensions app, if it does not show up, restart (maybe log out is enough) and check after that.

### Telegram

Install flatpack from https://flathub.org/apps/details/org.telegram.desktop

Gnome software crashed when I tried it so installing from command line:
```bash
sudo flatpak remote-add --if-not-exists flathub https://flathub.org/repo/flathub.flatpakrepo
flatpak install flathub org.telegram.desktop
```

Instruction from https://www.linuxcapable.com/how-to-install-telegram-on-fedora-35/#Method_3_Install_Telegram_with_Flatpak

### Switch input source

For some stupid reason alt shift stopped working and I failed to set it as a shortcut through the GUI so:

```bash
gsettings set org.gnome.desktop.wm.keybindings switch-input-source "['<Shift>Alt_L']"
gsettings set org.gnome.desktop.wm.keybindings switch-input-source-backward "['<Alt>Shift_L']"
```

https://askubuntu.com/a/986629

### Fix dark theme for legacy apps

Some applications like vs code do not follow system theme.
So install Gnome Tweaks from Software.
Then go to Appearance -> Themes, Legacy Application -> Select Dark theme

ref https://github.com/microsoft/vscode/issues/146804#issuecomment-1123706437

## Development

Config files:
* `~/.zshrc`
* `~/.gitconfig`
* `~/.p10k.zsh`

### Rust

Via rustup https://rustup.rs/

### VS Code

Follow the instructions https://code.visualstudio.com/docs/setup/linux#_rhel-fedora-and-centos-based-distributions

#### Extensions

```bash
xargs -n1 code --install-extension <<EOF
42Crunch.vscode-openapi
alygin.vscode-tlaplus
bierner.markdown-mermaid
ChristianAlexander.flip
cschlosser.doxdocgen
eamodio.gitlens
faustinoaq.lex-flex-yacc-bison
GitHub.copilot
jeff-hykin.better-cpp-syntax
mechatroner.rainbow-csv
ms-azuretools.vscode-docker
ms-python.python
ms-python.vscode-pylance
ms-toolsai.jupyter
ms-toolsai.jupyter-keymap
ms-toolsai.jupyter-renderers
ms-vscode-remote.remote-containers
ms-vscode-remote.remote-ssh
ms-vscode-remote.remote-ssh-edit
ms-vscode-remote.remote-wsl
ms-vscode.cmake-tools
ms-vscode.cpptools
ms-vscode.cpptools-extension-pack
ms-vscode.cpptools-themes
redhat.vscode-yaml
rust-lang.rust-analyzer
serayuzgur.crates
skellock.just
tamasfe.even-better-toml
tcwalther.cython
tomphilbin.gruvbox-themes
twxs.cmake
usernamehw.errorlens
viper-admin.prusti-assistant
yzhang.markdown-all-in-one
zxh404.vscode-proto3
EOF
```

### Tools

```bash
sudo dnf install \
    htop \

```

### Fix for tabs opening in the same directory

In Profile settings of Gnome terminal enable the "Run command as a login shell"

https://unix.stackexchange.com/a/251023
stopped working after reboot and does not work again

### ZSH

Some of the tips (mostly some plugins and oh-my-zsh parts reusing taken from https://web.archive.org/web/20211103173717/https://tjay.dev/howto-my-terminal-shell-setup-hyper-js-zsh-starship/)

#### Install ZSH
```bash
sudo dnf install zsh
```
#### Set ZSH as default

Set zsh as user default shell via chsh

```bash
sudo dnf install util-linux-user
chsh -s $(which zsh)
```

TODO review options from here, consider vim mode, proper history, etc
https://unix.stackexchange.com/questions/265957/zsh-histfile-still-read-from-zsh-history

#### Create directory for plugins

```bash
mkdir ~/.zsh
```

#### Install fontawesome

```bash
sudo dnf install fontawesome-fonts
```

#### Prompt customization

Install powerlevel10k 
TODO enable more segments (see https://github.com/romkatv/powerlevel10k/blob/master/README.md#batteries-included)
```bash
cd ~/.zsh && git clone --depth=1 https://github.com/romkatv/powerlevel10k.git
```

#### Install syntax highlighting
```bash
cd ~/.zsh && git clone --depth=1 https://github.com:zdharma/fast-syntax-highlighting.git
```

#### Install completions
This is extracted from oh my zsh
```bash
cd ~/.zsh && wget https://raw.githubusercontent.com/robbyrussell/oh-my-zsh/master/lib/completion.zsh
```

#### Install autosuggestions
```bash
cd ~/.zsh && git clone --depth=1 https://github.com/zsh-users/zsh-autosuggestions.git
```

#### Install history
```bash
cd ~/.zsh && wget https://raw.githubusercontent.com/robbyrussell/oh-my-zsh/master/lib/history.zsh
```

#### Install keybindings

```bash
cd ~/.zsh && wget https://raw.githubusercontent.com/robbyrussell/oh-my-zsh/master/lib/key-bindings.zsh
```

#### TODO migrate old config, aliases etc

### Install pyenv

Use installer: https://github.com/pyenv/pyenv-installer
```bash
curl https://pyenv.run | bash
```
Extra libraries to properly build python:
```bash
sudo dnf install bzip2-devel sqlite-devel libffi-devel
```

### poetry

https://python-poetry.org/docs/master/#installing-with-the-official-installer

### exa+ls alias

```bash
sudo dnf install exa
```

### fzf

```bash
dnf install fzf
```
### ripgrep

```bash
dnf install ripgrep
```

### Just
TODO completions are

```bash
dnf install just
just --completions zsh > ~/.zsh/just.zsh
```
### GIT Do not show untracked files
Automatically select current branch when saying `git push`
```
git config --global push.default current
```
Do not show untracked files
```
git config --global status.showUntrackedFiles no
```


### Git Delta

```
dnf install git-delta
```

### Dua

```
dnf install dua-cli
```

### Virtualbox + vagrant

Link:
https://computingforgeeks.com/how-to-install-virtualbox-on-fedora-linux/

Steps:
* Add virtualbox repo.
```
cat <<EOF | sudo tee /etc/yum.repos.d/virtualbox.repo 
[virtualbox]
name=Fedora $releasever - $basearch - VirtualBox
baseurl=http://download.virtualbox.org/virtualbox/rpm/fedora/36/\$basearch
enabled=1
gpgcheck=1
repo_gpgcheck=1
gpgkey=https://www.virtualbox.org/download/oracle_vbox.asc
EOF
```
* Install virtualbox
```
sudo dnf install VirtualBox-6.1
```
* To operate virtualbox without sudo
```
sudo usermod -a -G vboxusers $USER
newgrp vboxusers
id $USER
```
* Install vagrant
```
dnf install vagrant
```

### Kubectl

```
cat <<EOF | sudo tee /etc/yum.repos.d/kubernetes.repo
[kubernetes]
name=Kubernetes
baseurl=https://packages.cloud.google.com/yum/repos/kubernetes-el7-x86_64
enabled=1
gpgcheck=1
repo_gpgcheck=1
gpgkey=https://packages.cloud.google.com/yum/doc/yum-key.gpg https://packages.cloud.google.com/yum/doc/rpm-package-key.gpg
EOF
dnf install kubectl
```

### Set up Github SSH key

### TODO (Slack)

### Neon

Packages:

```bash
dnf install \
  flex \
  bison \
  readline-devel \
  zlib-devel \
  openssl-devel \
  libseccomp-devel \
  perl \
  clang \
  cmake \
  etcd \
  openssl
```
Optional:

speedup build by using mold:

```
dnf install mold
```


### Virtual Desktops Only On Primary (KDE)

https://askubuntu.com/questions/102294/how-to-fix-one-virtual-desktop-to-my-second-monitor-with-kde/1399798#1399798

### Custom spectacle shortcut

https://forum.kde.org/viewtopic.php?t=140137