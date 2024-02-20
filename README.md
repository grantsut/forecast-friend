# Forecast-Friend
Forecasting chat assistant, work-in-progress.

This is a work-in-progress chat assistant that creates time series forecasts using data from public repositories, helping you find good data and constructing a forecast model as required.

Available online at [https://forecast-friend-alpha.streamlit.app](https://forecast-friend-alpha.streamlit.app)

## Current capabilities
* Can search the FRED database and summarize available series.
* That's it, can't download data yet.

## Current issues
* The ChatGPT function calling API is hilariously unreliable and sometimes doesn't format its function calls correctly, there needs to be code to catch and handle this
* Sometimes ChatGPT doesn't bother calling the search function and just makes up results instead. Funny!
