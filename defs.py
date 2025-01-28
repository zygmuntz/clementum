import numpy as np
import polars as pl

from scipy.stats import linregress

def transpose_with_headers( df ):
	
	"""transpose a polars dataframe"""
	
	# Get new column names from first column
	new_headers = df.get_column( df.columns[0] ).to_list()
	
	# Transpose and get values excluding first column
	df_t = df.drop( df.columns[0] ).transpose()
	
	# Set new column names
	df_t.columns = new_headers
	
	return df_t


# Clenow's original implementation	
def momentum_score(ts):
	"""
	Input:  Price time series.
	Output: Annualized exponential regression slope,
			multiplied by the R2
	"""
	x = np.arange(len(ts))
	log_ts = np.log(ts)
	
	slope, intercept, r_value, p_value, std_err = linregress(x, log_ts)
	annualized_slope = (np.power(np.exp(slope), 252) - 1) * 100
	score = annualized_slope * (r_value ** 2)
	
	return score	
	
def momentum_score_alt( ts ):
	"""use Sharpe ratio as the momentum score"""
	return ts.mean() / ts.std()
	