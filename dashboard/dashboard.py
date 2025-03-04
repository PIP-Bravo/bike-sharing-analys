import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st
# sns.set_theme(style='dark')

def create_by_hour_day(df):
    by_hour_day_df = df.groupby(['hour', 'day']).agg({
        'total_user': 'sum'
    }).reset_index()

    by_hour_day_df = by_hour_day_df.reset_index()
    
    return by_hour_day_df

def create_by_weather(df):
    by_weather_df = df.groupby('weather').agg({
        'total_user' : "sum"
    }).reset_index()

    by_weather_df = by_weather_df.reset_index()
    
    return by_weather_df

def create_by_month(df):
    by_month_df = df.groupby('month').agg({
        'total_user' : "sum"
    }).reset_index()

    by_month_df = by_month_df.reset_index()
    
    return by_month_df

# MENYIAPKAN DATAFRAME

day_df = pd.read_csv("dashboard/day.csv")
hour_df = pd.read_csv("dashboard/hour.csv")

day_df.sort_values(by='date',inplace=True)
day_df['date'] = pd.to_datetime(day_df['date']) 
hour_df.sort_values(by='date',inplace=True)
hour_df['date'] = pd.to_datetime(hour_df['date']) 

# MEMBUAT KOMPONEN FILTER

min_date = day_df['date'].min()
max_date = day_df['date'].max()
min_date = hour_df['date'].min()
max_date = hour_df['date'].max()

with st.sidebar:
    # Menambahkan Logo
    st.image("dashboard/Rent.jpeg")

    # Mengambil start_date & end_date dari date_input
    start_date, end_date = st.date_input(
        label="Time Range", 
        min_value=min_date, max_value=max_date, value=[min_date,max_date],
    )

main_df = day_df[(day_df['date'] >= str(start_date)) & (day_df["date"] <= str(end_date))]
main_hour_df = hour_df[(hour_df['date'] >= str(start_date)) & (hour_df["date"] <= str(end_date))]

# Panggil semua fungsi yang telah didefinsikan sebelumnya
by_hour_day_df = create_by_hour_day(main_hour_df)
by_weather_df = create_by_weather(main_df)
by_month_df = create_by_month(main_df)


# MELENGKAPI DASHBOARD DENGAN VISUALISASI DATA
st.header('Bike Rental Analysis Dashboard 🚴‍♂️📊')



# 1. Perbandingan Total User di setiap jam dan setiap harinya

# Definisikan terlebih dahulu urutan hari agar nantinya hari yang ditampilkan terurut dengan baik
day_order = ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday']
by_hour_day_df['day'] = pd.Categorical(by_hour_day_df['day'], categories=day_order, ordered=True)
by_hour_day_df = by_hour_day_df.sort_values('day')

# Deklarasi tampilan 7 tabs
tabs = st.tabs(["All Days"] + day_order)

# Pendefinisian tab pertama untuk analisis keseluruhan semua hari
with tabs[0]:
    st.subheader("Users Trends at Specific Hours")

    fig, ax = plt.subplots(figsize=(12, 6))
    sns.lineplot(
        x='hour',
        y='total_user',
        hue='day',
        data=by_hour_day_df,
        marker='o',
        linewidth=2,
        ax=ax
    )
    
    ax.set_title("Number of Users at Specific Hours and Days", fontsize=16)
    ax.set_xlabel("Hour", fontsize=12)
    ax.set_ylabel("Total User", fontsize=12)
    ax.set_xticks(range(0, 24))
    ax.grid(axis='y', linestyle="--", alpha=0.5)
    ax.legend(title='Day', bbox_to_anchor=(1.05, 1), loc='upper left')
    
    st.pyplot(fig)

# Tab kedua hingga seterusnya berguna untuk menampilkan data pada masing-masing hari
for i, day in enumerate(day_order, start=1):
    with tabs[i]:
        st.subheader(f"User Trends for {day}")
        
        day_df = by_hour_day_df[by_hour_day_df['day'] == day]
        
        fig, ax = plt.subplots(figsize=(12, 6))
        sns.lineplot(
            x='hour',
            y='total_user',
            data=day_df,
            marker='o',
            linewidth=2,
            color='red',
            ax=ax
        )
        
        ax.set_title(f"Number of Users at Specific Hours on {day}", fontsize=16)
        ax.set_xlabel("Hour", fontsize=12)
        ax.set_ylabel("Total User", fontsize=12)
        ax.set_xticks(range(0, 24))
        ax.grid(axis='y', linestyle="--", alpha=0.5)
        
        st.pyplot(fig)



# 2. Perbandingan User teregistrasi dan tidak teregistrasi
st.subheader('Registration Rate Identification')

# Deklarasi 3 kolom yang akan digunakan
col1, col2, col3 = st.columns(3)

# Kolom pertama berisi jumlah total pengguna yang teregistrasi
with col1:
    total_registered = main_df.registered.sum()
    st.metric("Registered User", value=f"{total_registered:,}")

# Kolom kedua berisi jumlah total pengguna yang tidak teregistrasi
with col2:
    total_unregistered = main_df.unregistered.sum()
    st.metric("Unregistered User", value=f"{total_unregistered:,}")

# Kolom ketiga berisi perbandingan antara total pengguna yang teregistrasi dengan yang tidak teregistrasi
with col3:
    differentiation = total_registered - total_unregistered
    if total_unregistered > 0:
        percent = (differentiation / total_unregistered) * 100
    else:
        percent = -((differentiation / total_unregistered) * 100)
    st.metric("Registration Rate", value=f"{differentiation:,}", delta=f"{percent:.2f}%")

# Membuat pie chart untuk memvisualisasikan data yang ditampilkan pada kolom sebelumnya
labels = ['Registered Users', 'Unregistered Users']
sizes = [total_registered, total_unregistered]
colors = ['#4CAF50', '#FF5733']
explode = (0.1, 0)
fig, ax = plt.subplots()
ax.pie(
    sizes,
    labels=labels,
    autopct='%1.1f%%',
    colors=colors,
    explode=explode,
)
st.pyplot(fig)



# 3. Mengidentifikasi jumlah pengguna berdasarkan cuaca
st.subheader('Total of Users Comparison by Weather')

# Deklarasi 3 kolom yang akan digunakan untuk menampilkan jumlah spesifik total user
col1, col2, col3 = st.columns(3)

# Menampilkan jumlah spesifik total pengguna pada cuaca cerah
with col1 :
    clear = by_weather_df[by_weather_df['weather'] == 'Clear']

    if not clear.empty:
        clear_value = clear["total_user"].values[0]
    else:
        clear_value = 0

    st.metric("On Clear Weather", value=f"{clear_value:,}")

# Menampilkan jumlah spesifik total pengguna pada cuaca kabut
with col2 :
    mist = by_weather_df[by_weather_df['weather'] == 'Mist']

    if not mist.empty:
        mist_value = mist["total_user"].values[0]
    else:
        mist_value = 0

    st.metric("On Mist Weather", value=f"{mist_value:,}")

# Menampilkan jumlah spesifik total pengguna pada cuaca hujan ringan
with col3 :
    light_rain = by_weather_df[by_weather_df['weather'] == 'Light rain']

    if not light_rain.empty:
        light_rain_value = light_rain["total_user"].values[0]
    else:
        light_rain_value = 0

    st.metric("On Light Rain Weather", value=f"{light_rain_value:,}")

# Membuat plot
fig, ax = plt.subplots(figsize=(10, 5))

# Mengurutkan data secara Descending
by_weather_df = by_weather_df.sort_values(by="total_user", ascending=False)

# Warna khusus untuk bar dengan nilai tertinggi
colors_ = ["#72BCD4"] + ["#D3D3D3"] * (len(by_weather_df) - 1)

# Membuat bar plot
sns.barplot(
    y="total_user", 
    x="weather",
    data=by_weather_df,
    palette=colors_,
    ax=ax
)

# Styling agar diagram lebih rapi
ax.set_ylim(0, by_weather_df["total_user"].max() * 1.1)
ax.set_title("Total of Users by Weather", fontsize=15)
ax.set_xlabel("Weather", fontsize=12)
ax.set_ylabel("Total Users", fontsize=12)
ax.ticklabel_format(style='plain', axis='y')
st.pyplot(fig)



# 4. Mengidentifikasi jumlah pengguna berdasarkan bulan
st.subheader('Total of Users Comparison by Month')

# Mengurutkan data berdasarkan urutan bulan
month_order = ['January', 'February', 'March', 'April', 'May', 'June', 
               'July', 'August', 'September', 'October', 'November', 'December']
by_month_df['month'] = pd.Categorical(by_month_df['month'], categories=month_order, ordered=True)
by_month_df = by_month_df.sort_values('month')

# Membuat plot
fig, ax = plt.subplots(figsize=(10, 5))
ax.plot(
    by_month_df['month'],
    by_month_df['total_user'],
    marker='o',
    linewidth=2,
    color="#72BCD4"
)
ax.set_title("Total User on Each Month", fontsize=20)
ax.set_xlabel("Month", fontsize=12)
ax.set_ylabel("Total User", fontsize=12)
ax.set_xticklabels(by_month_df['month'], rotation=45, fontsize=10)
ax.set_yticklabels(ax.get_yticks(), fontsize=10)
st.pyplot(fig)


# Terima kasih Dicoding.
st.caption('Made with love by : J.Alfons')