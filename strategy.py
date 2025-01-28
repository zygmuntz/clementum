import polars as pl

from tqdm import tqdm
from matplotlib import pyplot as plt
from defs import momentum_score, momentum_score_alt

class Strategy():
	
	"""backtest a momentum strategy"""
	
	def __init__( self, df_prices, df_returns ):
		self.cash = 1e6
		self.shares = None
		self.history = []
		self.verbose = True
		
		self.step_size = 63
		self.window_size = 120
		self.vola_window_size = 21
		self.min_momentum_score = 30
		self.portfolio_size = 30
		self.costs = 0.001
		
		self.df_prices = df_prices
		self.df_returns = df_returns
		
		self.preselector = None
		self.can_trade_series = None
		self.can_trade_now = True
		
		self.use_alt_momentum_scores = True
		if self.use_alt_momentum_scores:
			print( "Using alternative momentum scores." )
			self.min_momentum_score = 0.1
			
			
	def plot( self, symbol ):
		
		"""plot symbol returns using the current returns window"""
		plt.plot(( self.window_returns[symbol] + 1 ).cum_prod())
		
		
	def set_window( self, start, symbols = None ):
		
		"""set temporal window for a given time step"""
		
		end = start + self.window_size
		
		if self.verbose:
			print( "window: {}:{}".format( start, end ))
		
		self.window_prices = self.df_prices[start:end]
		self.window_returns = self.df_returns[start:end]
		
		if self.window_prices.is_empty() or self.window_returns.is_empty():
			return
		
		#assert self.window_prices.shape[0] > 0
		assert self.window_prices.shape[1] == self.df_prices.shape[1]
		
		self.current_prices = self.window_prices[-1]
		
		if symbols is None:
			return
			
		#print( symbols )
		self.window_prices = self.window_prices[ symbols ]
		self.window_returns = self.window_returns[ symbols ]
		
		# trend filter
		if self.can_trade_series is not None:
			self.can_trade_now = self.can_trade_series[ start:end ][-1]
			if not self.can_trade_now and self.verbose:
				print( "CAN'T TRADE" )
		
		

	def set_momentum_scores( self ):
		
		"""
		calculate momentum scores
		result is two column df, symbol-score		
		"""
		
		self.momentum_scores = self.window_prices.select( pl.all().map_batches( momentum_score ))		# row series
		self.momentum_scores = pl.DataFrame([ self.window_prices.columns, self.momentum_scores.transpose() ], ['symbol', 'score'])
		self.momentum_scores = self.momentum_scores.sort( pl.col('score'), descending = True, nulls_last = True )
		
		# alternative
		momentum_scores_alt = self.window_returns.select( pl.all().map_batches( momentum_score_alt ))		# row series
		self.momentum_scores_alt = pl.DataFrame([ self.window_returns.columns, momentum_scores_alt.transpose() ], ['symbol', 'score'])
		self.momentum_scores_alt = self.momentum_scores_alt.sort( pl.col('score'), descending = True, nulls_last = True )	
	
		if self.use_alt_momentum_scores:
			self.momentum_scores = self.momentum_scores_alt
		
		
	def select_symbols( self ):		
		
		"""select symbols based on momentum score and portfolio size"""
		
		self.set_momentum_scores()
		self.selected_symbols = self.momentum_scores.filter( pl.col( 'score' ) >= self.min_momentum_score )
		self.selected_symbols = self.selected_symbols[:self.portfolio_size]
		# self.selected_symbols = self.selected_symbols[:0]		# debugging no symbols to buy situation
		

	def set_volatility( self ):
		
		"""
		compute volatility
		sets a row vector df
		TODO: maybe only for selected symbols
		"""
		
		# compute volatility for symbols in d
		self.volatility = self.window_returns[-self.vola_window_size:].std()
		assert len( self.volatility ) == 1
		assert ( self.volatility.to_numpy() > 0 ).all()
	
	
	def set_weights( self ):
		
		"""get portfolio weights for selected symbols based on volatility"""
		
		if len( self.selected_symbols ) < 1:
			self.cash_part = 1
			self.non_cash_part = 0
			self.weights = None
			return
		
		self.selected_volatility = self.volatility[ self.selected_symbols['symbol']]
		self.inv_selected_volatility = self.selected_volatility.select( pl.all().map_batches( lambda _: 1 / _ ))
		sum_inv_sel_vol = self.inv_selected_volatility.map_rows( sum ).item()
		
		self.weights = self.inv_selected_volatility / sum_inv_sel_vol
				
		# if fewer than desired symbols are selected, we leave some cash
		self.non_cash_part = len( self.selected_symbols ) / self.portfolio_size
		self.cash_part = 1 - self.non_cash_part
		
		self.weights *= self.non_cash_part
		
	def sell( self ):

		"""sell all shares, go cash"""
		
		if self.shares is None:
			if self.verbose:
				print( 'nothing to sell' )
			return
		
		self.prices = self.current_prices[ self.shares.columns ] * ( 1 - self.costs )
		self.income = self.prices * self.shares
		self.income = self.income.map_rows( sum ).item()
		
		self.shares = None
		self.cash += self.income
		
		if self.verbose:
			print( self.prices )
		

	def buy( self ):

		"""buy according to weights and available cash"""
		
		if not self.can_trade_now:
			return
		
		if self.non_cash_part == 0:
			if self.verbose:
				print( 'not buying anything' )
			self.shares = None
			return
		
		cash_for_buying = self.cash * self.non_cash_part
		self.symbol_allocation = self.weights * cash_for_buying
		self.prices = self.current_prices[ self.weights.columns ] * ( 1 + self.costs )
		self.shares = self.symbol_allocation / self.prices
		
		self.cash -= cash_for_buying
		
		if self.verbose:
			print( "\n\nprices:", self.prices )
		
	def clear_variables( self ):
		
		"""delete intermediate variables from the previous step (to avoid any confusion in debugging)"""
		
		self.window_prices = None
		self.window_returns = None
		self.momentum_scores = None
		self.selected_symbols = None
		self.volatility = None
		self.inv_selected_volatility = None
		#self.sum_inv_sel_vol = None
		self.weights = None
		self.symbol_allocation = None
		self.prices = None
		self.cash_part = None
		self.non_cash_part = None
		
	def step( self, i ):
		
		"""the core method, simulate one time step"""
		
		self.clear_variables()
		
		if self.preselector:
			self.universe_symbols = self.preselector.select_universe( i, i + self.window_size )
		else:
			self.universe_symbols = None
		
		self.set_window( i, self.universe_symbols )
		if self.window_prices.is_empty() or self.window_returns.is_empty():
			return
		
		self.select_symbols()
		self.set_volatility()
		self.set_weights()
		
		self.sell()
		self.history.append( self.cash )
		if self.verbose:
			print( 'portfolio value: {:.2f}'.format( self.cash ))
		
		self.buy()
		
	def simulate( self ):
		
		"""run backtest by stepping over historical data"""
		
		if self.verbose:
			for i in range( 0, len( self.df_prices ), self.step_size ):
				self.step( i )
		else:
			# just tqdm progress bar
			for i in tqdm( range( 0, len( self.df_prices ), self.step_size )):
				self.step( i )			
			
