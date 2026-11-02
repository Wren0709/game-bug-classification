import argparse
from pathlib import Path

import pandas as pd

from csv_output import REVIEW_COLUMNS, write_csv
from log_signals import detect_signals, read_log

ROOT = Path(__file__).resolve().parent


def load_feedback(path):
    path = Path(path)
    if path.suffix.lower() == '.csv':
        return pd.read_csv(path, keep_default_na=False, dtype=str, encoding='utf-8-sig')
    if path.suffix.lower() in {'.xlsx', '.xlsm'}:
        return pd.read_excel(path, keep_default_na=False, dtype=str, engine='openpyxl')
    raise ValueError('Choose a CSV, XLSX or XLSM file.')


def analyse_feedback(frame, model, text_column, id_column=None, link_column=None,
                     log_column=None, logs_dir=None):
    for column in (text_column, id_column, link_column, log_column):
        if column and column not in frame.columns:
            raise ValueError(f'Column not found: {column}')
    if not text_column:
        raise ValueError('Choose a description column.')
    source = frame.fillna('').astype(str).reset_index(drop=True)
    result = pd.DataFrame('', index=source.index, columns=REVIEW_COLUMNS)
    result['analysis_id'] = [f'ANL_{i:04d}' for i in range(1, len(source) + 1)]
    result['description'] = source[text_column]
    if id_column:
        result['source_record_id'] = source[id_column].str.strip()
    if link_column:
        result['source_record_url'] = source[link_column].str.strip()
    result['review_status'] = 'needs_review'

    descriptions = result['description'].str.strip()
    valid = descriptions.ne('')
    if valid.any():
        probabilities = model.predict_proba(descriptions[valid])
        result.loc[valid, 'suggested_category'] = model.classes_[probabilities.argmax(axis=1)]
        result.loc[valid, 'model_score'] = [f'{score:.3f}' for score in probabilities.max(axis=1)]
    result.loc[~valid, 'review_status'] = 'unresolved'
    result.loc[~valid, 'review_reason'] = 'empty_description'

    for index, row in source.iterrows():
        signals = set(detect_signals(row[log_column])) if log_column else set()
        if 'log_file' in source.columns:
            content, note = read_log(row['log_file'], logs_dir)
            signals.update(detect_signals(content))
            result.at[index, 'log_note'] = note
        result.at[index, 'log_signals'] = '; '.join(sorted(signals))
    return result


def main():
    parser = argparse.ArgumentParser(description='Prepare game feedback for manual review')
    parser.add_argument('--input', type=Path, default=ROOT / 'examples/sample_feedback.csv')
    parser.add_argument('--training', type=Path, default=ROOT / 'data/synthetic_bug_reports.csv')
    parser.add_argument('--output', type=Path, default=ROOT / 'private/workbench_results.csv')
    parser.add_argument('--text-col', default='description')
    parser.add_argument('--id-col', default='', help='Optional source identifier column')
    parser.add_argument('--url-col', default='', help='Optional source link column; links are not fetched')
    parser.add_argument('--log-col', default='', help='Optional log excerpt column')
    parser.add_argument('--logs-dir', type=Path)
    parser.add_argument('--overwrite', action='store_true', help='Replace an existing output file')
    args = parser.parse_args()
    if args.output.exists() and not args.overwrite:
        parser.error('Output already exists. Choose another path or use --overwrite.')
    from main import build_model, load_reports

    reference = load_reports(args.training)
    model = build_model()
    model.fit(reference.description, reference.category)
    result = analyse_feedback(
        load_feedback(args.input), model, args.text_col, args.id_col or None,
        args.url_col or None, args.log_col or None, args.logs_dir,
    )
    write_csv(result, args.output, args.overwrite)
    print(f'Saved {len(result)} reports to {args.output}')
    print(f"Empty descriptions: {result.review_status.eq('unresolved').sum()}")
    print("Review every suggestion. Model scores do not establish a bug's cause.")


if __name__ == '__main__':
    main()
