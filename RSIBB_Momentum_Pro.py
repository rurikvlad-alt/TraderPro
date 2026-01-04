import pandas as pd
import talib.abstract as ta
import freqtrade.vendor.qtpylib.indicators as qtpylib
from freqtrade.strategy.interface import IStrategy
from pandas import DataFrame

class RSIBB_Momentum_Pro(IStrategy):
    timeframe = '1h'
    minimal_roi = {
        "0": 0.02,
        "60": 0.015,
        "180": 0.01,
        "360": 0
    }
    stoploss = -0.03
    trailing_stop = True
    trailing_stop_positive = 0.01
    trailing_stop_positive_offset = 0.015
    trailing_only_offset_is_reached = True

    def populate_indicators(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        boll = qtpylib.bollinger_bands(dataframe["close"], period=20, stddev=2)
        dataframe["bb_upperband"] = boll["upper"]
        dataframe["bb_middleband"] = boll["mid"]
        dataframe["bb_lowerband"] = boll["lower"]
        dataframe["rsi"] = ta.RSI(dataframe, timeperiod=14)
        return dataframe

    def populate_buy_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        dataframe.loc[
            (
                (dataframe["rsi"] < self.rsi_buy.value)
                & (dataframe["close"] < dataframe["bb_lowerband"])
                & (dataframe["bb_width"] > self.bb_width_min.value)
                & (dataframe["momentum"] > 0)
                & (dataframe["volume"] > dataframe["volume_mean_slow"])
            ),
            "buy",
        ] = 1
        return dataframe

    def populate_sell_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        dataframe.loc[
            (
                (dataframe["rsi"] > self.rsi_sell.value)
                | (dataframe["close"] > dataframe["bb_upperband"])
                | (dataframe["momentum"] < 0)
            ),
            "sell",
        ] = 1
        return dataframe
