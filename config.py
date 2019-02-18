"""
======
Config
======

Several configurations on what data we want to extract.
"""
import numpy as np

loids = {8025: "S1", 7789: "S2", 7771: "S3"}
filters = {"LOID": ["7579", 7579, np.nan]}
transfer_filters = {"LOID": {8025, 7789, 7771, np.nan}}
unknown_columns = ["School", "Leeftijd", "Geslacht", "Cito-score",
                   "Cito vaardigheidscore"]
pre_ids = [1512433, 1928354, 2151770, 2151771, 966492, 1067176, 1041097,
           832284, 1740148, 1740522, 1740541, 1740547, 1334482, 1334489,
           1334486, 1334488, 1152951, 1152955, 1467251, 960793, 1474965,
           1474964, 1474963, 1474962]
post_ids = [2722251, 1874226, 838969, 1512439, 966513, 2592120, 827254, 972282,
            1740561, 1740151, 1740524, 2144152, 1334483, 1334484, 1334485,
            1334487, 2722255, 2722256, 933320, 1467252, 1222454, 1474966,
            2722257, 1474967, ]
gui_ids = [2151774, 1683854, 1683859, 1683868, 1683947, 2606967, 1683954,
           1684039, 1684040, 2151775, 1686784, 1686785, 1686786, 1686787,
           1686788, 1686789, 2151776, 1713996, 1713998, 1703196, 1703213,
           1707408, 1703212, 1703214, 1703217, ]
nap_ids = [2606968, 2606969, 2606991, 2606990, 1684033, 1684034, 1684035,
           1684036, 2606989, 1684041, 1684042, 1684064, 1684066, 1686790,
           1686791, 1686792, 1686793, 1686767, 1686769, 1686771, 1686772,
           1686774, 1686775, 1686781, 1686776, 1707403, 1707390, 1707394,
           1703090, 1703096, 1703097, 1703099, 1703100, 1703072, 1703082,
           1703081, 2606625, 2606626, 1702897, 1703108, ]

PARAMETER_L = [0.001, .027, 0.536]
PARAMETER_T = [0.149, .059, 0.101]
PARAMETER_G = [0.3, 0.250, 0.232]
PARAMETER_S = [0.1, 0.1, 0.1]
LEARNING_GOALS = [7771, 7789, 8025]
IMMEDIATE_PEAK_BOUNDARY = 10
MINIMUM_CHANGE = 0.015
MAXIMIMUM_DISTANCE_CLOSE_PEAKS = 25

use_estimated = False
if use_estimated is True:
    PARAMETER_L = [0.132, .027, 0.747]
    PARAMETER_T = [0.082, .026, 0.134]
    PARAMETER_G = [0.3, 0.3, 0.107]
    PARAMETER_S = [0.1, 0.1, 0.1]

no_limit = True
if no_limit is True:
    PARAMETER_L = [0.25, .047, 0.773]
    PARAMETER_T = [0.1, .021, 0.127]
    PARAMETER_G = [0.7, 0.356, 0.106]
    PARAMETER_S = [0.35, 0.226, 0.195]

