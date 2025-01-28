import polars as pl

class Preselector():
	
	"""select the universe of stocks to potentially trade based on their average daily volume"""
	
	def __init__( self, df_dolvol ):
		self.df_dolvol = df_dolvol
		self.limit = 1e6
		
	def select_universe( self, start, end ):
		self.window = self.df_dolvol[start:end]
		
		# version with symbols as rows
		#self.window = self.window.filter( pl.mean_horizontal( pl.all().exclude( 'symbol' )) > self.limit )
		
		# version selecting whole columns, not just names
		"""
		self.window.select(
			pl.col(col) for col in self.window.columns 
			if self.window[col].mean() > self.limit
		)
		"""
		
		symbols = [ col for col in self.window.columns if self.window[col].mean() > self.limit ]
		return symbols
		