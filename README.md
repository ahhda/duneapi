# Dune Analytics API

A simple framework for interacting with Dune Analytics unsupported API. The primary
class (`DuneAnalytics`) of this repo is adapted from
https://github.com/itzmestar/duneanalytics at commit
bdccd5ba543a8f3679e2c81e18cee846af47bc52

## Installation & Usage

```shell
python3 -m venv venv
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

To fetch some sample ethereum block data, run the sample script as:

```shell
python -m src.sample_fetch
```

This will result in the following console logs:

```
got 10 records from last query
First record Record(
    string='0x255309e019abaf74bf2d58d4020547c89f875842abae1c874fb0d5ae8eac9859', 
    integer=14362177, 
    decimal=0.14785533, 
    time='2022-03-10T23:50:16+00:00'
)
```
