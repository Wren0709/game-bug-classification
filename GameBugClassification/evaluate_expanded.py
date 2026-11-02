from pathlib import Path
import argparse
import hashlib
import json
import platform
import re

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import pandas as pd
import sklearn
from sklearn.metrics import ConfusionMatrixDisplay, accuracy_score, classification_report, confusion_matrix, f1_score

from csv_output import write_csv
from main import build_model, load_reports

ROOT = Path(__file__).resolve().parent


def normalized_descriptions(reports):
    return reports.description.str.normalize('NFKC').str.casefold().str.replace(r'[\W_]+', '', regex=True)


def verify_datasets(original, expanded, challenge):
    original_ids = set(original.report_id)
    expanded_ids = set(expanded.report_id)
    challenge_ids = set(challenge.report_id)
    if not original_ids.issubset(expanded_ids):
        raise ValueError('The expanded dataset must contain all original report IDs.')
    indexed = expanded.set_index('report_id')
    for field in ('title', 'description', 'category', 'data_source'):
        expected = original.set_index('report_id')[field].sort_index()
        actual = indexed.loc[expected.index, field]
        if not actual.equals(expected):
            raise ValueError(f'Original data has changed: {field}')
    if expanded_ids & challenge_ids:
        raise ValueError('Training and challenge report IDs overlap.')
    expanded_texts = set(normalized_descriptions(expanded))
    challenge_texts = set(normalized_descriptions(challenge))
    if expanded_texts & challenge_texts:
        raise ValueError('Training and challenge descriptions overlap.')
    if len(expanded) != 240 or len(challenge) != 50:
        raise ValueError('Expected 240 training and 50 challenge examples.')
    if not expanded.category.value_counts().eq(48).all():
        raise ValueError('The expanded dataset must have 48 reports per category.')
    if not challenge.category.value_counts().eq(10).all():
        raise ValueError('The challenge set must have 10 reports per category.')


def run_evaluation(original, expanded, challenge, output):
    verify_datasets(original, expanded, challenge)
    if output.exists() and any(output.iterdir()):
        raise FileExistsError('Output folder is not empty. Choose another --output directory.')
    output.mkdir(parents=True, exist_ok=True)
    labels = sorted(challenge.category.unique())
    metric_rows = []
    prediction_frame = challenge[['report_id', 'title', 'description', 'category']].rename(columns={'category':'actual_category'}).copy()
    details = {}
    for name, data in [('original_140', original), ('expanded_240', expanded)]:
        model = build_model()
        model.fit(data.description, data.category)
        prediction = model.predict(challenge.description)
        prediction_frame[name + '_prediction'] = prediction
        prediction_frame[name + '_correct'] = (prediction == challenge.category).to_numpy()
        acc = float(accuracy_score(challenge.category, prediction))
        f1 = float(f1_score(challenge.category, prediction, average='macro', zero_division=0))
        metric_rows.append({'model_training_dataset': name, 'training_reports': len(data),
                            'challenge_reports': len(challenge), 'accuracy': round(acc, 6), 'macro_f1': round(f1, 6)})
        matrix = confusion_matrix(challenge.category, prediction, labels=labels)
        details[name] = {'accuracy':acc, 'macro_f1':f1,
                         'by_class':classification_report(challenge.category, prediction, labels=labels, output_dict=True, zero_division=0),
                         'confusion_matrix':matrix.tolist()}
        fig, ax = plt.subplots(figsize=(8,6))
        ConfusionMatrixDisplay(confusion_matrix=matrix, display_labels=labels).plot(
            ax=ax, cmap='Blues', xticks_rotation=30, colorbar=False)
        ax.set_title(f'{name}: synthetic challenge reports (n=50)')
        fig.tight_layout()
        fig.savefig(output / f'confusion_matrix_{name}.png', dpi=170)
        plt.close(fig)
    write_csv(prediction_frame, output / 'challenge_predictions.csv')
    write_csv(pd.DataFrame(metric_rows), output / 'challenge_summary.csv')
    write_csv(prediction_frame.loc[(~prediction_frame.original_140_correct) | (~prediction_frame.expanded_240_correct)],
              output / 'challenge_misclassifications.csv')
    record = {
        'evaluation_scope':'50 synthetic challenge descriptions, not independent real-world data',
        'challenge_data_used_for_training':False,
        'data_source_note':'All extra synthetic records are AI-assisted fictional examples. Similar scenarios across sets may inflate scores.',
        'environment':{'python':platform.python_version(), 'scikit_learn':sklearn.__version__},
        'dataset_sha256': {
            name:hashlib.sha256((ROOT / f'data/{name}').read_bytes()).hexdigest()
            for name in ('synthetic_bug_reports.csv', 'synthetic_bug_reports_expanded.csv','synthetic_challenge_reports.csv')
        },
        'model':'TF-IDF word 1–2 grams + balanced logistic regression (same pipeline for both)',
        'results':details,
    }
    (output / 'challenge_metrics.json').write_text(json.dumps(record,indent=2),encoding='utf-8')
    lines = [
        'Synthetic challenge comparison: 50 cases, 10 per category',
        'Models use identical hyperparameters; each model is fitted to its own training dataset.',
        'Neither model trains on these 50 challenge reports.',
        '',
    ]
    for item in metric_rows:
        lines.append(f"{item['model_training_dataset']} (n={item['training_reports']}): "
                     f"accuracy={item['accuracy']:.3f}; macro-F1={item['macro_f1']:.3f}")
    lines += [
        '',
        'This is a synthetic development comparison, not a real-world generalisation test.',
        'Some issue scenarios may resemble the training data. No causal claim is made about data size alone.',
    ]
    (output / 'evaluation.txt').write_text('\n'.join(lines)+'\n',encoding='utf-8')
    print('\n'.join(lines))
    return record


def main():
    parser=argparse.ArgumentParser(description='Compare original and expanded datasets on a separate synthetic challenge set')
    parser.add_argument('--original',type=Path,default=ROOT/'data/synthetic_bug_reports.csv')
    parser.add_argument('--expanded',type=Path,default=ROOT/'data/synthetic_bug_reports_expanded.csv')
    parser.add_argument('--challenge',type=Path,default=ROOT/'data/synthetic_challenge_reports.csv')
    parser.add_argument('--output',type=Path,default=ROOT/'private/expanded_challenge')
    args=parser.parse_args()
    run_evaluation(load_reports(args.original),load_reports(args.expanded),load_reports(args.challenge),args.output)


if __name__=='__main__':
    main()
