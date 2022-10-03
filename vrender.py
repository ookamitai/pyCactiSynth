# Project Name: pyCactiSynth
# Project Desc.: A fully UTAU-compatible editor/synthesizer
# File name: vrender.py
# Author: ookamitai, null
# Date: Sept. 24 2022

import os
import logging
# import re
import scipy
import crepe
import time
import contextlib
import pyworld as pw
from decorator import catch_exception
import soundfile as sf
import numpy as np
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'


class VRenderError(RuntimeError):
    def __init__(self, *args):
        self.args = args


class VRender:
    def __init__(self, size=10):
        # TODO: Some smart people should tell me how to use the localization tool and try to localize the raised errors.
        self.size = size
        logging.info("VRender initialized.")

    @catch_exception
    def get_pitch(self, audio_data, sr):
        """
            Perform pitch estimation on given audio data

            Parameters
            ----------
            audio_data : np.ndarray
                The audio samples.
            sr : int
                Sample rate of the audio samples. The audio will be resampled if
                the sample rate is not 16 kHz, which is expected by the model.

            Returns
            -------
            A 2-tuple consisting of:

                timestamp_list: np.array
                    The timestamps on which the pitch was estimated
                freq_list: np.array
                    The predicted pitch values in Hz
            """
        # We suppress this error because ZeroDivisionError will occur if the audio data is completely muted
        with contextlib.suppress(ZeroDivisionError):
            start = time.time()
            # Use crepe for f0 estimation
            timestamp, frequency, confidence, activation = crepe.predict(
                audio_data,
                sr,
                viterbi=True,
                step_size=self.size,
                model_capacity="full",
                verbose=1,
            )
            # Print analysis time to give users an impression of how bad their computers are
            logging.info(f"Analysis time: {round(time.time() - start, 2)}s. ")
            return timestamp, frequency

    @catch_exception
    def synth(self, audio_data, sr, timestamp, frequency, _target, ratio, gender):
        """
            Perform pitch modifications on given audio data

            Parameters
            ----------
            audio_data : np.ndarray [shape=(N,) or (N, C)]
                The audio samples.
            sr : int
                Sample rate of the audio samples. The audio will be resampled if
                the sample rate is not 16 kHz, which is expected by the model.

            timestamp : np.array
                The timestamp array returned by get_pitch() function

            frequency : np.array
                The frequency array returned by get_pitch() function

            _target : np.array
                The desired target pitch

            ratio : float
                The ratio of the desired audio length and original length

            gender : float
                Gender parameters


            Returns
            -------

                x : np.ndarray
                    Synthesized audio data

            """

        # I don't care about shadow variable names because changing them will confuse the crap out of me
        _sp = pw.cheaptrick(audio_data, frequency, timestamp, sr)
        _ap = pw.d4c(audio_data, frequency, timestamp, sr)

        # This part is reserved for additional signal processing, for example, GENDER parameters
        shift = gender if gender >= 1 else 1
        sp = np.zeros_like(_sp)
        for f in range(sp.shape[1]):
            sp[:, f] = _sp[:, int(f / shift)]
        ap = _ap
        return pw.synthesize(_target, sp, ap, sr, self.size * ratio)


# Add some driver code here
if __name__ == "__main__":
    VoiceRender = VRender(10)
    data, samples = sf.read("/Users/raykura/Desktop/_ああいあうえあ.wav")
    timestamp, frequency = VoiceRender.get_pitch(data, samples)
    data_mod = VoiceRender.synth(
        data, samples, timestamp, frequency, frequency*2, 1.2, 1.2
    )
    scipy.io.wavfile.write("/Users/raykura/Desktop/_ああいあうえあ2.wav", samples, data_mod)
