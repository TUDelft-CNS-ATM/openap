"""
Given any trajectory, return the start and end of each flight phase. If data
is incomplete in desired flight phase, None will be returned.

Units:
  ts: second
  alt: feet
  spd: knot
  roc: feet/min
"""

import numpy as np
from openap import segment

def getTOIC(ts, alt, spd, roc=None):
    ts = np.array(ts)
    alt = np.array(alt)
    spd = np.array(spd)

    ndata = len(ts)

    # # skip data starting not on ground
    # if alt[0] > 0:      # ft
    #     return None

    # get the data chunk up to certain ft
    istart = 0
    iend = 0
    for i in range(0, ndata):
        if alt[i] < 1500:     # ft
            iend = i
            continue
        else:
            break

    # keep only the chunk in taking-off states, break at starting point
    spdtmp = spd[iend]
    for i in reversed(list(range(0, iend))):
        if spd[i] < 30 and spd[i] > spdtmp:
            break
        elif spd[i] < 5:
            break
        else:
            istart = i
            spdtmp = spd[i]


    # ignore too long take-off
    if ts[iend] - ts[istart] > 300:
        return None

    # ignore insufficient chunk size
    if iend - istart < 10:
        return None

    # ignore no in air data
    if alt[iend] < 200:
        return None

    # find the liftoff moment
    ilof = istart
    for i in range(istart+1, iend):
        if abs(alt[i] - alt[i-1]) > 10:
            ilof = i
            break


    # not sufficient data
    if ilof - istart < 5:
        return None

    return (istart, ilof, iend+1)


def getFALD(ts, alt, spd, roc=None):
    ts = np.array(ts)
    alt = np.array(alt)
    spd = np.array(spd)

    ndata = len(ts)

    # # skip data not ending on ground
    # if alt[-1] > 0:     # ft
    #     return None

    # get the approach + landing data chunk (h=0)
    istart = 0
    iend = 0

    for i in reversed(list(range(0, ndata))):
        if alt[i] < 1500:     # ft
            istart = i
        else:
            break


    # keep only the chunk in landing deceleration states, break at taxing point
    spdtmp = spd[istart]
    for i in range(istart, ndata):
        if spd[i] <= 50 and spd[i] >= spdtmp:       # kts
            break
        elif spd[i] < 30:
            break
        else:
            iend = i
            spdtmp = spd[i]

    # ignore insufficient chunk size
    # if iend - istart < 20:
    #     return None

    # ignore QNH altitude, or no in-air data
    if alt[istart] < 100:
        return None

    # # ignore where the end speed too high, ie. not breaked
    # if spd[iend] > 60: # kts
    #     return None

    # find the landing moment
    ild = iend
    for i in reversed(list(range(istart, iend-1))):
        if abs(alt[i] - alt[i+1]) > 10:
            ild = i
            break

    # ignore ground or air data sample less than 4
    if ild - istart < 5 or iend - ild < 5:
        return None

    return (istart, ild, iend+1)


def getCL(ts, alt, spd, roc):
    ts = np.array(ts)
    alt = np.array(alt)
    spd = np.array(spd)
    roc = np.array(roc)

    labels = segment.fuzzylabels(ts, alt, spd, roc)
    n = len(labels)

    if 'CL' not in labels:
        return None

    istart = labels.index('CL')

    if alt[istart] > 5000:
        # starting too low, data not good
        return None

    iend = istart + 1
    tmp_t = ts[iend]
    tmp_alt = alt[iend]

    for i in range(istart + 1, n):
        # stop when altitude has not increase 500 ft for 3 mins
        if (alt[i] - tmp_alt) > 500:
            tmp_alt = alt[i]
            tmp_t = ts[i]
            iend = i
        elif abs(tmp_t - ts[i]) > 180 and alt[i] > 6000:
            break

        # keep searching for CL, stop only when cruise for 5 minutes
        # if labels[i] == 'CR':
        #     if ts[i] - tmp_t > 300:
        #         break
        # elif labels[i] == 'CL':
        #     tmp_t = ts[i]
        #     iend = i
        # elif labels[i] not in ['CL', 'CR', 'NA']:
        #     break

    # if iend - istart < 200:
    #     # too few samples
    #     return None

    return istart, iend


def getDE(ts, alt, spd, roc):
    ts = np.array(ts)
    alt = np.array(alt)
    spd = np.array(spd)
    roc = np.array(roc)

    labels = segment.fuzzylabels(ts, alt, spd, roc)
    n = len(labels)

    if 'DE' not in labels:
        return None

    iend = n - 1 - labels[::-1].index('DE')

    if alt[iend] > 5000:
        # end too low, data not good
        return None

    istart = iend - 1
    tmp_t = ts[istart]
    tmp_alt = alt[istart]
    for i in range(0, iend)[::-1]:
        # stop when altitude has not decressed 1000 ft for 5 mins
        if (alt[i] - tmp_alt) > 1000:
            tmp_alt = alt[i]
            tmp_t = ts[i]
            istart = i
        elif abs(tmp_t - ts[i]) > 300 and alt[i] > 6000:
            break

        # keep searching for DE, stop only when cruise for 5 minutes
        # if labels[i] == 'CR':
        #     if abs(tmp_t - ts[i]) > 300 and alt[i] > 10000:
        #         break
        # elif labels[i] == 'DE':
        #     tmp_t = ts[i]
        #     istart = i
        # elif labels[i] not in ['DE', 'CR']:
        #     break

    # if iend - istart < 200:
    #     # too few samples
    #     return None

    if 'CR' in labels[istart:iend]:
        isCDA = False
    else:
        isCDA = True

    return istart, iend, isCDA


def getCR(ts, alt, spd, roc):
    ts = np.array(ts)
    alt = np.array(alt)
    spd = np.array(spd)
    roc = np.array(roc)

    # CR start = CL end, CR end = DE start
    ttCL = getCL(ts, alt, spd, roc)

    if not ttCL:
        return None

    ttDE = getDE(ts, alt, spd, roc)

    if not ttDE:
        return None

    ttDE = ttDE[0:2]

    istart = ttCL[-1]
    iend = ttDE[0]

    if iend - istart < 200:
        # too few samples
        return None

    return istart, iend


def getAll(ts, alt, spd, roc):
    ts = np.array(ts)
    alt = np.array(alt)
    spd = np.array(spd)
    roc = np.array(roc)

    ttTOIC = getTOIC(ts, alt, spd, roc)
    if ttTOIC == None:
        return None

    ttFALD = getFALD(ts, alt, spd, roc)
    if ttFALD == None:
        return None

    ttCL = getCL(ts, alt, spd, roc)
    if ttCL == None:
        return None

    ttDE = getDE(ts, alt, spd, roc)
    if ttDE == None:
        return None

    ttCR = getCR(ts, alt, spd, roc)
    if ttCR == None:
        return None

    istart = ttTOIC[0]
    iend = ttFALD[-1]

    if iend - istart < 600:
        # too few samples
        return None

    return istart, iend


def full_phase_idx(ts, alt, spd, roc):
    # Process the data and get the phase index
    ii_toic = getTOIC(ts, alt, spd, roc)
    ii_cl = getCL(ts, alt, spd, roc)
    ii_de = getDE(ts, alt, spd, roc)
    ii_fald = getFALD(ts, alt, spd, roc)

    ito = ii_toic[0] if ii_toic is not None else None
    iic = ii_toic[1] if ii_toic is not None else None
    icl = ii_toic[2] if ii_toic is not None else None
    icr = ii_cl[1] if ii_cl is not None else None
    ide = ii_de[0] if ii_de is not None else None

    if ii_fald is not None:
        ifa = ii_fald[0]
        ild = ii_fald[1]
        ied = ii_fald[2]
    elif ii_de is not None:
        ifa = ii_de[1]
        ild = None
        ied = len(ts)
    else:
        ifa = None
        ild = None
        ied = len(ts)

    idx = [ito, iic, icl, icr, ide, ifa, ild, ied]
    return idx
