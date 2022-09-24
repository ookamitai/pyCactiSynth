# Project Name: pyCactiSynth
# Project Desc.: A fully UTAU-compatible editor/synthesizer
# File name: vrender.py
# Author: ookamitai
# Date: Sept. 24 2022
import logging

import crepe
import time
import contextlib
import pyworld as pw
import soundfile as sf


class VRenderError(RuntimeError):
    def __init__(self, *args):
        self.args = args


class VRender:
    def __init__(self):
        # TODO: Some smart people should tell me how to use the localization tool and try to localize the raised errors.
        logging.info("VRender initialized.")

    @staticmethod
    def get_pitch(audio_data, sr):
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
            try:
                start = time.time()
                # Use crepe for f0 estimation
                timestamp, frequency, confidence, activation = crepe.predict(
                    audio_data,
                    sr,
                    viterbi=True,
                    step_size=10,
                    model_capacity="full",
                    verbose=1,
                )
                # Print analysis time to give users an impression of how bad their computers are
                logging.info(f"Analysis time: {time.time() - start}s. ")
                return timestamp, frequency
            except Exception as ex:
                try:
                    # Raise VRenderError and print it
                    raise VRenderError(ex.__class__.__name__) from ex
                except VRenderError as e:
                    logging.error(
                        f"An error occurred with VRender. Exception: {e.args[0]}"
                    )

    @staticmethod
    def synth(audio_data, sr, timestamp, frequency, target):
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

        target : np.array
            The desired target pitch

        Returns
        -------

            x : np.ndarray
                Synthesized audio data

        """

        # TODO: This is still WIP. Exception catching is required.
        # I don't care about shadow variable names because changing them will confuse the crap out of me
        _sp = pw.cheaptrick(audio_data, frequency, timestamp, sr)
        _ap = pw.d4c(audio_data, frequency, timestamp, sr)
        return pw.synthesize(target, _sp, _ap, sr, 10)


# Add some driver code here
if __name__ == "__main__":
    VoiceRender = VRender()
    data, samples = sf.read("/Users/raykura/Desktop/_ああいあうえあ.wav")
    timestamp, frequency = VoiceRender.get_pitch(data, samples)
    data_mod = VoiceRender.synth(data, samples, timestamp, frequency, frequency)