import os
import numpy as np
import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt


def get_plot_last_n_days(data, title, label, color):
	fig, axes = plt.subplots(1, 1, figsize=(8, 8))
	axes.set_title(title)
	axes.bar(np.arange(len(data)), data, label=label, color=color)
	axes.legend()
	axes.grid()

	return fig


def get_plot_all_states(data, states, latest_date=None):
	width = 0.3
	x_label_indices = np.arange(len(states))

	fig, axes = plt.subplots(2, 1, figsize=(12, 24))
	if latest_date is not None:
		plt.suptitle(f"Statewise covid-19 data on : {latest_date}")
	else:
		plt.suptitle(f"Statewise covid-19 data")

	axes[0].set_title("Confirmed vs Recovered cases")
	axes[0].bar(x_label_indices - (width/2), data[-3, :], width, label="confirmed", color="b")
	axes[0].bar(x_label_indices + (width/2), data[-2, :], width, label="recovered", color="g")
	axes[0].set_xticks(x_label_indices)
	axes[0].set_xticklabels(tuple(states))
	axes[0].legend()
	axes[0].grid()

	axes[1].set_title("Deceased cases")
	axes[1].bar(states, data[-1, :], label="deceased", color="r")
	axes[1].legend()
	axes[1].grid()

	return fig


def get_dataframe_read_csv(csv_file):
	df_csv = pd.read_csv(csv_file)

	return df_csv


def infection_latest_date():
	st.title("Covid-19 latest cases dashboard")
	df_daily = get_dataframe_read_csv(csv_weblinks["statewise_daily"])

	df_latest_data = df_daily.tail(3)
	latest_date = df_latest_data.to_numpy()[-1, 0]

	st.write(f"Latest data available from date : {latest_date}")
	st.write(df_latest_data)
	link_statewise_daily = "[Download statewise daily covid-19 caseload csv data]("+csv_weblinks["statewise_daily"]+")"
	st.markdown(link_statewise_daily, unsafe_allow_html=True)

	show_plot_latest_cases = st.sidebar.checkbox("Show plot latest cases", True)

	if show_plot_latest_cases:
		start_column = 3
		all_states = df_daily.columns[start_column:]
		latest_data = df_latest_data.to_numpy()[:, start_column:]

		fig = get_plot_all_states(latest_data, all_states, latest_date)
		fig.show()
		st.pyplot()


def infection_total():
	st.title("Covid-19 total cases dashboard")
	df_total = get_dataframe_read_csv(csv_weblinks["statewise_total"])

	df_total = df_total[["State", "State_code", "Confirmed", "Recovered", "Deaths", "Active"]]
	df_total["Mortality_Rate"] = np.around(100 * df_total.Deaths.to_numpy() / df_total.Confirmed.to_numpy(), 2)

	st.write(df_total)
	link_statewise_total = "[Download statewise total covid-19 caseload csv data]("+csv_weblinks["statewise_total"]+")"
	st.markdown(link_statewise_total, unsafe_allow_html=True)

	show_plot_total_cases = st.sidebar.checkbox("Show plot total cases", True)
	if show_plot_total_cases:
		all_states = df_total.State_code.to_numpy()[1:]
		all_data = df_total.to_numpy()[1:, 2:5].T

		fig = get_plot_all_states(all_data, all_states)
		fig.show()
		st.pyplot()


def infection_last_n_days():
	df_total = get_dataframe_read_csv(csv_weblinks["statewise_total"])
	df_daily = get_dataframe_read_csv(csv_weblinks["statewise_daily"])

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

	df_last_n_days = df_daily.tail(3 * selected_n_days)
	start_date, end_date = df_last_n_days.Date.to_numpy()[0], df_last_n_days.Date.to_numpy()[-1]

	st.title(f"Last {selected_n_days} days for {selected_state} ({selected_state_code}) from {start_date} to {end_date}")

	confirmed_cases = df_last_n_days[selected_state_code].to_numpy()[0::3]
	recovered_cases = df_last_n_days[selected_state_code].to_numpy()[1::3]
	deceased_cases = df_last_n_days[selected_state_code].to_numpy()[2::3]

	show_percentage_change = st.sidebar.checkbox("Show percentage change", True)
	show_plot_confirmed_cases = st.sidebar.checkbox("Show plot confirmed cases", True)
	show_plot_recovered_cases = st.sidebar.checkbox("Show plot recovered cases", True)
	show_plot_deceased_cases = st.sidebar.checkbox("Show plot deceased cases", True)

	if show_percentage_change:
		percentage_change_confirmed_cases = 100 * (confirmed_cases[-1] - confirmed_cases[0]) / confirmed_cases[0]
		percentage_change_deceased_cases = 100 * (deceased_cases[-1] - deceased_cases[0]) / deceased_cases[0]
		st.write(f"Change in confirmed cases in last {selected_n_days} days : {percentage_change_confirmed_cases:.02f} %")
		st.write(f"Change in deceased cases in last {selected_n_days} days : {percentage_change_deceased_cases:.02f} %")

	if show_plot_confirmed_cases:
		fig = get_plot_last_n_days(confirmed_cases, "Confirmed cases", "confirmed", "b")
		fig.show()
		st.pyplot()

	if show_plot_recovered_cases:
		fig = get_plot_last_n_days(recovered_cases, "Recovered cases", "recovered", "g")
		fig.show()
		st.pyplot()

	if show_plot_deceased_cases:
		fig = get_plot_last_n_days(deceased_cases, "Deceased cases", "deceased", "r")
		fig.show()
		st.pyplot()


modes = {
	"infection_total" : infection_total,
	"infection_latest_date" : infection_latest_date,
	"infection_last_n_days" : infection_last_n_days,
}


csv_weblinks = {
	"statewise_daily" : "https://api.covid19india.org/csv/latest/state_wise_daily.csv",
	"statewise_total" : "https://api.covid19india.org/csv/latest/state_wise.csv",
}


def main():
	mode = st.sidebar.selectbox("Mode", list(modes.keys()))
	modes[mode]()


if __name__ == "__main__":
	main()
