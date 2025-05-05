set pagination off
set debuginfod enabled on
set history save on
set history filename ~/.gdb_history
set history size unlimited

add-auto-load-safe-path /home/dr/.pyenv/versions/3.10.4/bin/python3.10-gdb.py
add-auto-load-safe-path /home/dr/.pyenv/versions/2.7.18/bin/python2.7-gdb.py
