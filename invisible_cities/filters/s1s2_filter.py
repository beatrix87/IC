from argparse import Namespace

import numpy  as np
from .. core.system_of_units_c import units
#from ..reco.pmaps_functions   import integrate_S2Si_charge

def select_peaks(peaks,
                 Emin, Emax,
                 Lmin, Lmax,
                 Hmin, Hmax,
                 Ethr = -1):

    is_valid = lambda E: (Lmin <= np.size(E) < Lmax and
                          Hmin <= np.max (E) < Hmax and
                          Emin <= np.sum (E) < Emax)

    return {peak_no: (t, E) for peak_no, (t, E) in peaks.items() if is_valid(E[E > Ethr])}


def select_Si(peaks,
              Nmin, Nmax):
    is_valid = lambda sipms: Nmin <= len(sipms) < Nmax
    return {peak_no: sipms for peak_no, sipms in peaks.items() if is_valid(sipms)}


class S12Selector:
    def __init__(self, **kwds):
        conf = Namespace(**kwds)
        self.S1_Nmin     = conf.s1_nmin
        self.S1_Nmax     = conf.s1_nmax
        self.S1_Emin     = conf.s1_emin
        self.S1_Emax     = conf.s1_emax
        self.S1_Lmin     = conf.s1_lmin
        self.S1_Lmax     = conf.s1_lmax
        self.S1_Hmin     = conf.s1_hmin
        self.S1_Hmax     = conf.s1_hmax
        self.S1_Ethr     = conf.s1_ethr

        self.S2_Nmin     = conf.s2_nmin
        self.S2_Nmax     = conf.s2_nmax
        self.S2_Emin     = conf.s2_emin
        self.S2_Emax     = conf.s2_emax
        self.S2_Lmin     = conf.s2_lmin
        self.S2_Lmax     = conf.s2_lmax
        self.S2_Hmin     = conf.s2_hmin
        self.S2_Hmax     = conf.s2_hmax
        self.S2_NSIPMmin = conf.s2_nsipmmin
        self.S2_NSIPMmax = conf.s2_nsipmmax
        self.S2_Ethr     = conf.s2_ethr

    def select_S1(self, s1d):
        return select_peaks(s1d,
                               self.S1_Emin, self.S1_Emax,
                               self.S1_Lmin, self.S1_Lmax,
                               self.S1_Hmin, self.S1_Hmax,
                               self.S1_Ethr)

    def select_S2(self, s2d, sid):
        s2df = select_peaks(s2d,
                              self.S2_Emin, self.S2_Emax,
                              self.S2_Lmin, self.S2_Lmax,
                              self.S2_Hmin, self.S2_Hmax,
                              self.S2_Ethr)
        sidf = select_Si(sid,
                           self.S2_NSIPMmin, self.S2_NSIPMmax)

        valid_peaks = set(s2df) & set(sidf)
        s2s = {peak_no: peak for peak_no, peak in s2df.items() if peak_no in valid_peaks}
        sis = {peak_no: peak for peak_no, peak in sidf.items() if peak_no in valid_peaks}
        return s2s, sis


def s1s2_filter(selector, s1, s2, s2si):
    """Takes the event pmaps (s1, s2 and  s2si)
    and filters the corresponding peaks in terms. The
    objects s1df, s2df and sidf are filtered dictionaries
    {peak:[(t,E)]}

    """

    # s1f, s2f and sif are filtered dicts, containining
    # the peaks that pass selection
    s1df          = selector.select_S1(s1.s1d)
    s2df, _       = selector.select_S2(s2.s2d, s2si.s2sid)

    return (selector.S1_Nmin <= len(s1df) <= selector.S1_Nmax and
            selector.S2_Nmin <= len(s2df) <= selector.S2_Nmax)

def s2si_filter(s2si):
    """All peaks must contain at least one non-zero charged sipm"""

    def at_least_one_sipm_with_Q_gt_0(Si):
        return any(q > 0 for q in Si.values())

    def all_peaks_contain_at_least_one_non_zero_charged_sipm(iS2Si):
        return all(at_least_one_sipm_with_Q_gt_0(Si)
                          for Si in iS2Si.values())
    #iS2Si = integrate_S2Si_charge(s2si.s2sid)
    iS2Si = s2si.peak_and_sipm_total_energy_dict()
    return all_peaks_contain_at_least_one_non_zero_charged_sipm(iS2Si)