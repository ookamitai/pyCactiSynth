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
    print(vb.find_entry("alias", "- k"))
    o = model.OTOSetting().from_file(Path("/Users/raykura/Desktop/new.ini"))
    print(o.size)
    o.append_entry(1, model.OTOEntry().from_string("1=2,3,4,5,6,7"))
    print(o.json(indent=4, ensure_ascii=0))
