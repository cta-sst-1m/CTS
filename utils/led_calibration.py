import pickle
import numpy as np
ac_led_calib = pickle.load( open('/data/software/CTS/config/ac_led_calib_spline_120.p' , "rb" ) )
ac_patch_calib = pickle.load( open('/data/software/CTS/config/ac_patch_calib_spline_120.p' , "rb" ) )

# revert by LED and LED Patch
ac_led_calib_byled = {}
for k in ac_led_calib.keys():
    ac_led_calib_byled[ac_led_calib[k]['LED']]={
        'DAC':ac_led_calib[k]['DAC'],
        'NPE':ac_led_calib[k]['NPE']
    }
ac_patch_calib_byled = {}
for k in ac_patch_calib.keys():
    ac_patch_calib_byled[ac_patch_calib[k]['LED']]={
        'DAC':ac_patch_calib[k]['DAC'],
        'NPE':ac_patch_calib[k]['NPE']
    }

def get_ACLED_DAC(npe,pixel):
    if pixel in ac_led_calib.keys():
        return ac_led_calib[pixel]['DAC'][np.argmin(np.abs(ac_led_calib[pixel]['NPE']-npe))]
    else :
        new_pix = np.argmin(np.abs(np.array(list(ac_led_calib.keys()))-pixel))
        print('replace the calib of pixel',pixel,'by pixel',new_pix)
        return ac_led_calib[new_pix]['DAC'][np.argmin(np.abs(ac_led_calib[new_pix]['NPE']-npe))]


def get_ACPATCH_DAC(npe,patch):
    if patch in ac_patch_calib.keys():
        return ac_patch_calib[patch]['DAC'][np.argmin(np.abs(ac_patch_calib[patch]['NPE']-npe))]
    else :
        new_patch = np.argmin(np.abs(np.array(list(ac_patch_calib.keys()))-patch))
        print('replace the calib of patch',patch,'by patch',new_patch)
        return ac_patch_calib[new_patch]['DAC'][np.argmin(np.abs(ac_patch_calib[new_patch]['NPE']-npe))]

def get_ACLED_DAC_byled(npe,led):
    if led in ac_led_calib_byled.keys():
        return ac_led_calib_byled[led]['DAC'][np.argmin(np.abs(ac_led_calib_byled[led]['NPE']-npe))]
    else :
        new_pix = np.argmin(np.abs(np.array(list(ac_led_calib_byled.keys()))-led))
        print('replace the calib of led',led,'by led',new_led)
        return ac_led_calib_byled[new_led]['DAC'][np.argmin(np.abs(ac_led_calib_byled[new_eld]['NPE']-npe))]


def get_ACPATCH_DAC_byled(npe,patch):
    if patch in ac_patch_calib_byled.keys():
        return ac_patch_calib_byled[patch]['DAC'][np.argmin(np.abs(ac_patch_calib_byled[patch]['NPE']-npe))]
    else :
        new_patch = np.argmin(np.abs(np.array(list(ac_patch_calib_byled.keys()))-patch))
        print('replace the calib of patch',patch,'by patch',new_patch)
        return ac_patch_calib_byled[new_patch]['DAC'][np.argmin(np.abs(ac_patch_calib_byled[new_patch]['NPE']-npe))]
