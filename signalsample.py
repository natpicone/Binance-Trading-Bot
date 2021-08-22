from helpers.parameters import load_config, parse_args

# Load arguments then parse settings
args = parse_args()
# get config file
DEFAULT_CONFIG_FILE = "config.yml"
config_file = args.config if args.config else DEFAULT_CONFIG_FILE
parsed_config = load_config(config_file)


# used for directory handling
import glob

# use for environment variables
import os

# use if needed to pass args to external modules
import sys
import time

from tradingview_ta import Exchange, Interval, TA_Handler

MY_EXCHANGE = "BINANCE"
MY_SCREENER = "CRYPTO"
MY_FIRST_INTERVAL = Interval.INTERVAL_1_MINUTE
MY_SECOND_INTERVAL = Interval.INTERVAL_5_MINUTES
TA_BUY_THRESHOLD = 18  # How many of the 26 indicators to indicate a buy
PAIR_WITH = parsed_config["trading_options"]["PAIR_WITH"]
TICKERS = parsed_config["trading_options"]["TICKERS_LIST"]
TIME_TO_WAIT = parsed_config["trading_options"][
    "SIGNALS_FREQUENCY"
]  # Minutes to wait between analysis
FULL_LOG = parsed_config["script_options"][
    "VERBOSE_MODE"
]  # List anylysis result to console


def analyze(pairs):
    taMax = 0
    taMaxCoin = "none"
    signal_coins = {}
    first_analysis = {}
    second_analysis = {}
    first_handler = {}
    second_handler = {}
    if os.path.exists("signals/signalsample.exs"):
        os.remove("signals/signalsample.exs")

    for pair in pairs:
        first_handler[pair] = TA_Handler(
            symbol=pair,
            exchange=MY_EXCHANGE,
            screener=MY_SCREENER,
            interval=MY_FIRST_INTERVAL,
            timeout=10,
        )
        second_handler[pair] = TA_Handler(
            symbol=pair,
            exchange=MY_EXCHANGE,
            screener=MY_SCREENER,
            interval=MY_SECOND_INTERVAL,
            timeout=10,
        )

    for pair in pairs:

        try:
            first_analysis = first_handler[pair].get_analysis()
            second_analysis = second_handler[pair].get_analysis()
        except Exception as e:
            print("Exeption:")
            print(e)
            print(f"Coin: {pair}")
            print(f"First handler: {first_handler[pair]}")
            print(f"Second handler: {second_handler[pair]}")
            tacheckS = 0

        first_tacheck = first_analysis.summary["BUY"]
        second_tacheck = second_analysis.summary["BUY"]
        if FULL_LOG:
            print(f"{pair} First {first_tacheck} Second {second_tacheck}")
        else:
            print(".", end="")

        if first_tacheck > taMax:
            taMax = first_tacheck
            taMaxCoin = pair
        if first_tacheck >= TA_BUY_THRESHOLD and second_tacheck >= TA_BUY_THRESHOLD:
            signal_coins[pair] = pair
            print("")
            print(f"Signal detected on {pair}")
            with open("signals/signalsample.exs", "a+") as f:
                f.write(pair + "\n")
    print("")
    print(f"Max signal by {taMaxCoin} at {taMax} on shortest timeframe")

    return signal_coins


if __name__ == "__main__":
    signal_coins = {}
    pairs = {}

    pairs = [line.strip() for line in open(TICKERS)]
    for line in open(TICKERS):
        pairs = [line.strip() + PAIR_WITH for line in open(TICKERS)]

    while True:
        print(f"Analyzing {len(pairs)} coins")
        signal_coins = analyze(pairs)
        if len(signal_coins) == 0:
            print(f"No coins above {TA_BUY_THRESHOLD} threshold")
        else:
            print(
                f"{len(signal_coins)} coins above {TA_BUY_THRESHOLD} treshold on both timeframes"
            )
        print(f"Waiting {TIME_TO_WAIT} minutes for next analysis")
        time.sleep((TIME_TO_WAIT * 60))
