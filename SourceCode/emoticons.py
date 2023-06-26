'''
Created on   : DS Team June 27, 2023
@author      : Masterofray
Compiler     : Python 3.8

Version 0.01.27
'''

class EmoticonDetector:
    emoticons = {}

    def __init__(self, emoticon_file="data\\emoticons.txt"):
        from pathlib import Path
        content = Path(emoticon_file).read_text()
        positive = True
        for line in content.split("\n"):
            if "positive" in line.lower():
                positive = True
                continue
            elif "negative" in line.lower():
                positive = False
                continue

            self.emoticons[line] = positive

    def is_positive(self, emoticon):
        if emoticon in self.emoticons:
            return self.emoticons[emoticon]
        return False

    def is_emoticon(self, to_check):
        return to_check in self.emoticons
