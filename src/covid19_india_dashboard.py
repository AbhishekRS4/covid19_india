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
    st.title("Covid-19: latest cases dashboard")
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
        st.pyplot(fig)
    st.markdown("_Source of data - [covid19india.org](https://www.covid19india.org)_")


def infection_total():
    st.title("Covid-19: total cases dashboard")
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
        st.pyplot(fig)
    st.markdown("_Source of data - [covid19india.org](https://www.covid19india.org)_")


def infection_last_n_days():
    df_infection_state_total = get_dataframe_read_csv(csv_weblinks["statewise_total"])
    df_infection_state_daily = get_dataframe_read_csv(csv_weblinks["statewise_daily"])

    states_list = df_infection_state_total.State.to_numpy()
    states_code = df_infection_state_total.State_code.to_numpy()

    states_mapping_dict = dict()

    for i in range(len(states_list)):
        states_mapping_dict[states_list[i]] = states_code[i]

    min_n_days = 7
    max_n_days = df_infection_state_daily.shape[0] // 3
    selected_state = st.sidebar.selectbox("State / region", states_list)
    selected_n_days = st.sidebar.number_input(f"Last N days ({min_n_days}-{max_n_days})", \
        min_value=min_n_days, max_value=max_n_days, value=60)
    selected_state_code = states_mapping_dict[selected_state]

    df_last_n_days = df_infection_state_daily.tail(3 * selected_n_days)
    start_date, end_date = df_last_n_days.Date_YMD.to_numpy()[0], df_last_n_days.Date_YMD.to_numpy()[-1]

    st.title(f"Covid-19: data for last {selected_n_days} days for {selected_state} ({selected_state_code}) from {start_date} to {end_date}")

    confirmed_cases = df_last_n_days[selected_state_code].to_numpy()[0::3]
    recovered_cases = df_last_n_days[selected_state_code].to_numpy()[1::3]
    deceased_cases = df_last_n_days[selected_state_code].to_numpy()[2::3]

    show_plot_confirmed_cases = st.sidebar.checkbox("Show plot confirmed cases", True)
    show_plot_recovered_cases = st.sidebar.checkbox("Show plot recovered cases", True)
    show_plot_deceased_cases = st.sidebar.checkbox("Show plot deceased cases", True)

    if show_plot_confirmed_cases:
        fig_c = get_bar_chart_single(confirmed_cases, f"Confirmed cases in {selected_state} for last {selected_n_days} days", "confirmed", "b")
        st.pyplot(fig_c)

    if show_plot_recovered_cases:
        fig_r = get_bar_chart_single(recovered_cases, f"Recovered cases in {selected_state} for last {selected_n_days} days", "recovered", "g")
        st.pyplot(fig_r)

    if show_plot_deceased_cases:
        fig_d = get_bar_chart_single(deceased_cases, f"Deceased cases in {selected_state} for last {selected_n_days} days", "deceased", "r")
        st.pyplot(fig_d)
    st.markdown("_Source of data - [covid19india.org](https://www.covid19india.org)_")


def infection_last_n_days_districtwise():
    df_infection_district_daily = get_dataframe_read_csv(csv_weblinks["infection_districtwise_daily"],
        usecols=["Date", "State", "District", "Confirmed", "Recovered", "Deceased"])

    states_list = np.unique(df_infection_district_daily.State.to_numpy())
    selected_state = st.sidebar.selectbox("State / region", states_list)
    df_state_daily = df_infection_district_daily[df_infection_district_daily["State"] == selected_state]

    districts_list = np.unique(df_state_daily.District.to_numpy())
    selected_district = st.sidebar.selectbox("District", districts_list)
    df_district_daily = df_state_daily[df_state_daily["District"] == selected_district]

    confirmed_cases_cum = df_district_daily.Confirmed.to_numpy()
    recovered_cases_cum = df_district_daily.Recovered.to_numpy()
    deceased_cases_cum = df_district_daily.Deceased.to_numpy()

    confirmed_cases_daily = np.hstack((confirmed_cases_cum[0], np.diff(confirmed_cases_cum)))
    recovered_cases_daily = np.hstack((recovered_cases_cum[0], np.diff(recovered_cases_cum)))
    deceased_cases_daily = np.hstack((deceased_cases_cum[0], np.diff(deceased_cases_cum)))

    min_n_days = 7
    max_n_days = confirmed_cases_daily.shape[0]
    all_dates = df_district_daily.Date.to_numpy()

    selected_n_days = st.sidebar.number_input(f"Last N days ({min_n_days}-{max_n_days})", \
        min_value=min_n_days, max_value=max_n_days, value=60)

    st.title(f"Covid-19: data for last {selected_n_days} days for {selected_district}, {selected_state} \
        from {all_dates[-selected_n_days]} to {all_dates[-1]}")

    show_plot_confirmed_cases = st.sidebar.checkbox("Show plot confirmed cases", True)
    show_plot_recovered_cases = st.sidebar.checkbox("Show plot recovered cases", True)
    show_plot_deceased_cases = st.sidebar.checkbox("Show plot deceased cases", True)

    if show_plot_confirmed_cases:
        fig_c = get_bar_chart_single(confirmed_cases_daily[(max_n_days-selected_n_days):], \
            f"Confirmed cases in {selected_district}, {selected_state} for last {selected_n_days} days", \
            "confirmed", "b")
        st.pyplot(fig_c)

    if show_plot_recovered_cases:
        fig_r = get_bar_chart_single(recovered_cases_daily[(max_n_days-selected_n_days):], \
            f"Recovered cases in {selected_district}, {selected_state} for last {selected_n_days} days", \
            "recovered", "g")
        st.pyplot(fig_r)

    if show_plot_deceased_cases:
        fig_d = get_bar_chart_single(deceased_cases_daily[(max_n_days-selected_n_days):], \
            f"Deceased cases in {selected_district}, {selected_state} for last {selected_n_days} days", \
            "deceased", "r")
        st.pyplot(fig_d)

    st.markdown("_Source of data - [covid19india.org](https://www.covid19india.org)_")


def infection_rate():
    df_positivity = get_dataframe_read_csv(csv_weblinks["infection_statewise_daily"],\
        usecols=["Date", "State", "Confirmed", "Deceased", "Tested"])
    df_positivity = df_positivity.dropna()

    states_list = np.unique(df_positivity.State.to_numpy())
    selected_state = st.sidebar.selectbox("State / region", states_list, 13)

    df_positivity_state = df_positivity[df_positivity["State"] == selected_state]
    positive_cases_cum = df_positivity_state.Confirmed.to_numpy()
    deceased_cases_cum = df_positivity_state.Deceased.to_numpy()
    total_tested_cum = df_positivity_state.Tested.to_numpy()

    positive_cases_daily = np.hstack((positive_cases_cum[0], np.diff(positive_cases_cum)))
    deceased_cases_daily = np.hstack((deceased_cases_cum[0], np.diff(deceased_cases_cum)))
    total_tested_daily = np.hstack((total_tested_cum[0], np.diff(total_tested_cum)))

    rate_mortality = np.around(100 * np.divide(deceased_cases_cum, positive_cases_cum), 2)
    rate_positivity = np.around(100 * np.divide(positive_cases_daily, total_tested_daily), 2)
    rate_positivity = rate_positivity[np.isfinite(rate_positivity)]

    min_n_days = 7
    max_n_days = len(rate_positivity)
    all_dates = df_positivity_state.Date.to_numpy()
    selected_n_days = st.sidebar.number_input(f"Last N days ({min_n_days}-{max_n_days})",\
        min_value=min_n_days, max_value=max_n_days, value=60)
    st.title(f"Covid-19: infection rates for {selected_state} from {all_dates[-selected_n_days]} to {all_dates[-1]}")
    st.write(f"Mortality rate in {selected_state} : {rate_mortality[-1]} %")
    fig_1 = get_line_chart_single(rate_positivity[(max_n_days-selected_n_days):],\
        f"Positivity rates in {selected_state} in last {selected_n_days} days", "positivity_rates", "r")
    st.pyplot(fig_1)

    fig_2 = get_line_chart_single(total_tested_daily[(len(total_tested_daily)-selected_n_days):],\
        f"Total tests in {selected_state} in last {selected_n_days} days", "tests_daily", "b")
    st.pyplot(fig_2)
    st.markdown("_Source of data - [covid19india.org](https://www.covid19india.org)_")


def preprocess_vaccine_doses_df(df_vaccine_doses):
    df_vaccine_doses = df_vaccine_doses.set_index("State").T
    df_vaccine_doses = df_vaccine_doses.reset_index()
    df_vaccine_doses = df_vaccine_doses.rename(columns={"index": "Date"})
    df_vaccine_doses = df_vaccine_doses.dropna()
    return df_vaccine_doses


def vaccine_doses_daily():
    df_vaccine_doses = get_dataframe_read_csv(csv_weblinks["vaccine_doses_daily"])
    df_vaccine_doses = preprocess_vaccine_doses_df(df_vaccine_doses)
    dates_list = df_vaccine_doses.Date.to_numpy()
    st.title(f"Covid-19: vaccine doses administered daily from {dates_list[0]} to {dates_list[-1]}")

    states_list = df_vaccine_doses.columns[1:].to_numpy()
    selected_state = st.sidebar.selectbox("State / Region", states_list, len(states_list) - 1)

    vaccine_doses_cumulative_array = df_vaccine_doses[selected_state].to_numpy().astype(np.int32)
    st.header(f"Overall vaccine doses administered in {selected_state} : {vaccine_doses_cumulative_array[-1]} \
        ({vaccine_doses_cumulative_array[-1]/10**6} Million)")
    vaccine_doses_daily_array = np.hstack((vaccine_doses_cumulative_array[0], np.diff(vaccine_doses_cumulative_array)))

    fig = get_bar_chart_single(vaccine_doses_daily_array, f"Vaccine doses administered in {selected_state}", "vaccine_doses_administered", "g")
    st.pyplot(fig)
    st.markdown("_Source of data - [covid19india.org](https://www.covid19india.org)_")


def vaccine_doses_total():
    df_vaccine_doses = get_dataframe_read_csv(csv_weblinks["vaccine_doses_daily"])
    df_vaccine_doses = preprocess_vaccine_doses_df(df_vaccine_doses)
    dates_list = df_vaccine_doses.Date.to_numpy()

    st.title(f"Covid-19: statewise distribution of total vaccine doses administered")
    show_percent = st.sidebar.checkbox("Show percentage", True)

    states_list = df_vaccine_doses.columns[1:-1].to_numpy()
    vaccine_doses_all_states_array = df_vaccine_doses.iloc[-1].to_numpy()[1:-1].astype(np.int32)
    total_vaccine_doses = np.sum(vaccine_doses_all_states_array)
    st.header(f"Total vaccine doses administered in India : {total_vaccine_doses} ({total_vaccine_doses/10**6} Million)")

    link_vaccine_doses_total = "[Download statewise total administered vaccine doses csv data]("+csv_weblinks["vaccine_doses_daily"]+")"
    st.markdown(link_vaccine_doses_total, unsafe_allow_html=True)

    fig = get_pie_chart_multi_categories(vaccine_doses_all_states_array, states_list, \
        "Distribution of total vaccine doses administered by states", show_percent)
    st.pyplot(fig)
    st.markdown("_Source of data - [covid19india.org](https://www.covid19india.org)_")


def developer_info():
    st.title("Developer info")
    st.markdown("_Developer - Abhishek R. S._")
    st.markdown("_Github - [github.com/AbhishekRS4](https://github.com/AbhishekRS4)_")
    st.markdown("_Source of data - [covid19india.org](https://www.covid19india.org)_")


modes = {
    "Total statewise" : infection_total,
    "Latest date statewise" : infection_latest_date,
    "Last N days statewise" : infection_last_n_days,
    "Last N days districtwise" : infection_last_n_days_districtwise,
    "Infection rates statewise" : infection_rate,
    "Vaccine doses daily" : vaccine_doses_daily,
    "Vaccine doses total" : vaccine_doses_total,
    "Developer info" : developer_info,
}


csv_weblinks = {
    "statewise_daily" : "https://api.covid19india.org/csv/latest/state_wise_daily.csv",
    "statewise_total" : "https://api.covid19india.org/csv/latest/state_wise.csv",
    "vaccine_doses_daily" : "http://api.covid19india.org/csv/latest/vaccine_doses_statewise.csv",
    "infection_statewise_daily" : "https://api.covid19india.org/csv/latest/states.csv",
    "infection_districtwise_daily" : "https://api.covid19india.org/csv/latest/districts.csv",
}


def main():
    mode = st.sidebar.selectbox("Mode", list(modes.keys()))
    modes[mode]()


if __name__ == "__main__":
    main()
