import pathlib

import pandas as pd


class DataHandler:
    
    req_cols = ["Open", "High", "Low", "Close", "Volume"]  # noqa: RUF012
    price_cols = ["Open", "High", "Low", "Close"]  # noqa: RUF012
    
    def __init__(self, filepath):
        self.filepath = pathlib.Path(filepath)
        self.data = self._load_data(filepath)
        self._validate_data()
        
    def _load_data(self, filepath):
        
        # Check that the file exists
        if not self.filepath.exists():
            raise FileNotFoundError(f'File not found at: {self.filepath}')
        
        # Check that it is a file
        if not self.filepath.is_file():
            raise ValueError(f'Path is not a file: {self.filepath}')
        
        # Read file
        try:
            data = pd.read_csv(filepath, skiprows=[1,2])
            data = data.rename(columns={'Price': 'Date'})
        except pd.errors.EmptyDataError:
            raise ValueError(f'Data file is empty: {self.filepath}')
        except pd.errors.ParserError as e:
            raise ValueError(f'Could not parse CSV: {e}')
        
        # Check that the data was loaded
        if data.empty:
            raise ValueError(f'No data was loaded from CSV: {self.filepath}')
            
        return data
    
    def _validate_data(self):
        self._check_columns()
        self.check_dates()
        self._check_numeric()
        self._missing_values()
        self._positive_prices()
        self._check_volume() 
        self._check_relations()
        
    def _missing_values(self):
        # Find missing data
        missing = self.data[self.req_cols].isna().sum()
        missing = missing[missing > 0]
        if not missing.empty:
            raise ValueError(f'Missing values found: {missing.to_dict()}')
        
    def _positive_prices(self):
        # Prices are strictly positive
        if (self.data[self.price_cols] <= 0).any().any():
            raise ValueError('Non-positive prices found')
        
    def _check_columns(self):
        # Check for missing columns
        missing = [column for column in self.req_cols if column not in self.data.columns]
        if missing:
            raise ValueError(f'Missing required columns: {missing}')
    
    def check_dates(self):
        # No date column
        if 'Date' not in self.data.columns:
            raise ValueError(' No date column found')
        
        # DateTime casting
        try:
            self.data['Date'] = pd.to_datetime(self.data['Date'], errors='raise')
        except (ValueError, TypeError) as e:
            raise ValueError(f'Invalid date values: {e}')
        
        # Missing dates
        if self.data['Date'].isna().any():
            raise ValueError('Missing value in Date column')
        
        # Duplicate date
        if self.data['Date'].duplicated().any():
            duplicates = self.data.loc[self.data['Date'].duplicated(), 'Date'].dt.strftime('%Y-%m-%d').tolist()
            raise ValueError(f'Duplicate dates found: {duplicates[:5]}')
        
        self.data = self.data.sort_values('Date')
        self.data = self.data.set_index('Date')
        
    def _check_numeric(self):
        # Check numerical columns
        columns = self.price_cols + ['Volume']
        for column in columns:
            try:
                self.data[column] = pd.to_numeric(self.data[column], errors='raise')
            except (ValueError, TypeError) as e:
                raise ValueError(f'Column {column} contains non-numeric values: {e}')
            
    def _check_volume(self):
        if (self.data['Volume'] < 0).any():
            raise ValueError('Negative volume found')
        
    def _check_relations(self):
        # High < Open or Close
        invalid_high = self.data['High'] < self.data[['Open','Close']].max(axis=1)
        if invalid_high.any():
            raise ValueError('Row where High < Open or Close')
        
        # Low > Open or Close
        invalid_low = self.data['Low'] > self.data[['Open','Close']].min(axis=1)
        if invalid_low.any():
            raise ValueError('Row where Low > Open or Close')    
            
    def get_close(self, date):
        
        # Generate Timestamp
        try:
            date = pd.Timestamp(date)
        except (ValueError, TypeError) as e:
            raise ValueError(f'Invalid date: {date}') from e

        # Date not in index
        if date not in self.data.index:
            raise KeyError(f'Date not found in dataset: {date}')
        
        return self.data.loc[date, 'Close']
        
    def get_between(self, start, end):
        
        # Generate Timestamps
        try:
            start = pd.Timestamp(start)
            end = pd.Timestamp(end)
        except (ValueError, TypeError) as e:
            raise ValueError('Invalid start or end date') from e
        
        # Start must be before end
        if start > end:
            raise ValueError('Start date must be before end date')
        
        # Period before Data
        if end < self.data.index.min():
            raise ValueError('Requested period is before the dataset begins')
        
        if start > self.data.index.max():
            raise ValueError('Requested period is after the dataset ends')
        
        return self.data.loc[start:end].copy()
    
    def get_all(self):
        return self.data.copy()
    
    def get_dates(self):
        return self.data.index.copy()