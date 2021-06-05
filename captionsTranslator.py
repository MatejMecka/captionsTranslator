# -*- coding: utf-8 -*-
# Thanks to the people at Hacklab Kika and the people on stackoverflow that helped me fix some of the bugs I encountered during writing this.

import argparse
import pysrt 
import os
import shutil
import sys
import time
from datetime import datetime
import tempfile

# Now this is where all the fun begins	

def translate(input, output, languagef, languaget, api_key):

	if not api_key:
		from deepl_scraper.translator import DeepLEngine
		translator = DeepLEngine(source_language=languagef, target_language=languaget)
	else:
		from deep_translator import DeepL

	subs = pysrt.open(input)
	fileresp = open(output, 'w') # Use w mode instead
	for index, sub in enumerate(subs):
		linefromsub = subs[index].text
		try:
			if not api_key:
				translationSentence = translator.translate(linefromsub)
			else:
				translationSentence = DeepL(api_key=api_key, source=languagef.lower(), target=languaget.lower()).translate(linefromsub)
			print(str(sub.start) + ' ' + translationSentence)
			fileresp.write("{}\n{} --> {}\n{}\n\n".format(sub.index,str(sub.start), str(sub.end), translationSentence))
		except IndexError as e:
			toSend = linefromsub.split('\n')
			stringToWrite = ""
			for part in toSend:
				if not api_key:
					finString = stringToWrite + translator.translate(linefromsub)
				else:
					finString = stringToWrite + DeepL(api_key=api_key, source=languagef.lower(), target=languaget.lower()).translate(linefromsub)
			fileresp.write("{}\n{} --> {}\n{}\n\n".format(sub.index,str(sub.start), str(sub.end), translationSentence))

	os.remove(input)

def handleTranslations(inp,out,laf,lat, api_key):
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

	subs.save(inp, encoding='utf-8')
	translate(inp, out, laf, lat, api_key)


def parsefiles(inputFile, outputFile, languageFrom, languageTo, api_key):
	if inputFile == None:
		print("Input file not specified! Exiting...")
		sys.exit(2)
	if languageTo == None:
		print("Language not specified! Exiting...")
		sys.exit(2)

	if outputFile == None:
		outputFile = inputFile + languageTo + '.srt'


	tempFile = tempfile.NamedTemporaryFile(suffix='.srt',delete=False)
	shutil.copyfile(inputFile,tempFile.name)
	shutil.copyfile(inputFile, outputFile) 
	# Due to a bug that files cannot be accessed I had to move everything to another function
	handleTranslations(tempFile.name, outputFile, languageFrom, languageTo, api_key)

def main():
	# Parse Arguments
	parser = argparse.ArgumentParser(description='Python Program that translates a subtitle file using deepl')
	parser.add_argument('-i', '--input-file', action="store", help="takes the input file", metavar="FILE")
	parser.add_argument('-o', '--output-file', action="store", help="takes the output file", metavar="FILE")
	parser.add_argument('-lf', '--language-from', action="store", help="language to translate from", default="auto")
	parser.add_argument('-lt', '--language-to', action="store", help="language to translate to")
	parser.add_argument('-a', '--api-key', action="store", help="Deepl API Key - Optional")
	args = parser.parse_args()
	parsefiles(args.input_file, args.output_file, args.language_from, args.language_to, args.api_key)


main()
