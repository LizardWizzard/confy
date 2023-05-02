FROM fedora:37

RUN dnf update -y

COPY . .

RUN python3 setup.py install