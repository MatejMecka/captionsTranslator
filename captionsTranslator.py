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
import asyncio

# Now this is where all the fun begins	

async def puppeteer(elements, to_lang, from_lang):
	from deepl_scraper_pp.deepl_tr import deepl_tr
	coros = [await deepl_tr(elem['text'], to_lang=to_lang, from_lang=from_lang) for elem in elements ]
	return coros

def translate(input, output, languagef, languaget, api_key):
	"""
	Translate each subtitle block
	"""

	if api_key:
		print("Using Deepl's API. Should be faster.")
		from deep_translator import DeepL
	else:
		print('Scraping Deepl, this may take some time....')
		loop = asyncio.get_event_loop()

	subs = pysrt.open(input)
	elements = []
	elements_translated = []
	for index, sub in enumerate(subs):
		entry = {'index': sub.index, 'start_time': sub.start, 'end_time': sub.end, 'text': sub.text}
		elements.append(entry)
		elements_translated.append(entry)

	counter = 20
	second_counter = 0
	while elements != []:
		try:
			if not api_key:
				translatedSentences = loop.run_until_complete(asyncio.gather(puppeteer(elements[:counter], languaget, languagef), return_exceptions=True))
				translatedSentences = translatedSentences[0]
			else:
				translatedSentences = Deepl(api_key, source=languagef, target=languaget).translate_batch(elements[:counter])
		except:
			translatedSentences = [None for elem in range(counter)]

		for sentence in translatedSentences:
			try:
				elements_translated[second_counter]['text'] = sentence
				print(f"{elements_translated[second_counter]['index']}. -> {elements_translated[second_counter]['text']}")
				second_counter+=1
			except:
				pass

		del elements[:counter]

	print(elements)
	with open(output, 'w') as fileresp: # Use w mode instead
		for element in elements_translated:
			try:
				print(f"{element['start_time']}  {element['text']}")
				fileresp.write(f"{element['index']}\n{element['start_time']} --> {element['end_time']}\n{element['text']}\n\n")
			except:
				pass

		fileresp.close()

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
	translate(inputFile, outputFile, languageFrom, languageTo, api_key)

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

if __name__ == '__main__':
	main()
