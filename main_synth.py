"""
run with synthetic data
this doesn't use volume data for preselection
or index data for trend filtering
"""

from matplotlib import pyplot as plt

from defs import *
from strategy import Strategy
from preselector import Preselector

from make_synth_data import prices, returns

#

st = Strategy( prices, returns )
st.verbose = False
st.simulate()

plt.plot( st.history )

