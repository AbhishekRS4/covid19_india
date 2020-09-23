import os
import numpy as np
import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt


def latest_date():
	st.title("Covid-19 latest caseload dashboard")
	df_latest = pd.read_csv(csv_weblinks["statewise_daily"])

	states = df_latest.columns[2:]
	latest_values = df_latest.tail(3)
	latest_date = latest_values.to_numpy()[-1, 0]

	st.write("Latest data available from date : {}".format(latest_date))
	st.write(latest_values)

	plot_latest_data = st.sidebar.checkbox("plot_latest_data")

	if plot_latest_data:
		x_label_indices = np.arange(len(states))
		width = 0.3

		fig, axes = plt.subplots(2, 1, figsize=(12, 24))
		plt.suptitle("Statewise covid-19 data on : {}".format(latest_date))

		axes[0].set_title("Confirmed vs Recovered cases")
		axes[0].bar(x_label_indices - (width/2), latest_values.to_numpy()[-3, 2:], width, label="confirmed", color="r")
		axes[0].bar(x_label_indices + (width/2), latest_values.to_numpy()[-2, 2:], width, label="recovered", color="g")
		axes[0].set_xticks(x_label_indices)
		axes[0].set_xticklabels(tuple(states))
		axes[0].legend()
		axes[0].grid()

		axes[1].set_title("Deceased cases")
		axes[1].bar(states, latest_values.to_numpy()[-1, 2:], label="deceased", color="b")
		axes[1].legend()
		axes[1].grid()

		plt.show()
		st.pyplot()


def total():
	st.title("Covid-19 total caseload dashboard")
	df_total = pd.read_csv(csv_weblinks["statewise_total"])

	df_total = df_total[["State", "Confirmed", "Recovered", "Deaths", "Active"]]
	df_total["Mortality_Rate"] = np.around(100 * df_total.Deaths.values / df_total.Confirmed.values, 2)

	st.write(df_total)


modes = {
	"latest_date" : latest_date,
	"total" : total
}


csv_weblinks = {
	"statewise_daily" : "https://api.covid19india.org/csv/latest/state_wise_daily.csv",
	"statewise_total" : "https://api.covid19india.org/csv/latest/state_wise.csv"
}


def main():
	mode = st.sidebar.selectbox("Mode", list(modes.keys()))
	modes[mode]()


if __name__ == "__main__":
	main()