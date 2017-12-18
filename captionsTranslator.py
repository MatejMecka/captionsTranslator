# -*- coding: utf-8 -*-
# Thanks to the people at Hacklab Kika and the people on stackoverflow that helped me fix some of the bugs I encountered during writing this.

import argparse
import pysrt # This is bad practice forgive me. But each has it's cases i'm using it.
import pydeepl
import os
import shutil
import sys
import time
from datetime import datetime

# Now this is where all the fun begins	

def translate(input, output, languagef, languaget):
	subs = pysrt.open(input)
	for index, sub in enumerate(subs):
		try:
			linetotranslate = subs[index].text 
			translated = pydeepl.translate(linetotranslate, languaget.upper(), languagef.upper())
			subs[index] = translated
			print(subs[index]) 
		except IndexError:
			print("Error parsing data from deepl.")	
	subs.save(output)

def handleTranslations(inp,out,laf,lat):
	subs = pysrt.open(inp)
	append_index = None
	remove_list = []                # List of unwanted indexes
	sub_index = subs[0].index       # Existing starting index

	for index, sub in enumerate(subs):
		if append_index is not None:
			subs[append_index].text += sub.text
			subs[append_index].end = sub.end
			remove_list.append(index)
		if sub.text[-1] not in '.?!':
			append_index = index
		else:
			append_index = None

	# Remove orphaned subs in reverse order        
	for index in remove_list[::-1]:     
		del subs[index]

	# Reindex remaining subs
	for index in range(len(subs)):
		subs[index].index = index + sub_index

	subs.save('correcthorsebatterystaple', encoding='utf-8')
	translate('correcthorsebatterystaple.srt', out, laf, lat)


def parsefiles(inputFile, outputFile, languageFrom, languageTo):
	if inputFile == None:
		print("Input file not specified! Exiting...")
		sys.exit(2)
	if languageTo == None:
		print("Language not specified! Exiting...")
		sys.exit(2)

	if outputFile == None:
		outputFile = inputFile + languageTo + '.srt'

	shutil.copyfile(inputFile, outputFile)
	shutil.copyfile(inputFile, 'correcthorsebatterystaple.srt') # So I don't overwrite the original file i'll create this temp one and then delete it. 
	# Due to a bug that files cannot be accessed I had to move everything to another function
	handleTranslations(inputFile, outputFile, languageFrom, languageTo)


def main():
	# Parse Arguments
	parser = argparse.ArgumentParser(description='Python Program that translates a subtitle file using deepl')
	parser.add_argument('-i', '--input-file', action="store", help="takes the input file", metavar="FILE")
	parser.add_argument('-o', '--output-file', action="store", help="takes the output file", metavar="FILE")
	parser.add_argument('-lf', '--language-from', action="store", help="language to translate from", default="auto")
	parser.add_argument('-lt', '--language-to', action="store", help="language to translate to")
	args = parser.parse_args()
	parsefiles(args.input_file, args.output_file, args.language_from, args.language_to)


main()
