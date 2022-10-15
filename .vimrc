let data_dir = has('nvim') ? stdpath('data') . '/site' : '~/.vim'
if empty(glob(data_dir . '/autoload/plug.vim'))
  silent execute '!curl -fLo '.data_dir.'/autoload/plug.vim --create-dirs  https://raw.githubusercontent.com/junegunn/vim-plug/master/plug.vim'
  autocmd VimEnter * PlugInstall --sync | source $MYVIMRC
endif
" plugins using vim-pugin
call plug#begin()
" plug for coc.nvim
Plug 'neoclide/coc.nvim', {'branch': 'release'}
" end of plugin
call plug#end()

" coc-snippet: Make <tab> used for trigger completion, completion confirm, snippet expand and jump like VSCode.
inoremap <silent><expr> <TAB>
      \ coc#pum#visible() ? coc#_select_confirm() :
      \ coc#expandableOrJumpable() ? "\<C-r>=coc#rpc#request('doKeymap', ['snippets-expand-jump',''])\<CR>" :
      \ CheckBackSpace() ? "\<TAB>" :
      \ coc#refresh()

function! CheckBackSpace() abort
  let col = col('.') - 1
  return !col || getline('.')[col - 1]  =~# '\s'
endfunction

let g:coc_snippet_next = '<tab>'

" prettier configuration command
" command! -nargs=0 Prettier :call CocAction('runCommand', 'prettier.formatFile')
" command! -nargs=0 Prettier :CocCommand prettier.forceFormatDocument

" To enable file type detection
" filetype on
" augroup JavascriptTabSettings
" 	autocmd FileType javascript source /home/vagrant/.vim/custom/javascript-settings.vim
" 	autocmd FileType typescript source /home/vagrant/.vim/custom/javascript-settings.vim
" augroup END

" number set
set number

" color scheme
colorscheme pablo
