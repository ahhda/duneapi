# Dune Analytics API

## Installation & Usage

```shell
python3 -m venv env
source ./env/bin/activate
pip install -r requirements.txt
cp .env.sample .env
source .env
```

Fill out your Dune credentials in the `.env` file. The Dune user and password are
straight-forward login credentials to Dune Analytics. The `DUNE_QUERY_ID` is an integer
id found in the URL of a query when saved in the Dune interface. This should be created
beforehand, but the same query id can be used everywhere throughout the program (as long
as it is owned by the account corresponding to the user credentials provided).

Each individual file should be executable as a standalone script. Many of the scripts
found here initiate and execute query, returning the results.

### Example Usage

To fetch the total eth spent, realized fees and cow rewards for an accounting period run
the period totals script as follows

```shell
python -m src.fetch.period_totals --start '2022-02-01' --end '2022-02-08'
```

This will result in the following console logs:
