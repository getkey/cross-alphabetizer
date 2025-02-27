#!/usr/bin/env python3

import fontforge
import sys

def rename(font, new_font_name):
    font.fontname = new_font_name.replace(' ', '')
    font.familyname = new_font_name
    font.fullname = new_font_name

def swap(font, char_map):
    for glyph in font.glyphs():
        if glyph.unicode == -1:
            continue

        char = chr(glyph.unicode)
        if char in char_map:
            glyph.unicode = ord(char_map[char])

def ligate(font, ligature_map, simple_map):
    font.addLookup("liga","gsub_ligature",(),(("liga", (("latn", ("dflt")), ("grek", ("dflt")))),))
    font.addLookupSubtable("liga","liga1")

    for ligature, key in ligature_map.items():
        ligature_chars = []
        for char in ligature:
            char = simple_map.get(char, char)
            char = font[ord(char)].glyphname
            ligature_chars.append(char)
        ligature_tuple = tuple(ligature_chars)

        glyph = font[ord(key)]
        glyph.addPosSub("liga1", ligature_tuple)

def decompose(font, ligature_map):
    font.addLookup("decomp","gsub_multiple",(),(("ccmp", (("latn", ("dflt")), ("grek", ("dflt")))),))
    font.addLookupSubtable("decomp","decomp1")

    for ligature, key in ligature_map.items():
        ligature_chars = []
        for char in ligature:
            char = font[ord(char)].glyphname
            ligature_chars.append(char)
        ligature_tuple = tuple(ligature_chars)

        glyph = font[ord(key)]
        glyph.addPosSub("decomp1", ligature_tuple)

def gen_1_to_1_mappings(file):
    char_map = {}
    file.seek(0)
    for line in file:
        key, value = line.strip().split('\t')

        # exclude ligatures
        if len(key) > 1 or len(value) > 1:
            continue

        char_map[key] = value
        char_map[value] = key

    return char_map

def gen_ligature_mappings(file):
    char_map = {}
    file.seek(0)
    for line in file:
        key, value = line.strip().split('\t')


        print(key, value)

        if len(key) > 1 and len(value) == 1:
            char_map[key] = value

        if len(value) > 1 and len(key) == 1:
            char_map[value] = key

    return char_map

if __name__ == "__main__":
    if len(sys.argv) != 5:
        print("Usage: fontforge -script test.py <input.sfd> <output.otf> <new_font_name> <transcription_map.tsv>")
        sys.exit(1)

    output_otf = sys.argv[2]

    with open(sys.argv[4], 'r', encoding='utf-8') as transcription_file:
        simple_mappings = gen_1_to_1_mappings(transcription_file)
        ligature_mappings = gen_ligature_mappings(transcription_file)

    font = fontforge.open(sys.argv[1])
    font.encoding = 'UnicodeBmp' # make sure the unicode is taken into account
    rename(font, sys.argv[3])
    swap(font, simple_mappings)
    ligate(font, ligature_mappings, simple_mappings)
    decompose(font, ligature_mappings)

    # font.save("test.sfd")
    font.generate(sys.argv[2])
    print(f"Font saved as {sys.argv[2]}")
