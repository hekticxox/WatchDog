def multi_factor_signal(rsi, macd, macd_signal, close, bb_upper, bb_lower, atr, st_k, st_d, vwap):
    buy_score = 0
    sell_score = 0
    # Example confluence logic for buy
    if rsi is not None and rsi < 35:
        buy_score += 1
    if macd is not None and macd > 0:
        buy_score += 1
    if close is not None and bb_lower is not None and close < bb_lower:
        buy_score += 1
    if st_k is not None and st_d is not None and st_k < 20 and st_d < 20:
        buy_score += 1

    # Example confluence logic for sell
    if rsi is not None and rsi > 65:
        sell_score += 1
    if macd is not None and macd < 0:
        sell_score += 1
    if close is not None and bb_upper is not None and close > bb_upper:
        sell_score += 1
    if st_k is not None and st_d is not None and st_k > 80 and st_d > 80:
        sell_score += 1

    if buy_score >= 3:
        return "buy"
    elif sell_score >= 3:
        return "sell"
    else:
        return "hold"