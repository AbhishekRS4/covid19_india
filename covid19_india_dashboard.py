import os
import numpy as np
import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt


def plot_single_bar(data_array, title, label, color):
	fig, axes = plt.subplots(1, 1, figsize=(8, 8))
	axes.set_title(title)
	axes.bar(np.arange(len(data_array)), data_array, label=label, color=color)
	axes.legend()
	axes.grid()
	return fig


def latest_date():
	st.title("Covid-19 latest caseload dashboard")
	df_daily = pd.read_csv(csv_weblinks["statewise_daily"])

	states = df_daily.columns[2:]
	latest_values = df_daily.tail(3)
	latest_date = latest_values.to_numpy()[-1, 0]

	st.write(f"Latest data available from date : {latest_date}")
	st.write(latest_values)

	show_plot_latest_cases = st.sidebar.checkbox("Show plot latest cases")

	if show_plot_latest_cases:
		x_label_indices = np.arange(len(states))
		width = 0.3

		fig, axes = plt.subplots(2, 1, figsize=(12, 24))
		plt.suptitle(f"Statewise covid-19 data on : {latest_date}")

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
	df_total["Mortality_Rate"] = np.around(100 * df_total.Deaths.to_numpy() / df_total.Confirmed.to_numpy(), 2)

	st.write(df_total)


def last_n_days():
	df_total = pd.read_csv(csv_weblinks["statewise_total"])
	df_daily = pd.read_csv(csv_weblinks["statewise_daily"])

	states_list = list(df_total.State.to_numpy())
	states_code = list(df_total.State_code.to_numpy())

	states_mapping_dict = dict()

	for i in range(len(states_list)):
		states_mapping_dict[states_list[i]] = states_code[i]

	min_n_days = 7
	max_n_days = df_daily.shape[0] // 3
	selected_n_days = st.sidebar.number_input(f"Last N days ({min_n_days}-{max_n_days})", \
		min_value=min_n_days, max_value=max_n_days, value=60)
	selected_state = st.sidebar.selectbox("State / Region", list(states_list))
	selected_state_code = states_mapping_dict[selected_state]

	data = df_daily.tail(3 * selected_n_days)
	start_date, end_date = data.Date.to_numpy()[0], data.Date.to_numpy()[-1]

	st.title(f"Last {selected_n_days} days for {selected_state} ({selected_state_code}) from {start_date} to {end_date}")

	confirmed_cases = data[selected_state_code].to_numpy()[::3]
	recovered_cases = data[selected_state_code].to_numpy()[1::3]
	deceased_cases = data[selected_state_code].to_numpy()[2::3]

	show_plot_confirmed_cases = st.sidebar.checkbox("Show plot confirmed cases")
	show_plot_recovered_cases = st.sidebar.checkbox("Show plot recovered cases")
	show_plot_deceased_cases = st.sidebar.checkbox("Show plot deceased cases")

	if show_plot_confirmed_cases:
		fig = plot_single_bar(confirmed_cases, "Confirmed cases", "confirmed", "r")
		fig.show()
		st.pyplot()

	if show_plot_recovered_cases:
		fig = plot_single_bar(recovered_cases, "Recovered cases", "recovered", "g")
		fig.show()
		st.pyplot()

	if show_plot_deceased_cases:
		fig = plot_single_bar(deceased_cases, "Deceased cases", "deceased", "b")
		plt.show()
		st.pyplot()


modes = {
	"total" : total,
	"latest_date" : latest_date,
	"last_n_days" : last_n_days
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