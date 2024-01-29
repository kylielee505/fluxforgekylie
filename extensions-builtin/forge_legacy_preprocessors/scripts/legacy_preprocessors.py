# This is a python script to convert all old preprocessors to new format.
# However, the old preprocessors are not very memory effective
# and eventually we should move all old preprocessors to new format manually
# see also the forge_preprocessor_normalbae/scripts/preprocessor_normalbae for
# how to make better implementation of preprocessors.
# No newer preprocessors should be written in this legacy way.

# Never add new leagcy preprocessors please.
# The new forge_preprocessor_normalbae/scripts/preprocessor_normalbae
# is much more effective and maintainable


import contextlib

from annotator.util import HWC3
from modules_forge.ops import automatic_memory_management
from legacy_preprocessors.preprocessor_compiled import legacy_preprocessors
from modules_forge.supported_preprocessor import Preprocessor, PreprocessorParameter
from modules_forge.shared import add_supported_preprocessor


class LegacyPreprocessor(Preprocessor):
    def __init__(self, legacy_dict):
        super().__init__()
        self.name = legacy_dict['label']
        self.call_function = legacy_dict['call_function']
        self.unload_function = legacy_dict['unload_function']
        self.managed_model = legacy_dict['managed_model']
        self.do_not_need_model = legacy_dict['model_free']
        self.show_control_mode = not legacy_dict['no_control_mode']
        self.sorting_priority = legacy_dict['priority']
        self.tags = legacy_dict['tags']

        if legacy_dict['resolution'] is None:
            self.resolution = PreprocessorParameter(visible=False)
        else:
            legacy_dict['resolution']['label'] = 'Resolution'
            legacy_dict['resolution']['step'] = 8
            self.resolution = PreprocessorParameter(**legacy_dict['resolution'], visible=True)

        if legacy_dict['slider_1'] is None:
            self.slider_1 = PreprocessorParameter(visible=False)
        else:
            self.slider_1 = PreprocessorParameter(**legacy_dict['slider_1'], visible=True)

        if legacy_dict['slider_2'] is None:
            self.slider_2 = PreprocessorParameter(visible=False)
        else:
            self.slider_2 = PreprocessorParameter(**legacy_dict['slider_2'], visible=True)

        if legacy_dict['slider_3'] is None:
            self.slider_3 = PreprocessorParameter(visible=False)
        else:
            self.slider_3 = PreprocessorParameter(**legacy_dict['slider_3'], visible=True)

    def __call__(self, input_image, resolution, slider_1=None, slider_2=None, slider_3=None, **kwargs):
        # Legacy Preprocessors does not have slider 3
        del slider_3

        if self.unload_function is not None or self.managed_model is not None:
            context = automatic_memory_management()
        else:
            context = contextlib.nullcontext()

        with context:
            result, is_image = self.call_function(img=input_image, res=resolution, thr_a=slider_1, thr_b=slider_2, **kwargs)

        del is_image  # Not used anymore
        result = HWC3(result)

        if self.unload_function is not None:
            self.unload_function()

        return result


for k, v in legacy_preprocessors.items():
    p = LegacyPreprocessor(v)
    p.name = k
    add_supported_preprocessor(p)
