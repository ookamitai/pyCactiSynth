# Project Name: pyCactiSynth
# Project Desc.: A fully UTAU-compatible editor/synthesizer
# File name: passthrough.py
# Author: ookamitai, null
# Date: Oct.4 2022

import vrender
import parser
import model
from pathlib import Path


# Driver code
if __name__ == "__main__":
    vb = model.VoiceBank(Path("/Users/raykura/Desktop/Voices/噤音セロ連続音ver.1.0"))
    print(vb.file_count)
