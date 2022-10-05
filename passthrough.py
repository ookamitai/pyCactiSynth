# Project Name: pyCactiSynth
# Project Desc.: A fully UTAU-compatible editor/synthesizer
# File name: passthrough.py
# Author: ookamitai, null
# Date: Oct.4 2022

import vrender
import parser
import model

# Driver code
if __name__ == "__main__":
    oto_setting = model.OTOSetting("/Users/raykura/Desktop/Voices/噤音セロ連続音ver.1.0/d3/oto.ini")
    print(oto_setting.size)
    print(oto_setting.get_entry(1).to_string())
    oto_setting.remove_entry(1)
    print(oto_setting.get_entry(1).to_string())
    oto_setting.to_file("/Users/raykura/Desktop/new.ini")
