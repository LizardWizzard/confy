docker build --progress plain -t confy .
docker run -e TERM -e COLORTERM -e LC_ALL=C.UTF-8 -it confy /bin/zsh 