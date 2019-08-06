"""
======
Config
======

Several configurations on what data we want to extract.
"""
GYNZY = True
use_estimated = False
parameters_babette = False
parameters_simone = False
parameters_nadine = False
parameters_kb = True
no_limit = False

import numpy as np

nadine_file_name = "./../Applab/Moment2Moment/resultaten-radboud-all_anoniem "\
              "samengevoegd_editforfirstattempts.xlsx"

if GYNZY is False:
    loids = {8025: "S1", 7789: "S2", 7771: "S3"}
else:
    loids = {8232: "S1", 8234: "S2", 8240: "S3"}

filters = {"LOID": ["7579", 7579, np.nan, 8181], "UserId": [2217523, 1376603]}
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
if parameters_simone is True:
    post_ids = [1928354, 1874226, 838969, 1512439, 966513, 2592120, 827254,
                972282, 1740561, 1740151, 1740524, 2144152, 1334483, 1334484,
                1334485, 1334487, 1152951, 1467251, 933320, 1467252,
                1222454, 1474966, 1474963, 1474967, 993861]
gui_ids = [2151774, 1683854, 1683859, 1683868, 1683947, 1683951, 1683954,
           1684039, 1684040, 2151775, 1686784, 1686785, 1686786, 1686787,
           1686788, 1686789, 2151776, 1713996, 1713998, 1703196, 1703213,
           1707408, 1703212, 1703214, 1703217, ]
nap_ids = [2606968, 2606969, 2606991, 2606990, 1684033, 1684034, 1684035,
           1684036, 2606989, 1684041, 1684042, 1684064, 1684066, 1686790,
           1686791, 1686792, 1686793, 1686767, 1686769, 1686771, 1686772,
           1686774, 1686775, 1686781, 1686776, 1707403, 1707390, 1707394,
           1703090, 1703096, 1703097, 1703099, 1703100, 1703072, 1703082,
           1703081, 2606625, 2606626, 1702897, 1703108, ]

gynzy_pre_ids = [938564, 1658437, 1656606, 939141, 939337, 1656633, 1656624,
                 938961, 926827, 1657174, 1657179, 926618, 926747, 1657008,
                 926732, 926651, 930400, 1657994, 1657952, 930092, 1657973,
                 1657956, 1657918, 1657943]

gynzy_post_ids = [1656709, 1656619, 1656593, 1440977, 1658439, 1656638,
                  939329, 926651, 1441003, 1657023, 1657053, 1657049,
                  1657054, 1657059, 926732, 1657173, 929883, 1657961,
                  928752, 930304, 931544, 1658789, 1657978, 931192]

PARAMETER_L = [0.001, .027, 0.536]
PARAMETER_T = [0.149, .059, 0.101]
PARAMETER_G = [0.3, 0.250, 0.232]
PARAMETER_S = [0.1, 0.1, 0.1]
LEARNING_GOALS = [7771, 7789, 8025]
if GYNZY is True:
    LEARNING_GOALS = [8232, 8234, 8240]  # Test for Babette
IMMEDIATE_PEAK_BOUNDARY = 10
MINIMUM_CHANGE = 0.015
MAXIMIMUM_DISTANCE_CLOSE_PEAKS = 25

if use_estimated is True:
    PARAMETER_L = [0.132, .027, 0.747]
    PARAMETER_T = [0.082, .026, 0.134]
    PARAMETER_G = [0.3, 0.3, 0.107]
    PARAMETER_S = [0.1, 0.1, 0.1]

if no_limit is True:
    PARAMETER_L = [0.257, .047, 0.773]
    PARAMETER_T = [0.101, .021, 0.127]
    PARAMETER_G = [0.167, 0.356, 0.106]
    PARAMETER_S = [0.351, 0.226, 0.195]

if parameters_babette is True:
    PARAMETER_L = [0.116, 0.107, 0.002]
    PARAMETER_T = [0.037, 0.032, 0.026]
    PARAMETER_G = [0.3, 0.3, 0.3]
    PARAMETER_S = [0.1, 0.1, 0.1]

if parameters_simone is True:
    PARAMETER_L = [0.22, 0.45, 0.89]
    PARAMETER_T = [0.09, 0.14, 0.19]
    PARAMETER_G = [0.3, 0.08, 0.29]
    PARAMETER_S = [0.1, 0.1, 0.07]

if parameters_nadine is True:
    PARAMETER_L = [.321, .018, .772]
    PARAMETER_T = [.195, .073, .148]
    PARAMETER_G = [.026, .3, .076]
    PARAMETER_S = [.1, .1, .1]

if parameters_kb is True:
    PARAMETER_L = [.201, .591, .056]
    PARAMETER_T = [.083, .071, .064]
    PARAMETER_G = [.3, .3, .3]
    PARAMETER_S = [.1, .1, .001]

