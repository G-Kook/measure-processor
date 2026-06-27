def bridge_ileak_max() -> float:
    return 1e-9

def idvg_ioff_min_max(pid: str) -> tuple[float, float]:
    return -10e-12, 10e-12

def idvg_ion_min_max(pid: str) -> tuple[float, float]:
    if pid in ['Gen10']:
        return 80e-9, 200e-9
    if pid in ['Gen11']:
        return 60e-9, 200e-9
    raise Exception('pid is not supported')

def ispp_slope_min_max(pid: str) -> tuple[float, float]:
    return 0.1, 4.0

def ispp_slope_filter_range(pid: str) -> tuple[float, float]:
    return 14.1, 20