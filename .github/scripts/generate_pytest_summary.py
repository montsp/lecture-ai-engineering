import json
import os

BASE_DIR = "day5/演習3"
REPORT_FILE = os.path.join(BASE_DIR, "report.json")
REPORT_VALUES_DIR = os.path.join(BASE_DIR, "test_results")
ACCURACY_REPORT_PATH = os.path.join(REPORT_VALUES_DIR, "accuracy_report.txt")
INFERENCE_TIME_REPORT_PATH = os.path.join(REPORT_VALUES_DIR, "inference_time_report.txt")

def read_metric_from_file(file_path):
    """指定されたファイルからメトリクスを読み込むヘルパー関数"""
    if os.path.exists(file_path):
        try:
            with open(file_path, 'r') as f:
                return f.read().strip()
        except (ValueError, IOError):
            return "N/A (Read Error)"
    return "N/A"


def generate_pytest_summary():
    report_file = REPORT_FILE
    summary_file = os.environ.get('GITHUB_STEP_SUMMARY')
    github_repository = os.environ.get('GITHUB_REPOSITORY')
    github_run_id = os.environ.get('GITHUB_RUN_ID')

    if not summary_file:
        print("GITHUB_STEP_SUMMARY environment variable is not set. Cannot write summary.")
        return

    try:
        with open(report_file, 'r') as f:
            report_data = json.load(f)
    except FileNotFoundError:
        print(f"Error: {report_file} not found. Skipping summary generation.")
        with open(summary_file, 'a') as f:
            f.write("### Pytest 検証結果サマリー\n\n")
            f.write("pytestレポートファイルが見つかりませんでした。\n")
        return
    except json.JSONDecodeError:
        print(f"Error: Could not decode JSON from {report_file}. Skipping summary generation.")
        with open(summary_file, 'a') as f:
            f.write("### Pytest 検証結果サマリー\n\n")
            f.write("pytestレポートのパースに失敗しました。\n")
        return

    summary = report_data.get('summary', {})
    total_tests = summary.get('total', 0)
    passed_tests = summary.get('passed', 0)
    failed_tests = summary.get('failed', 0)
    skipped_tests = summary.get('skipped', 0)
    test_duration = report_data.get('duration', 0.0)
    accuracy_raw = read_metric_from_file(ACCURACY_REPORT_PATH)
    inference_time_raw = read_metric_from_file(INFERENCE_TIME_REPORT_PATH)

    try:
        accuracy_value = f"{float(accuracy_raw):.3f}" if accuracy_raw != "N/A" else "N/A"
    except ValueError:
        accuracy_value = "N/A (Format Error)"

    try:
        inference_time_value = f"{float(inference_time_raw):.3f} s" if inference_time_raw != "N/A" else "N/A"
    except ValueError:
        inference_time_value = "N/A (Format Error)"

    summary_content = f"""
### CI/CD結果サマリー

| メトリクス | 数値 |
| :--------- | :--- |
| **総テスト数** | {total_tests} |
| **成功** | {passed_tests} |
| **失敗** | {failed_tests} |
| **スキップ** | {skipped_tests} |
| **実行時間** | {test_duration:.2f} s |
| **モデル精度** | {accuracy_value} |
| **推論時間** | {inference_time_value} |

---

詳細なログは [リンク](https://github.com/{github_repository}/actions/runs/{github_run_id}) を参照。
"""

    # GITHUB_STEP_SUMMARY ファイルに書き込み
    with open(summary_file, 'a') as f:
        f.write(summary_content)
    print("Pytest summary successfully generated.")

if __name__ == "__main__":
    generate_pytest_summary()
