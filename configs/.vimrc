set nocompatible

set encoding=UTF-8

let g:python_highlight_all = 1
syntax on

if empty(glob('~/.vim/autoload/plug.vim'))
  silent !curl -fLo ~/.vim/autoload/plug.vim --create-dirs
    \ https://raw.githubusercontent.com/junegunn/vim-plug/master/plug.vim
  autocmd VimEnter * PlugInstall --sync | source $MYVIMRC
endif

call plug#begin('~/.vim/plugged')

"nerd tree
Plug 'scrooloose/nerdtree', {'on': 'NERDTreeToggle' }
Plug 'Xuyuanp/nerdtree-git-plugin'

"toml syntax
Plug 'cespare/vim-toml'

"lsp autocomplete
Plug 'prabirshrestha/async.vim'
Plug 'prabirshrestha/vim-lsp'
Plug 'prabirshrestha/asyncomplete.vim'
Plug 'prabirshrestha/asyncomplete-lsp.vim'
Plug 'prabirshrestha/asyncomplete-buffer.vim'
Plug 'prabirshrestha/asyncomplete-file.vim'

"fzf
Plug 'junegunn/fzf', { 'dir': '~/.fzf', 'do': './install --all' }
Plug 'junegunn/fzf.vim'

"markdown /pandoc support
Plug 'vim-pandoc/vim-pandoc'
Plug 'vim-pandoc/vim-pandoc-syntax'

Plug 'airblade/vim-rooter'
Plug 'airblade/vim-gitgutter'

"Plug 'chriskempson/base16-vim'
Plug 'morhetz/gruvbox'
Plug 'vim-airline/vim-airline'
Plug 'vim-airline/vim-airline-themes'

Plug 'tpope/vim-commentary'

"extended python syntax highlighting but still incomplete :(
Plug 'vim-python/python-syntax'

call plug#end()


let NERDTreeShowHidden=1
let NERDTreeIgnore=['\.DS_Store$', '\.git$', '\.pyc$', '__pycache__', '\.clwb$', '\.idea$', '\.mypy_cache$', '\.pytest_cache$', '\.vscode$']

"https://github.com/preservim/nerdtree#how-can-i-map-a-specific-key-or-shortcut-to-open-nerdtree
map <C-n> :NERDTreeToggle<CR>
"https://github.com/preservim/nerdtree#how-can-i-open-nerdtree-automatically-when-vim-starts-up-on-opening-a-directory
autocmd StdinReadPre * let s:std_in=1
autocmd VimEnter * if argc() == 1 && isdirectory(argv()[0]) && !exists("s:std_in") | exe 'NERDTree' argv()[0] | wincmd p | ene | exe 'cd '.argv()[0] | endif
" TODO make shortcut
cnoreabbrev ntf NERDTreeFind


call asyncomplete#register_source(asyncomplete#sources#buffer#get_source_options({
    \ 'name': 'buffer',
    \ 'whitelist': ['*'],
    \ 'completor': function('asyncomplete#sources#buffer#completor'),
    \ 'config': {
    \    'max_buffer_size': 5000000,
    \  },
    \ }))

au User asyncomplete_setup call asyncomplete#register_source(asyncomplete#sources#file#get_source_options({
    \ 'name': 'file',
    \ 'whitelist': ['*'],
    \ 'priority': 10,
    \ 'completor': function('asyncomplete#sources#file#completor')
    \ }))

"python language serrver
if executable('pyls')
    " pip install python-language-server TODO options about black etc.
    au User lsp_setup call lsp#register_server({
        \ 'name': 'pyls',
        \ 'cmd': {server_info->['ide_pyls']},
        \ 'whitelist': ['python'],
        \ })
endif

"rust analyzer
if executable('ra_lsp_server')
    " pip install python-language-server TODO options about black etc.
    au User lsp_setup call lsp#register_server({
        \ 'name': 'rust-analyzer',
        \ 'cmd': {server_info->['ra_lsp_server']},
        \ 'whitelist': ['rust'],
        \ })
endif


"https://github.com/prabirshrestha/asyncomplete.vim
"inoremap <expr> <Tab>   pumvisible() ? "\<C-n>" : "\<Tab>"
"inoremap <expr> <S-Tab> pumvisible() ? "\<C-p>" : "\<S-Tab>"
"inoremap <expr> <cr>    pumvisible() ? "\<C-y>" : "\<cr>"

"close autocompletition window when completition is done
autocmd! CompleteDone * if pumvisible() == 0 | pclose | endif

cnoreabbrev fmt LspDocumentFormat
cnoreabbrev dia LspDocumentDiagnostics
cnoreabbrev def LspDefinition
cnoreabbrev defp LspPeekDefinition
cnoreabbrev ref LspReferences

let g:lsp_diagnostics_echo_cursor = 1 " enable echo under cursor when in normal mode
let g:lsp_highlight_references_enabled = 1
"highlight lspReference ctermfg=red guifg=red ctermbg=red guibg=red! is not
"working, googleit

cnoreabbrev ghl GitGutterLineHighlightsToggle
autocmd BufWritePost * GitGutter

let g:airline#extensions#tabline#enabled = 1

"fzf tweaks/bat preview
" --column: Show column number
" --line-number: Show line number
" --no-heading: Do not show file headings in results
" --fixed-strings: Search term as a literal string
" --ignore-case: Case insensitive search
" --no-ignore: Do not respect .gitignore, etc...
" --hidden: Search hidden files and folders
" --follow: Follow symlinks
" --glob: Additional conditions for search (in this case ignore everything in the .git/ folder)
" --color: Search color options
command! -bang -nargs=* Find call fzf#vim#grep('rg --column --line-number --no-heading --fixed-strings --ignore-case --no-ignore --hidden --follow --glob "!.git/*" --color "always" '.shellescape(<q-args>), 1, <bang>0)
let $FZF_DEFAULT_OPTS = "--ansi --preview-window 'right:60%' --preview 'bat_wrap {}'"


"splits navigation using ctrl h j k l
nnoremap <C-J> <C-W><C-J>
nnoremap <C-K> <C-W><C-K>
nnoremap <C-L> <C-W><C-L>
nnoremap <C-H> <C-W><C-H>

""https://vi.stackexchange.com/questions/84/how-can-i-copy-text-to-the-system-clipboard-from-vim
"let clipboard='unnamedplus'

"vnoremap <C-c> "*y
" copy and paste
vmap <C-c> "+yi
vmap <C-x> "+c
vmap <C-v> c<ESC>"+p
imap <C-v> <ESC>"+pa

"split open direction
set splitbelow
set splitright

set nu rnu

"make delete work on mac in insert mode
set backspace=indent,eol,start

set langmap=ФИСВУАПРШОЛДЬТЩЗЙКЫЕГМЦЧНЯ;ABCDEFGHIJKLMNOPQRSTUVWXYZ,фисвуапршолдьтщзйкыегмцчня;abcdefghijklmnopqrstuvwxyz

set tabstop=4
set shiftwidth=4
set showcmd
set smartindent
set noswapfile
set ruler

au BufNewFile,BufRead *.js, *.html, *.css, *.c, *.sh
    \ set tabstop=2
    \ set softtabstop=2
    \ set shiftwidth=2

set mouse=a
set expandtab
set hlsearch

"https://www.youtube.com/watch?v=XA2WjJbmmoM
set path+=**
set wildmenu
set completeopt=longest,menu
set wildmode=list:longest,list:full
set complete=.,t

set termguicolors
"let base16colorspace=256
"base16-ashes
"colorscheme base16-atlas
let g:gruvbox_contrast_dark="hard"
let g:gruvbox_invert_tabline=1
let g:airline_theme='gruvbox'
colorscheme gruvbox
set bg=dark

"colorscheme base16-tomorrow-night
"colorscheme base16-woodland
"TODO make shortcut to reset search highlight
"TODO bash autocomplete


let mapleader=","
map <leader>r :NERDTreeFind<cr>

"let g:lsp_log_verbose = 1
"let g:lsp_log_file = expand('~/vim-lsp.log')
let g:rooter_patterns = ['Cargo.toml', '.git/']

nnoremap  <silent>   <tab>  :if &modifiable && !&readonly && &modified <CR> :write<CR> :endif<CR>:bnext<CR>
nnoremap  <silent> <s-tab>  :if &modifiable && !&readonly && &modified <CR> :write<CR> :endif<CR>:bprevious<CR>
