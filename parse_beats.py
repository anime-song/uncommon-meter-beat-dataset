import os
import json
import glob
import re
import argparse


YOUTUBE_FILENAME_PATTERN = re.compile(
    r"^(?P<title>.+)_(?P<youtube_id>[A-Za-z0-9_-]{11})\.beat$"
)


def extract_youtube_id(file_path):
    basename = os.path.basename(file_path)
    match = YOUTUBE_FILENAME_PATTERN.match(basename)
    if match:
        return match.group("youtube_id")

    if "_" in basename:
        return basename.rsplit("_", 1)[1].replace(".beat", "")

    return os.path.splitext(basename)[0]


def clean_annotation(ann):
    """
    アノテーション文字列の環境依存文字や表記揺れをクリーンアップする
    """
    mapping = {
        "𝄐": "fermata",
        "a tempo": "a_tempo",
        "rit.": "rit",
        "Rubato": "rubato",
        "Shuffle": "shuffle",
        "Swing": "swing",
    }
    return mapping.get(ann, ann)


def parse_beat_file(file_path):
    """
    単一の .beat ファイルをパースして、ダウンビート時間などを計算し辞書のリストを返す
    """
    with open(file_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    # ファイル名から youtube_id を抽出 (最初の '_' 以降を使用)
    basename = os.path.basename(file_path)
    youtube_id = extract_youtube_id(file_path)

    # トラック全体のオフセット (ms) を初期時間として設定
    current_time_ms = float(data.get("offsetMs", 0))

    # テンポと拍子の状態を保持（前小節からの引き継ぎ用）
    current_tempo_bpm = 120.0  # デフォルト値
    current_base_note = "quarter"
    current_time_sig_num = 4
    current_time_sig_den = 4

    parsed_measures = []

    for measure in data.get("measures", []):
        m_index = measure.get("index", 0)

        # 拍子情報の更新
        time_sig = measure.get("timeSignature")
        if time_sig:
            current_time_sig_num = time_sig.get("num", current_time_sig_num)
            current_time_sig_den = time_sig.get("den", current_time_sig_den)

        # テンポ情報の更新
        tempo = measure.get("tempo")
        if tempo:
            current_tempo_bpm = tempo.get("bpm", current_tempo_bpm)
            current_base_note = tempo.get("baseNote", current_base_note)

        # アノテーションの取得とクリーンアップ
        raw_annotations = measure.get("annotations", [])
        cleaned_annotations = [clean_annotation(a) for a in raw_annotations]

        # 現在のダウンビート情報を記録（ms -> sec）
        measure_data = {
            "measure_index": m_index,
            "downbeat_sec": round(current_time_ms / 1000.0, 4),
            "time_sig_num": current_time_sig_num,
            "time_sig_den": current_time_sig_den,
            "tempo_bpm": current_tempo_bpm,
            "base_note": current_base_note,
            "annotations": cleaned_annotations,
        }
        parsed_measures.append(measure_data)

        # --- 次の小節までの時間を計算して加算 ---
        # base_note の種類に応じて基準となる音符の長さを定義
        # "quarter" = 4分音符=1拍, "eighth" = 8分音符=0.5拍, "half" = 2分音符=2拍
        base_note_factor = 4.0
        if current_base_note == "eighth":
            base_note_factor = 8.0
        elif current_base_note == "half":
            base_note_factor = 2.0

        # 1小節の中で含まれる 四分音符の数 (quarter notes per measure)
        # = (num / den) * (基準音符の長さ)
        quarter_notes = current_time_sig_num * (base_note_factor / current_time_sig_den)

        base_note_value = 4
        if current_base_note == "eighth":
            base_note_value = 8
        elif current_base_note == "half":
            base_note_value = 2

        beats_in_measure = current_time_sig_num * (
            base_note_value / current_time_sig_den
        )
        ms_per_beat = 60000.0 / current_tempo_bpm
        measure_duration_ms = beats_in_measure * ms_per_beat

        # オフセットに加算
        current_time_ms += measure_duration_ms

    result_data = {"youtube_id": youtube_id, "measures": parsed_measures}
    return basename, result_data


def process_all_beats(input_dir, output_dir):
    """
    ディレクトリ内のすべての.beatファイルを処理し、個別のJSONファイルに出力する
    """
    os.makedirs(output_dir, exist_ok=True)

    beat_files = glob.glob(os.path.join(input_dir, "*.beat"))
    for file_path in beat_files:
        try:
            file_name, parsed_data = parse_beat_file(file_path)
            output_file = os.path.join(output_dir, f"{file_name}.beats.json")

            with open(output_file, "w", encoding="utf-8") as f:
                json.dump(parsed_data, f, ensure_ascii=False, indent=2)

            # print(f"Processed {os.path.basename(file_path)} -> {output_file}")
        except Exception as e:
            print(f"Error processing {file_path}: {e}")

    print(f"処理完了: {len(beat_files)} ファイルを {output_dir} に出力しました。")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Parse .beat files to JSON annotations."
    )
    parser.add_argument(
        "--input_dir",
        type=str,
        default="beats",
        help="Path to the directory containing .beat files (default: 'beats')",
    )
    parser.add_argument(
        "--output_dir",
        type=str,
        default="parsed_beats",
        help="Path to the directory to save parsed .json files (default: 'parsed_beats')",
    )

    args = parser.parse_args()

    process_all_beats(args.input_dir, args.output_dir)
