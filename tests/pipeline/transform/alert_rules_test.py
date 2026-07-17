import unittest

import pandas as pd

from pipeline.transform.alert_rules import build_new_admin_risk_overview, generate_alerts


class AlertRulesTest(unittest.TestCase):
    def test_heavy_rain_uses_rolling_24_hour_sum_not_single_hour(self):
        snapshot_at = pd.Timestamp(
            "2026-07-17 00:00:00",
            tz="Asia/Ho_Chi_Minh",
        )
        valid_times = pd.date_range(snapshot_at, periods=24, freq="h")
        forecast = pd.DataFrame(
            {
                "location_id": [1] * 24,
                "snapshot_at": [snapshot_at] * 24,
                "valid_time": valid_times,
                "model": ["open_meteo_best_match"] * 24,
                "temperature_2m": [20.0] * 24,
                "precipitation": [5.0] * 24,
                "wind_speed_10m": [5.0] * 24,
                "wind_gusts_10m": [8.0] * 24,
            }
        )
        locations = pd.DataFrame(
            {
                "location_id": [1],
                "old_admin_unit": ["Xã cũ"],
                "new_admin_unit": ["Xã mới"],
                "province": ["Điện Biên"],
            }
        )

        detail, summary = generate_alerts(forecast, locations)

        rain = detail[detail["hazard_type"] == "heavy_rain"]
        self.assertEqual(len(rain), 1)
        self.assertEqual(rain.iloc[0]["severity"], "danger")
        self.assertEqual(rain.iloc[0]["metric_name"], "rain_24h")
        self.assertEqual(rain.iloc[0]["metric_value"], 120.0)
        self.assertEqual(summary.iloc[0]["new_admin_unit"], "Xã mới")

    def test_cold_alert_uses_complete_daily_mean(self):
        snapshot_at = pd.Timestamp(
            "2026-01-17 00:00:00",
            tz="Asia/Ho_Chi_Minh",
        )
        forecast = pd.DataFrame(
            {
                "location_id": [1] * 24,
                "snapshot_at": [snapshot_at] * 24,
                "valid_time": pd.date_range(
                    snapshot_at,
                    periods=24,
                    freq="h",
                ),
                "model": ["open_meteo_best_match"] * 24,
                "temperature_2m": [12.5] * 24,
                "precipitation": [0.0] * 24,
                "wind_speed_10m": [5.0] * 24,
                "wind_gusts_10m": [8.0] * 24,
            }
        )
        locations = pd.DataFrame(
            {
                "location_id": [1],
                "old_admin_unit": ["Xã cũ"],
                "new_admin_unit": ["Xã mới"],
                "province": ["Điện Biên"],
            }
        )

        detail, _ = generate_alerts(forecast, locations)

        cold = detail[detail["hazard_type"] == "cold"]
        self.assertEqual(len(cold), 1)
        self.assertEqual(cold.iloc[0]["severity"], "danger")
        self.assertEqual(
            cold.iloc[0]["metric_name"],
            "daily_mean_temperature",
        )
        self.assertEqual(cold.iloc[0]["metric_value"], 12.5)

    def test_new_admin_summary_keeps_highest_old_location_risk(self):
        snapshot_at = pd.Timestamp(
            "2026-07-17 00:00:00",
            tz="Asia/Ho_Chi_Minh",
        )
        times = pd.date_range(snapshot_at, periods=24, freq="h")
        forecast = pd.DataFrame(
            {
                "location_id": [1] * 24 + [2] * 24,
                "snapshot_at": [snapshot_at] * 48,
                "valid_time": times.tolist() * 2,
                "model": ["open_meteo_best_match"] * 48,
                "temperature_2m": [20.0] * 48,
                "precipitation": [2.5] * 24 + [5.0] * 24,
                "wind_speed_10m": [5.0] * 48,
                "wind_gusts_10m": [8.0] * 48,
            }
        )
        locations = pd.DataFrame(
            {
                "location_id": [1, 2],
                "old_admin_unit": ["Xã cũ A", "Xã cũ B"],
                "new_admin_unit": ["Xã mới", "Xã mới"],
                "province": ["Điện Biên", "Điện Biên"],
            }
        )

        _, summary = generate_alerts(forecast, locations)

        rain = summary[summary["hazard_type"] == "heavy_rain"]
        self.assertEqual(len(rain), 1)
        self.assertEqual(rain.iloc[0]["severity"], "danger")
        self.assertEqual(rain.iloc[0]["old_admin_unit"], "Xã cũ B")

    def test_three_complete_wet_days_create_monitoring_signal(self):
        snapshot_at = pd.Timestamp(
            "2026-07-17 00:00:00",
            tz="Asia/Ho_Chi_Minh",
        )
        forecast = pd.DataFrame(
            {
                "location_id": [1] * 72,
                "snapshot_at": [snapshot_at] * 72,
                "valid_time": pd.date_range(
                    snapshot_at,
                    periods=72,
                    freq="h",
                ),
                "model": ["open_meteo_best_match"] * 72,
                "temperature_2m": [20.0] * 72,
                "precipitation": [1.0] * 72,
                "wind_speed_10m": [5.0] * 72,
                "wind_gusts_10m": [8.0] * 72,
            }
        )
        locations = pd.DataFrame(
            {
                "location_id": [1],
                "old_admin_unit": ["Xã cũ"],
                "new_admin_unit": ["Xã mới"],
                "province": ["Điện Biên"],
            }
        )

        detail, _ = generate_alerts(forecast, locations)

        prolonged = detail[
            detail["hazard_type"] == "prolonged_rain_signal"
        ]
        self.assertEqual(len(prolonged), 1)
        self.assertEqual(prolonged.iloc[0]["severity"], "warning")
        self.assertEqual(prolonged.iloc[0]["metric_name"], "rain_72h")
        self.assertEqual(prolonged.iloc[0]["metric_value"], 72.0)
        self.assertIn("theo dõi", prolonged.iloc[0]["message_vi"].lower())

    def test_sustained_wind_is_not_confused_with_gust(self):
        snapshot_at = pd.Timestamp(
            "2026-07-17 00:00:00",
            tz="Asia/Ho_Chi_Minh",
        )
        forecast = pd.DataFrame(
            {
                "location_id": [1] * 24,
                "snapshot_at": [snapshot_at] * 24,
                "valid_time": pd.date_range(
                    snapshot_at,
                    periods=24,
                    freq="h",
                ),
                "model": ["open_meteo_best_match"] * 24,
                "temperature_2m": [20.0] * 24,
                "precipitation": [0.0] * 24,
                "wind_speed_10m": [61.0] + [5.0] * 23,
                "wind_gusts_10m": [20.0] * 24,
            }
        )
        locations = pd.DataFrame(
            {
                "location_id": [1],
                "old_admin_unit": ["Xã cũ"],
                "new_admin_unit": ["Xã mới"],
                "province": ["Điện Biên"],
            }
        )

        detail, _ = generate_alerts(forecast, locations)

        wind = detail[detail["hazard_type"] == "strong_wind"]
        self.assertEqual(len(wind), 1)
        self.assertEqual(wind.iloc[0]["metric_name"], "max_wind_speed_10m")
        self.assertEqual(wind.iloc[0]["metric_value"], 61.0)
        self.assertNotIn("gust", wind.iloc[0]["metric_name"])

    def test_wind_gust_has_separate_rule_and_metric(self):
        snapshot_at = pd.Timestamp(
            "2026-07-17 00:00:00",
            tz="Asia/Ho_Chi_Minh",
        )
        forecast = pd.DataFrame(
            {
                "location_id": [1] * 24,
                "snapshot_at": [snapshot_at] * 24,
                "valid_time": pd.date_range(
                    snapshot_at,
                    periods=24,
                    freq="h",
                ),
                "model": ["open_meteo_best_match"] * 24,
                "temperature_2m": [20.0] * 24,
                "precipitation": [0.0] * 24,
                "wind_speed_10m": [5.0] * 24,
                "wind_gusts_10m": [80.0] + [8.0] * 23,
            }
        )
        locations = pd.DataFrame(
            {
                "location_id": [1],
                "old_admin_unit": ["Xã cũ"],
                "new_admin_unit": ["Xã Mường Nhé"],
                "province": ["Điện Biên"],
            }
        )

        detail, _ = generate_alerts(forecast, locations)

        gust = detail[detail["hazard_type"] == "strong_wind_gust"]
        self.assertEqual(len(gust), 1)
        self.assertEqual(gust.iloc[0]["metric_name"], "max_wind_gusts_10m")
        self.assertEqual(gust.iloc[0]["metric_value"], 80.0)

    def test_risk_overview_contains_normal_rows_for_units_without_alerts(self):
        locations = pd.DataFrame(
            {
                "location_id": [1, 2],
                "old_admin_unit": ["Xã cũ A", "Xã cũ B"],
                "new_admin_unit": ["Xã Mường Nhé", "Xã Sín Thầu"],
                "province": ["Điện Biên", "Điện Biên"],
            }
        )
        summary = pd.DataFrame(
            {
                "new_admin_unit": ["Xã Mường Nhé"],
                "severity": ["warning"],
                "severity_rank": [1],
                "hazard_type": ["heavy_rain"],
                "confidence": ["high"],
                "valid_from": [
                    pd.Timestamp(
                        "2026-07-18 00:00:00",
                        tz="Asia/Ho_Chi_Minh",
                    )
                ],
                "valid_to": [
                    pd.Timestamp(
                        "2026-07-18 23:00:00",
                        tz="Asia/Ho_Chi_Minh",
                    )
                ],
            }
        )

        overview = build_new_admin_risk_overview(summary, locations)

        self.assertEqual(len(overview), 45)
        status = overview.set_index("new_admin_unit")["severity"].to_dict()
        self.assertEqual(status["Xã Mường Nhé"], "warning")
        self.assertEqual(status["Xã Sín Thầu"], "normal")
        self.assertEqual(
            (overview["coverage_status"] == "missing_location_data").sum(),
            43,
        )

    def test_normal_weather_returns_typed_empty_alert_frames(self):
        snapshot_at = pd.Timestamp(
            "2026-07-17 00:00:00",
            tz="Asia/Ho_Chi_Minh",
        )
        forecast = pd.DataFrame(
            {
                "location_id": [1] * 24,
                "snapshot_at": [snapshot_at] * 24,
                "valid_time": pd.date_range(
                    snapshot_at,
                    periods=24,
                    freq="h",
                ),
                "model": ["open_meteo_best_match"] * 24,
                "temperature_2m": [20.0] * 24,
                "precipitation": [0.0] * 24,
                "wind_speed_10m": [5.0] * 24,
                "wind_gusts_10m": [8.0] * 24,
            }
        )
        locations = pd.DataFrame(
            {
                "location_id": [1],
                "old_admin_unit": ["Xã cũ"],
                "new_admin_unit": ["Xã Mường Nhé"],
                "province": ["Điện Biên"],
            }
        )

        detail, summary = generate_alerts(forecast, locations)

        self.assertTrue(detail.empty)
        self.assertTrue(summary.empty)
        self.assertIn("hazard_type", detail.columns)
        self.assertEqual(
            str(detail["snapshot_at"].dtype),
            "datetime64[ns, Asia/Ho_Chi_Minh]",
        )


if __name__ == "__main__":
    unittest.main()
