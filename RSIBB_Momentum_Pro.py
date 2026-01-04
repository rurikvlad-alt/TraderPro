from freqtrade.strategy import IStrategy, IntParameter, DecimalParameter
from pandas import DataFrame
import technical.indicators as qtpylib
import talib.abstract as ta

class RSIBB_Momentum_Pro(IStrategy):
    timeframe = "1h"
    startup_candle_count = 30
    process_only_new_candles = True
    use_exit_signal = True
    exit_profit_only = False
    ignore_roi_if_entry_signal = False

    minimal_roi = {"0": 0.02, "60": 0.015, "180": 0.01, "360": 0}
    stoploss = -0.03
    trailing_stop = True
    trailing_stop_positive = 0.01
    trailing_stop_positive_offset = 0.015
    trailing_only_offset_is_reached = True

    rsi_buy = IntParameter(20, 40, default=30, space="buy")
    rsi_sell = IntParameter(60, 80, default=70, space="sell")
    bb_width_min = DecimalParameter(0.010, 0.050, default=0.02, space="buy")

    def populate_indicators(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        dataframe["rsi"] = ta.RSI(dataframe)
        boll = qtpylib.bollinger_bands(dataframe["close"], window=20, stds=2)
        dataframe["bb_lowerband"] = boll["lower"]
        dataframe["bb_middleband"] = boll["mid"]
        dataframe["bb_upperband"] = boll["upper"]
        dataframe["bb_width"] = (boll["upper"] - boll["lower"]) / dataframe["bb_middleband"]
        dataframe["ema_fast"] = ta.EMA(dataframe, timeperiod=9)
        dataframe["ema_slow"] = ta.EMA(dataframe, timeperiod=21)
        dataframe["momentum"] = dataframe["ema_fast"] - dataframe["ema_slow"]
        dataframe["volume_mean_slow"] = ta.SMA(dataframe["volume"], timeperiod=30)
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
