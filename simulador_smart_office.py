#!/usr/bin/env python3
# simulador_smart_office.py
# Gera dados simulados para sensores de temperatura (°C), luminosidade (lux) e ocupação (0/1)
# por 7 dias, em janelas de 15 minutos. Salva em smart_office_data.csv (na pasta atual).
import pandas as pd
import numpy as np

def gerar_dados(caminho_csv: str = "smart_office_data.csv", zone: str = "America/Sao_Paulo"):
    end_dt = pd.Timestamp.now(tz=zone).replace(minute=59, second=0, microsecond=0)
    end_dt = (end_dt - pd.Timedelta(days=1)).replace(hour=23, minute=59)
    start_dt = end_dt - pd.Timedelta(days=6, hours=23, minutes=44)
    time_index = pd.date_range(start=start_dt, end=end_dt, freq="15min")

    hours = time_index.hour
    dow = time_index.dayofweek

    day_factor = (np.sin((hours - 6) * np.pi / 12) + 1) / 2
    temp_base = 20 + 6 * day_factor
    temp_noise = np.random.normal(0, 0.6, len(time_index))
    temperature = temp_base + temp_noise

    light_day_curve = (np.sin((hours - 6) * np.pi / 12) + 1) / 2
    is_daylight = (hours >= 6) & (hours <= 18)
    lux = np.where(is_daylight, 50 + light_day_curve * 550, 0)
    lux = np.maximum(0, lux + np.random.normal(0, 15, len(lux)))

    business_hours = (dow < 5) & (hours >= 8) & (hours < 18)
    p_occ = np.where(business_hours, 0.7, 0.05)
    weekend = dow >= 5
    spike_slots = np.random.rand(len(time_index)) < (0.12 * weekend)
    p_occ = np.clip(p_occ + spike_slots * 0.8, 0, 1)
    occupancy = (np.random.rand(len(time_index)) < p_occ).astype(int)

    df_temp = pd.DataFrame({
        "timestamp": time_index,
        "sensor_id": "temp-01",
        "type": "temperatura_c",
        "value": np.round(temperature, 2),
    })
    df_light = pd.DataFrame({
        "timestamp": time_index,
        "sensor_id": "lux-01",
        "type": "luminosidade_lux",
        "value": np.round(lux, 1),
    })
    df_occ = pd.DataFrame({
        "timestamp": time_index,
        "sensor_id": "occ-01",
        "type": "ocupacao_bool",
        "value": occupancy,
    })

    df = pd.concat([df_temp, df_light, df_occ], ignore_index=True).sort_values("timestamp")
    df.to_csv(caminho_csv, index=False)
    return df

if __name__ == "__main__":
    df = gerar_dados("smart_office_data.csv")
    print("Linhas geradas:", len(df))
    print("Período:", df["timestamp"].min(), "->", df["timestamp"].max())
    print(df["type"].value_counts())
