"""make synthetic returns and prices"""

import numpy as np
import polars as pl

n_symbols = 500
n_periods = 1000

symbols = [ "A{}".format( a ) for a in range( n_symbols )]

# slightly positive returns
returns = np.random.normal( 0.0005, 0.01, ( n_periods, n_symbols ))
prices = np.cumprod( returns + 1, axis = 0 )

returns = pl.DataFrame( returns, symbols )
prices = pl.DataFrame( prices, symbols )
