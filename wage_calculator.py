import pandas as pd
import matplotlib.pyplot as plt

class Wage_Calculator():
    '''Calculator to explore how new salary rates affect Astronomy Dept wages.'''
    def __init__(self):
        # import wages
        self.base_wages = pd.read_csv('base_wages.csv', index_col=0).T
        self.astro_wages = pd.read_csv('astro_wages.csv', index_col=0).T
        
        # old 60% FTE wages
        self.astro_wages_fte60 = (self.base_wages * 1.2).astype(int)
        
        # Seattle inflation for past 4 years, plus projected 3.5%, 3%, and 3% inflation
        # source https://www.bls.gov/regions/west/news-release/consumerpriceindex_seattle.htm
        self.inflation = {2021: 4.98, 2022: 8.93, 2023: 5.75, 2024: 4.35, 2025: 3.5, 2026: 3, 2027: 3}
        self.levels=list(self.base_wages.index)
        
        # initialize dataframes for pay increase rates and real wages
        self.base_gross_increase = pd.DataFrame([])
        self.astro_gross_increase = pd.DataFrame([])

        self.base_net_increase = pd.DataFrame([])
        self.astro_net_increase = pd.DataFrame([])
        
        self.base_real_wages = self.base_wages[[2021]]
        self.astro_real_wages = self.astro_wages[[2021]]
        self.astro_real_wages_fte60 = self.astro_wages[[2021]]
        
        self._calculate_gross_increases()
        self._calculate_net_increases()
        self._calculate_real_wages()
    
    
    def __str__(self):
        print('Base Pay:')
        self.print_df(self.base_wages)
        print()
        print('Astro Pay:')
        self.print_df(self.astro_wages)
        print(20 * '_', '\n')
        
        print('Astro Pay is Base Pay:')
        self.print_df(self.astro_wages.round(0) <= self.base_wages.round(0), sym='tf')
        print(20 * '_', '\n')        
        
        print('Base Gross Increases:')
        self.print_df(self.base_gross_increase, sym='%')
        print()
        print('Astro Gross Increases:')
        self.print_df(self.astro_gross_increase, sym='%')
        print(20 * '_', '\n')
    
        print('Base Net Increases:')
        self.print_df(self.base_net_increase, sym='%')
        print()
        print('Astro Net Increases:')
        self.print_df(self.astro_net_increase, sym='%')
        print(20 * '_', '\n')

        print('Base Net Pay (2021 Dollars):')
        self.print_df(self.base_real_wages)
        print()
        print('Astro Net Pay (2021 Dollars):')
        self.print_df(self.astro_real_wages)

        return ''
    
    
    def _calculate_gross_increases(self):
        # Calculate increase percentages from wages
        for year in self.base_wages.columns[1:]:
            self.base_gross_increase.loc[:,year] = (self.base_wages[year] / self.base_wages[int(year - 1)])
            self.astro_gross_increase.loc[:,year] = (self.astro_wages[year] / self.astro_wages[int(year - 1)])
            
            
    def _calculate_net_increases(self):
        # Calculate wage increase percentages after inflation
        for year in self.base_wages.columns[1:]:
            self.base_net_increase.loc[:,year] = (self.base_wages[year] / self.base_wages[int(year - 1)] / (self.inflation[year] / 100 + 1))
            self.astro_net_increase.loc[:,year] = (self.astro_wages[year] / self.astro_wages[int(year - 1)] / (self.inflation[year] / 100 + 1)) 

            
    def _calculate_wages_from_increases(self):
        # Calculate wages from increase percentages
        for year in self.base_wages.columns[1:]:
            self.base_wages.loc[:,year] = (self.base_wages[int(year - 1)] * self.base_gross_increase[year])#.astype(int)
            self.astro_wages.loc[:,year] = (self.astro_wages[int(year - 1)] * self.astro_gross_increase[year])#.astype(int)
            self.astro_real_wages_fte60.loc[:,year] = (self.astro_wages_fte60[int(year - 1)] * self.base_gross_increase[year])#.astype(int)
        
        self._check_wages_over_base()
    
    def _calculate_real_wages(self):
        # Calculate real wages in 2020-2021 dollars
        for year in self.base_wages.columns[1:]:
            self.base_real_wages.loc[:,year] = (self.base_real_wages[int(year - 1)] * self.base_net_increase[year])#.astype(int)
            self.astro_real_wages.loc[:,year] = (self.astro_real_wages[int(year - 1)] * self.astro_net_increase[year])#.astype(int)
            self.astro_real_wages_fte60.loc[:,year] = (self.astro_real_wages_fte60[int(year - 1)] * self.base_net_increase[year])#.astype(int)
   

    def _check_wages_over_base(self):
        print('Checking if astro wages ever fall below base wages.')
        if (self.astro_wages.astype(int) <= self.base_wages.astype(int)).values.sum():
            # Print out years when astro wages are also base wages
            self.print_df((self.astro_wages.round(0) <= self.base_wages.round(0)), sym='tf')
            for year in self.base_wages.columns:
                # Find all levels in year where astro wages are less than or equal to base wages
                astro_lt_base = self.astro_wages[year].astype(int) <= self.base_wages[year].astype(int)
                
                # Set astro wages to base wages for those levels in year
                self.astro_wages.loc[astro_lt_base, year] = self.base_wages.loc[astro_lt_base, year]
            
            # Recaulculate the gross percentage increases
            self._calculate_gross_increases()
                
            
    def _reset_all_values(self):
        self.__init__(self)
        
        
    def change_pay_increases(self, rate_name=None, level=None, years=[2025, 2026, 2027]):
        if level is None:
            level = input('Level (premaster, intermediate, candidate): ')
            level = level.lower()
            assert level.lower() in ('premaster', 'intermediate', 'candidate'), f'Entered level not valid: {level}'

        if rate_name is None:
            rate_name = input('Which Rate? (astro, base): ')
            rate_name = rate_name.lower()
            assert rate_name.lower() in ('astro', 'base'), f'Entered level not valid: {rate_name}'

        rates = []
        for year in years:
            x = input(f'{year} Rate (e.g. 3 for 3%): ')
            try:
                x = float(x)
            except:
                raise ValueError('Inputted rate must be a number')
                
            rates.append(1 + x / 100)
        
        if rate_name == 'astro':
            self.astro_gross_increase.loc[level, years] = rates
            
        if rate_name == 'base':
            self.base_gross_increase.loc[level, years] = rates
        
        # Recalculate gross wages, checking with a base rate floor:
        self._calculate_wages_from_increases()
        
        # Recalculate net increases and real wages:
        self._calculate_net_increases()
        self._calculate_real_wages()

        
    def change_inflation_rates(self, rates, years=[2025, 2026, 2027]):
        '''Change the inflation rates for the years specified
        
        Input:
            rates: list of interest rates e.g. 1.03 == 3% increase
            years: list of corresponding years'''
        
        assert len(rates) == len(years), f'Number of years and rates to update must be the same'

        for i in range(len(rates)):
            self.inflation[years[i]] = rates[i]
            
        # Recalculate net increases and real wages:
        self._calculate_net_increases()
        self._calculate_real_wages()            
        
        
    def plot_gross_wages(self, fte60=False):
        plt.figure(figsize=(10, 6))
        plt.title('Gross Wages by Level')
        years = list(self.base_wages.columns)
        colors = ['red', 'orange', 'green']
        for i, level in enumerate(self.levels):
            plt.plot(years, self.base_wages.loc[level], ':o', color=colors[i], label=f'base {level}')
            plt.plot(years, self.astro_wages.loc[level], '-o', color=colors[i], label=f'astro {level}')
            if fte60:
                plt.plot(years, self.astro_wages_fte60.loc[level], '-o', alpha=.3, color=colors[i], label=f'astro {level} FTE60')
        plt.xlabel('Year')
        plt.ylabel('Monthly Rate [$]')
        plt.legend()
        plt.show()

        
    def plot_net_wages(self, plot_base=True, fte60=False, wages2021_base=False, wages2021_astro=True):
        plt.figure(figsize=(10, 6))
        plt.title('Inflation Adjusted Wages by Level (2021 Dollars)')
        years = list(self.base_wages.columns)
        colors = ['red', 'orange', 'green']
        for i, level in enumerate(self.levels):
            plt.plot(years, self.astro_real_wages.loc[level], '-o', color=colors[i], label=f'astro {level}')
            if plot_base:
                plt.plot(years, self.base_real_wages.loc[level], ':o', color=colors[i], label=f'base {level}')
            if wages2021_base:
                plt.axhline(self.base_real_wages.loc[level, 2021], linestyle=':', alpha=.2, color=colors[i])
            if wages2021_astro:
                plt.axhline(self.astro_real_wages.loc[level, 2021], alpha=.2, color=colors[i])
            if fte60:
                plt.plot(years, self.astro_real_wages_fte60.loc[level], '-o', alpha=.3, color=colors[i], label=f'astro {level} FTE60')
        plt.xlabel('Year')
        plt.ylabel('Monthly Rate [2021 $]')
        plt.legend()
        plt.show()
        
        
    def print_df(self, df, sym='$'):
        if sym=='$':
            print('$'+df.astype(int).astype(str))
        elif sym=='%':
            print((100 * (df - 1)).round(1).astype(str) + '%')
        elif sym=='tf':
            print(df.astype(bool))
        else:
            print(df.round(3))