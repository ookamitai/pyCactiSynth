# Project Name: pyCactiSynth
# Project Desc.: A fully UTAU-compatible editor/synthesizer
# File name: passthrough.py
# Author: ookamitai, null
# Date: Oct.4 2022

import model
from pathlib import Path


# Driver code
if __name__ == "__main__":
    vb = model.VoiceBank(Path("/Users/raykura/Desktop/Voices/重音テト音声ライブラリー"))
    print(vb.find_entry("alias", "- あ", "A3", find_all=True))

