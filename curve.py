import config


def get_type(curve):
    n_peaks, p_peaks = get_peaks(curve)
    print(f"the number of peaks is {n_peaks} and they are at locations "
          f"{p_peaks}")
    if n_peaks == 1:
        if p_peaks[0] < config.IMMEDIATE_PEAK_BOUNDARY:
            return 2
        else:
            return 3
    else:
        if n_peaks > 1:
            if n_peaks == 2:
                return 6
            if p_peaks[-1] < config.MAXIMIMUM_DISTANCE_CLOSE_PEAKS:
                return 4
            return 5
        else:
            return 1


def get_peaks(curve):
    n_peaks = 0
    p_peaks = []
    for point in range(1, len(curve) - 1):
        if curve[point] > curve[point + 1] + config.MINIMUM_CHANGE and curve[
         point] > curve[point - 1] + config.MINIMUM_CHANGE:
            n_peaks += 1
            p_peaks.append(point)
    return n_peaks, p_peaks


def get_curve(df, testing=False):
    loid = df.LOID.values[0]
    # print(loid)
    p_l = config.PARAMETER_L[config.LEARNING_GOALS.index(loid)]
    p_t = config.PARAMETER_T[config.LEARNING_GOALS.index(loid)]
    p_g = config.PARAMETER_G[config.LEARNING_GOALS.index(loid)]
    p_s = config.PARAMETER_S[config.LEARNING_GOALS.index(loid)]
    ln = get_ln(df, p_l, p_t, p_g, p_s, testing)
    n_ln_t = [(1 - n) * p_t for n in ln]
    n_ln_n_t = [(1 - n) * (1 - p_t) for n in ln]
    return calculate_p_j(df.Correct.values, ln, n_ln_t, n_ln_n_t, (p_t, p_g,
                                                                   p_s)), ln


def get_ln(df, l, t, g, s, testing):
    p_ln = [l]
    # print(l)
    for answer in df.Correct:
        k = p_ln[-1]
        if answer > 0:
            ln_prev_s = (k * (1 - s)) / ((k * (1 - s)) + ((1 - k) * g))
        else:
            ln_prev_s = (k * s) / ((k * s) + ((1 - k) * (1 - g)))
        new_k = ln_prev_s + (1 - ln_prev_s) * t
        if testing is True:
            new_k = min(new_k, 0.999)
        p_ln.append(new_k)
        # print(answer, ln_prev_s, p_ln[-1])
    return p_ln[1:]


def calculate_p_j(answers, ln, n_ln_t, n_ln_n_t, params):
    t, g, s = params
    p_jl = []
    for a_id in range(len(answers) - 2):
        p_l = ln[a_id]
        p_nl_t = n_ln_t[a_id]
        p_nl_nt = n_ln_n_t[a_id]
        if answers[a_id + 1] == 1:
            if answers[a_id + 2] == 1:  # RR
                a_l = (1 - s) ** 2
                a_nl_nt = g * (1 - t) * g + g * t * (1 - s)
            else:  # RW
                a_l = s * (1 - s)
                a_nl_nt = g * (1 - t) * (1 - g) + g * t * s
        else:
            if answers[a_id + 2] == 1:  # WR
                a_l = s * (1 - s)
                a_nl_nt = g * (1 - t) * (1 - g) + (1 - g) * t * (1 - s)
            else:  # WW
                a_l = s ** 2
                a_nl_nt = (1 - g) * (1 - t) * (1 - g) + (1 - g) * t * s
        a_nl_t = a_l
        a12 = p_l * a_l + p_nl_t * a_nl_t + p_nl_nt * a_nl_nt
        p_jl.append(a_nl_t * p_nl_t / a12)
    return p_jl
