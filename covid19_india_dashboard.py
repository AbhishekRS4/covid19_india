import os
import numpy as np
import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt
from matplotlib import cm


def get_line_chart_single(data, title, label, color, marker="o"):
	fig, axes = plt.subplots(1, 1, figsize=(8, 8))
	axes.set_title(title)
	axes.plot(data, label=label, color=color, marker=marker, linestyle="dashed")
	axes.legend()
	axes.grid()

	return fig


def get_bar_chart_single(data, title, label, color):
	fig, axes = plt.subplots(1, 1, figsize=(8, 8))
	axes.set_title(title)
	axes.bar(np.arange(len(data)), data, label=label, color=color)
	axes.legend()
	axes.grid()

	return fig


def get_bar_chart_multi(data, states, latest_date=None):
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


def get_pie_chart_multi_categories(sizes, labels, plot_title, show_percent=False, color_offsets=31, color_offsets_2=101):
	total_values = len(sizes) * 4
	colors = np.arange(0, total_values, 1) / total_values
	colors = np.random.permutation(colors)
	colors = colors.reshape(-1, 4)

	fig = plt.figure(figsize=(12, 12))
	patches, texts = plt.pie(sizes, colors=colors, startangle=90)
	plt.axis("equal")
	plt.title(plot_title)

	if show_percent:
		percent = 100. * sizes / sizes.sum()
		labels = [f"{i} - {j:1.2f} %" for i, j in zip(labels, percent)]
	else:
	    labels = [f"{i} - {j}" for i, j in zip(labels, sizes)]

	sort_legend = True
	if sort_legend:
		patches, labels, dummy = zip(*sorted(zip(patches, labels, sizes), key=lambda labels: labels[2], reverse=True))

	plt.legend(patches, labels, loc="best", fontsize=8)

	return fig


def get_dataframe_read_csv(csv_file, usecols=None):
	df_csv = pd.read_csv(csv_file, usecols=usecols)

	return df_csv


def infection_latest_date():
	st.title("Covid-19 latest cases dashboard")
	df_infection_state_daily = get_dataframe_read_csv(csv_weblinks["statewise_daily"])

	df_latest_data = df_infection_state_daily.tail(3)
	latest_date = df_latest_data.to_numpy()[-1, 1]

	st.write(f"Latest data available from date : {latest_date}")
	st.write(df_latest_data)
	link_statewise_daily = "[Download statewise daily covid-19 caseload csv data]("+csv_weblinks["statewise_daily"]+")"
	st.markdown(link_statewise_daily, unsafe_allow_html=True)

	show_plot_latest_cases = st.sidebar.checkbox("Show plot latest cases", True)

	if show_plot_latest_cases:
		start_column = 3
		states_list = df_infection_state_daily.columns[start_column:]
		latest_data = df_latest_data.to_numpy()[:, start_column:]

		fig = get_bar_chart_multi(latest_data, states_list, latest_date)
		fig.show()
		st.pyplot()


def infection_total():
	st.title("Covid-19 total cases dashboard")
	df_infection_state_total = get_dataframe_read_csv(csv_weblinks["statewise_total"])

	df_infection_state_total = df_infection_state_total[["State", "State_code", "Confirmed", "Recovered", "Deaths", "Active"]]
	df_infection_state_total["Mortality_Rate"] = np.around(100 * df_infection_state_total.Deaths.to_numpy() / df_infection_state_total.Confirmed.to_numpy(), 2)

	st.write(df_infection_state_total)
	link_statewise_total = "[Download statewise total covid-19 caseload csv data]("+csv_weblinks["statewise_total"]+")"
	st.markdown(link_statewise_total, unsafe_allow_html=True)

	show_plot_total_cases = st.sidebar.checkbox("Show plot total cases", True)
	if show_plot_total_cases:
		states_list = df_infection_state_total.State_code.to_numpy()[1:]
		all_data = df_infection_state_total.to_numpy()[1:, 2:5].T

		fig = get_bar_chart_multi(all_data, states_list)
		fig.show()
		st.pyplot()


def infection_last_n_days():
	df_infection_state_total = get_dataframe_read_csv(csv_weblinks["statewise_total"])
	df_infection_state_daily = get_dataframe_read_csv(csv_weblinks["statewise_daily"])

	states_list = list(df_infection_state_total.State.to_numpy())
	states_code = list(df_infection_state_total.State_code.to_numpy())

	states_mapping_dict = dict()

	for i in range(len(states_list)):
		states_mapping_dict[states_list[i]] = states_code[i]

	min_n_days = 7
	max_n_days = df_infection_state_daily.shape[0] // 3
	selected_n_days = st.sidebar.number_input(f"Last N days ({min_n_days}-{max_n_days})", \
		min_value=min_n_days, max_value=max_n_days, value=60)
	selected_state = st.sidebar.selectbox("State / Region", list(states_list))
	selected_state_code = states_mapping_dict[selected_state]

	df_last_n_days = df_infection_state_daily.tail(3 * selected_n_days)
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
		fig = get_bar_chart_single(confirmed_cases, f"Confirmed cases in {selected_state} for last {selected_n_days} days", "confirmed", "b")
		fig.show()
		st.pyplot()

	if show_plot_recovered_cases:
		fig = get_bar_chart_single(recovered_cases, f"Recovered cases in {selected_state} for last {selected_n_days} days", "recovered", "g")
		fig.show()
		st.pyplot()

	if show_plot_deceased_cases:
		fig = get_bar_chart_single(deceased_cases, f"Deceased cases in {selected_state} for last {selected_n_days} days", "deceased", "r")
		fig.show()
		st.pyplot()


def infection_rate():
	df_positivity = get_dataframe_read_csv(csv_weblinks["infection_statewise_daily"],\
		usecols=["Date", "State", "Confirmed", "Deceased", "Tested"])
	df_positivity = df_positivity.dropna()

	states_list = np.unique(df_positivity["State"].values)
	selected_state = st.sidebar.selectbox("State / region", states_list, 13)
	st.title("Infection rate")
	st.header(f"Selected state / region : {selected_state}")

	df_positivity_state = df_positivity[df_positivity["State"] == selected_state]
	positive_cases_cum = df_positivity_state.Confirmed.values
	deceased_cases_cum = df_positivity_state.Deceased.values
	total_tested_cum = df_positivity_state.Tested.values

	positive_cases_daily = np.hstack((positive_cases_cum[0], np.diff(positive_cases_cum)))
	deceased_cases_daily = np.hstack((deceased_cases_cum[0], np.diff(deceased_cases_cum)))
	total_tested_daily = np.hstack((total_tested_cum[0], np.diff(total_tested_cum)))

	rate_mortality = np.around(100 * np.divide(deceased_cases_cum, positive_cases_cum), 2)
	st.write(f"Total mortality rate : {rate_mortality[-1]} %")

	rate_positivity = np.around(100 * np.divide(positive_cases_daily, total_tested_daily), 2)
	rate_positivity = rate_positivity[np.isfinite(rate_positivity)]

	min_n_days = 7
	max_n_days = len(rate_positivity)
	selected_n_days = st.sidebar.number_input(f"Last N days ({min_n_days}-{max_n_days})",\
		min_value=min_n_days, max_value=max_n_days, value=60)
	fig = get_line_chart_single(rate_positivity[(max_n_days-selected_n_days):],\
		f"Positivity rate for {selected_state} in last {selected_n_days} days", "positivity_rate", "r")
	fig.show()
	st.pyplot()


def preprocess_vaccine_doses_df(df_vaccine_doses):
	df_vaccine_doses = df_vaccine_doses.set_index("State").T
	df_vaccine_doses = df_vaccine_doses.reset_index()
	df_vaccine_doses = df_vaccine_doses.rename(columns={"index": "Date"})
	df_vaccine_doses = df_vaccine_doses.dropna()
	return df_vaccine_doses


def vaccine_doses_daily():
	df_vaccine_doses = get_dataframe_read_csv(csv_weblinks["vaccine_doses_daily"])
	df_vaccine_doses = preprocess_vaccine_doses_df(df_vaccine_doses)
	dates_list = df_vaccine_doses["Date"].values
	st.title(f"Vaccine doses administered daily from {dates_list[0]} to {dates_list[-1]}")

	states_list = list(df_vaccine_doses.columns[1:])
	selected_state = st.sidebar.selectbox("State / Region", states_list, len(states_list) - 1)

	st.header(f"Selected state / region : {selected_state}")
	vaccine_doses_cumulative_array = df_vaccine_doses[selected_state].values
	vaccine_doses_daily_array = np.hstack((vaccine_doses_cumulative_array[0], np.diff(vaccine_doses_cumulative_array)))

	fig = get_bar_chart_single(vaccine_doses_daily_array, f"Vaccine doses administered in {selected_state}", "vaccine_doses_administered", "g")
	fig.show()
	st.pyplot()


def vaccine_doses_total():
	df_vaccine_doses = get_dataframe_read_csv(csv_weblinks["vaccine_doses_daily"])
	df_vaccine_doses = preprocess_vaccine_doses_df(df_vaccine_doses)
	dates_list = df_vaccine_doses["Date"].values

	st.title(f"Statewise distribution of total vaccine doses administered")
	show_percent = st.sidebar.checkbox("Show percentage", True)

	states_list = df_vaccine_doses.columns[1:].values
	vaccine_doses_all_states_array = df_vaccine_doses.iloc[-1].values[1:].astype(np.int32)

	link_vaccine_doses_total = "[Download statewise total administered vaccine doses csv data]("+csv_weblinks["vaccine_doses_daily"]+")"
	st.markdown(link_vaccine_doses_total, unsafe_allow_html=True)

	fig = get_pie_chart_multi_categories(vaccine_doses_all_states_array[:-1], states_list[:-1], \
		"Distribution of total vaccine doses administered by states", show_percent)
	fig.show()
	st.pyplot()


modes = {
	"infection_total" : infection_total,
	"infection_latest_date" : infection_latest_date,
	"infection_last_n_days" : infection_last_n_days,
	"infection_rate" : infection_rate,
	"vaccine_doses_daily" : vaccine_doses_daily,
	"vaccine_doses_total" : vaccine_doses_total,
}


csv_weblinks = {
	"statewise_daily" : "https://api.covid19india.org/csv/latest/state_wise_daily.csv",
	"statewise_total" : "https://api.covid19india.org/csv/latest/state_wise.csv",
	"vaccine_doses_daily" : "http://api.covid19india.org/csv/latest/vaccine_doses_statewise.csv",
	"infection_statewise_daily" : "https://api.covid19india.org/csv/latest/states.csv",
}


def main():
	mode = st.sidebar.selectbox("Mode", list(modes.keys()))
	modes[mode]()


if __name__ == "__main__":
	main()
