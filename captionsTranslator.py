# -*- coding: utf-8 -*-

import argparse
import srt
import pydeepl
import os
from shutil import copyfile
import sys
import fileinput

# Now this is where all the fun begins

def translate(inputFile, outputFile, languageFrom, languageTo):
	if inputFile == None:
		print("Input file not specified! Exiting...")
		sys.exit(2)
	if languageTo == None:
		print("Language not specified! Exiting...")
		sys.exit(2)

	if outputFile == None:
		outputFile = inputFile + languageTo + '.srt'

	file = open(inputFile, 'r').read()
	copyfile(inputFile, os.curdir + '/' + outputFile)
	translatedFile = open(outputFile, 'w')
	subs = list(srt.parse(file))
	for sub in subs:
		try:
			translationSentence = pydeepl.translate(sub.content, languageTo.upper(), languageFrom.upper())
			print(str(sub.index) + ' ' +translationSentence)
			for line in fileinput.input(outputFile, inplace=True):
				line.replace(sub.content,translationSentence)
		except IndexError:
			print("Error parsing data from deepl")
def main():
	# Parse Arguments
	parser = argparse.ArgumentParser(description='Python Program that translates a subtitle file using deepl')
	parser.add_argument('-i', '--input-file', action="store", help="takes the input file", metavar="FILE")
	parser.add_argument('-o', '--output-file', action="store", help="takes the output file", metavar="FILE")
	parser.add_argument('-lf', '--language-from', action="store", help="language to translate from", default="auto")
	parser.add_argument('-lt', '--language-to', action="store", help="language to translate to")
	args = parser.parse_args()
	translate(args.input_file, args.output_file, args.language_from, args.language_to)


main()
