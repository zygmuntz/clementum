clementum
=========

This is a simplified implementation of a momentum strategy for stocks, as described by Andreas F. Clenow in the following books:

* Stocks on the move, 2015
* Trading evolved, 2019

The author provides source code in the second book, it's linked from the [official page](https://www.followingthetrend.com/trading-evolved/). The source code uses Zipline for backtesting (the original Zipline is discontinued, but there is [Zipline reloaded](https://github.com/stefan-jansen/zipline-reloaded)). Zipline forces its expectations and standards on the user, so if you don't want to learn it and would rather skip loading data into Zipline, here's an alternative.

	defs - functions, mainly the momentum score
	main_synth - run the backtest on synthetic data
	make_synth_data - make synthetic data
	preselector - a class for preselecting the stocks to consider, used by the Strategy class
	requirements.txt - the list of required Python modules
	strategy - the main class implementing the backtester for the strategy
	
How to run
----------

Run `main_synth.py`, basically:

	st = Strategy( prices, returns )
	st.verbose = False
	st.simulate()

	plt.plot( st.history )
	
Data
----

As input the Strategy consumes daily prices and daily returns. Notice that these are mostly the same thing in two different formats. See `make_synt_data.py` for the format details. Rows are time steps and columns are symbols.

This software uses polars. If you prefer working with pandas, it should be straightforward to convert a pandas data frame into a polars data frame, and vice versa, using something like:

	import polars as pl
	
	polars_df = pl.DataFrame( pandas_df )

More information later
----------------------
