# Get_Stock_Prices
 
## How to use
### Build environment
```
git clone https://github.com/samwang1228/Get_tse_otc.git
cd Get_tse_otc
pip install -r requirement.txt
```
### Get stock price
```python
# searchprice.py
# type = 'tse' or 'otc'
type = 'tse'
# set date range
start_date = '2024-07-01'
end_date = '2024-09-05'
```
```
python seachprice.py
```
### Filter ETF and only 4 digit stock

```python
# filter.py
# set input file and output file
input_file = 'stock_prices_20240701_20240905.csv'
otc_file=os.path.join('otc',input_file)
tse_file=os.path.join('tse',input_file)
otc_output_file = os.path.join('otc',f'filtered_{input_file}')
tse_output_file = os.path.join('tse',f'filtered_{input_file}')
filter_four_digit_stocks(otc_file, otc_output_file)
filter_four_digit_stocks(tse_file, tse_output_file)
```
```
python filter.py
```
### Calculate stock growth rate
```python
python calculate.py
```

### renew data
* step 1
```python
# seachprice.py
# set date range
start_date = 'new start date'
end_date = 'new end date'
fetcher.set_date_range(start_date, end_date)
# set stock type
type = 'tse'
fetcher.set_stock_type(type)
# set existing file
existing_file = 'original file'
fetcher.add_historical_prices(existing_file)
```
* step 2
```python
modify olddate.txt to your olddate
modify date.txt to your newdate
```
```pytho
python updatefile.py
```