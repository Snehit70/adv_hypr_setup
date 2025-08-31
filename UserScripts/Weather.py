#!/usr/bin/env python3
# /* ---- 💫 https://github.com/JaKooLit 💫 ---- */
# Reimplemented weather module using Open-Meteo (no scraping, no pyquery)
# Compatible with Waybar custom/weather JSON and existing CSS classes

import json
import os
import sys
from typing import Dict, Tuple

import requests


def safe_get(d: dict, path: Tuple):
    cur = d
    for key in path:
        if not isinstance(cur, dict) or key not in cur:
            return None
        cur = cur[key]
    return cur


def get_location() -> Tuple[float, float, str]:
    try:
        r = requests.get("https://ipinfo.io", timeout=4)
        r.raise_for_status()
        data = r.json()
        lat_str, lon_str = (data.get("loc") or "0,0").split(",")
        city = data.get("city") or ""
        return float(lat_str), float(lon_str), city
    except Exception:
        # Default fallback: 0,0
        return 0.0, 0.0, ""


def map_weather_code_to_class_and_icon(code: int, is_day: int) -> Tuple[str, str, str]:
    # CSS classes expected by your styles: sunnyDay, clearNight, cloudyFoggyDay, cloudyFoggyNight,
    # rainyDay, rainyNight, snowyIcyDay, snowyIcyNight, severe, default
    # Nerd Font icons consistent with previous script
    is_daytime = is_day == 1

    def pick(day_icon: str, night_icon: str, day_class: str, night_class: str):
        if is_daytime:
            return day_class, day_icon, "Day"
        return night_class, night_icon, "Night"

    # Open-Meteo weather codes mapping
    # https://open-meteo.com/en/docs#latitude=52.52&longitude=13.41&hourly=weathercode
    if code == 0:
        cls, icon, _ = pick("󰖙", "󰖔", "sunnyDay", "clearNight")
        desc = "Clear sky"
        return cls, icon, desc
    if code in (1, 2, 3):
        cls, icon, part = pick("", "", "cloudyFoggyDay", "cloudyFoggyNight")
        desc = {1: f"Mainly clear {part}", 2: f"Partly cloudy {part}", 3: f"Overcast {part}"}[code]
        return cls, icon, desc
    if code in (45, 48):
        cls, icon, _ = pick("", "", "cloudyFoggyDay", "cloudyFoggyNight")
        return cls, icon, "Fog"
    if code in (51, 53, 55, 56, 57):
        cls, icon, _ = pick("", "", "rainyDay", "rainyNight")
        return cls, icon, "Drizzle"
    if code in (61, 63, 65, 66, 67, 80, 81, 82):
        cls, icon, _ = pick("", "", "rainyDay", "rainyNight")
        return cls, icon, "Rain"
    if code in (71, 73, 75, 77, 85, 86):
        cls, icon, _ = pick("", "", "snowyIcyDay", "snowyIcyNight")
        return cls, icon, "Snow"
    if code in (95, 96, 97, 99):
        # 95 thunderstorm, 96-99 with hail
        return "severe", "", "Thunderstorm"

    return "default", "", "Unknown"


def build_tooltip(temp: str, icon: str, status: str, feels_like: str, tmin: str, tmax: str,
                   wind_kmh: str, humidity: str, visibility_km: str, precip_summary: str) -> str:
    temp_min_max = f"  {tmin}\t\t  {tmax}"
    wind_text = f"  {wind_kmh} km/h"
    humidity_text = f"  {humidity}%"
    visibility_text = f"  {visibility_km} km" if visibility_km else ""
    prediction = f"\n\n (hourly) {precip_summary}" if precip_summary else ""
    return str.format(
        "\t\t{}\t\t\n{}\n{}\n{}\n\n{}\n{}\t{}\n{}{}",
        f'<span size="xx-large">{temp}</span>',
        f"<big> {icon}</big>",
        f"<b>{status}</b>",
        f"<small>Feels like {feels_like}</small>",
        f"<b>{temp_min_max}</b>",
        wind_text,
        humidity_text,
        visibility_text,
        prediction,
    )


def main():
    latitude, longitude, city = get_location()

    try:
        params = {
            "latitude": latitude,
            "longitude": longitude,
            "current": ",".join([
                "temperature_2m",
                "apparent_temperature",
                "weather_code",
                "wind_speed_10m",
                "is_day",
            ]),
            "hourly": ",".join([
                "precipitation_probability",
                "visibility",
                "relative_humidity_2m",
            ]),
            "daily": ",".join([
                "temperature_2m_max",
                "temperature_2m_min",
            ]),
            "timezone": "auto",
        }
        r = requests.get("https://api.open-meteo.com/v1/forecast", params=params, timeout=6)
        r.raise_for_status()
        data = r.json()

        cur = data.get("current") or {}
        hourly = data.get("hourly") or {}
        daily = data.get("daily") or {}

        temp_c = safe_get(cur, ("temperature_2m",))
        apparent_c = safe_get(cur, ("apparent_temperature",))
        code = int(safe_get(cur, ("weather_code",)) or 0)
        is_day = int(safe_get(cur, ("is_day",)) or 1)
        wind_kmh = safe_get(cur, ("wind_speed_10m",))

        # Hourly values are arrays; pick next few entries
        precip_probs = hourly.get("precipitation_probability") or []
        humidity_vals = hourly.get("relative_humidity_2m") or []
        visibility_vals = hourly.get("visibility") or []

        # Next 5 hours precipitation summary as e.g. "50% 20% 10% 0% 0%"
        precip_summary = " ".join([f"{p}%" for p in (precip_probs[:5] or []) if p is not None])

        # Use current humidity/visibility when available
        humidity = None
        if humidity_vals:
            # Use first which corresponds to current hour
            humidity = humidity_vals[0]
        visibility_km = None
        if visibility_vals:
            visibility_km = round((visibility_vals[0] or 0) / 1000.0, 2)

        # Daily min/max (today)
        tmin = None
        tmax = None
        if (daily.get("temperature_2m_min") and daily.get("temperature_2m_max")):
            tmin = daily["temperature_2m_min"][0]
            tmax = daily["temperature_2m_max"][0]

        # Map to icon/class/phrase
        css_class, icon, phrase = map_weather_code_to_class_and_icon(code, is_day)
        status = phrase

        # Compose strings with units
        temp = f"{int(round(temp_c))}°" if isinstance(temp_c, (int, float)) else "--"
        feels = f"{int(round(apparent_c))}°" if isinstance(apparent_c, (int, float)) else "--"
        tmin_s = f"{int(round(tmin))}°" if isinstance(tmin, (int, float)) else "--"
        tmax_s = f"{int(round(tmax))}°" if isinstance(tmax, (int, float)) else "--"
        wind_s = f"{int(round(wind_kmh))}" if isinstance(wind_kmh, (int, float)) else "--"
        humidity_s = f"{int(round(humidity))}" if isinstance(humidity, (int, float)) else "--"
        visibility_s = f"{visibility_km}" if isinstance(visibility_km, (int, float)) else ""

        tooltip_text = build_tooltip(
            temp=temp,
            icon=icon,
            status=status,
            feels_like=feels,
            tmin=tmin_s,
            tmax=tmax_s,
            wind_kmh=wind_s,
            humidity=humidity_s,
            visibility_km=visibility_s,
            precip_summary=precip_summary,
        )

        out_data = {
            "text": f"{icon}  {temp}",
            "alt": status if city == "" else f"{status} - {city}",
            "tooltip": tooltip_text,
            "class": css_class,
        }
        print(json.dumps(out_data))

        # Write simple cache for other scripts/tooltips
        simple_weather = (
            f"{icon}  {status}\n"
            + f"  {temp} (Feels {feels})\n"
            + f"  {wind_s} km/h \n"
            + f"  {humidity_s}% \n"
            + (f"  {visibility_s} km\n" if visibility_s else "")
        )
        try:
            with open(os.path.expanduser("~/.cache/.weather_cache"), "w") as f:
                f.write(simple_weather)
        except Exception:
            pass

    except Exception as e:
        # Always output something so Waybar keeps the module visible
        fallback = {
            "text": "  N/A",
            "alt": "Weather unavailable",
            "tooltip": f"Weather unavailable: {type(e).__name__}",
            "class": "default",
        }
        print(json.dumps(fallback))


if __name__ == "__main__":
    main()
