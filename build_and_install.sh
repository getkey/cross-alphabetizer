#!/bin/sh

fontfile=../liberation-fonts/src/LiberationSerif-Regular.sfd
swap_csv=./traditional_greek_romanization.tsv
outname=LiberationGreekLatinSwap

fontforge -script swap.py "$fontfile" ~/.local/share/fonts/"$outname".otf "$outname" "$swap_csv"
fc-cache -f
