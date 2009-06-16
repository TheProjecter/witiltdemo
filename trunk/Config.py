__author__="Simon Baev"
class Config:
    """
    Configuration storage and management
    @param
    frame_size -- size of frame in binary mode including XYZR channels
    @param
    calibration data -- [(XM,XW),(YM,YW),(ZM,ZW),RZ] where xM is ADC raw output
    corresponding to 0 gravity, xW is the "width" of gravity channel -- how many
    ADC tick encode maximal gravity value
    @param
    fps -- desired number of frames per second
    @param
    fs -- sampling rate of data retrival from WiTilt module
    """
    def __init__(self):
		pass

        