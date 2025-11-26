import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import f1_score, roc_curve, auc, precision_recall_curve

def generate_synthetic(n=2000, seed=42):
    np.random.seed(seed)
    data = pd.DataFrame({
        'num_fields': np.random.poisson(lam=12, size=n),
        'num_pages': np.random.randint(1,6,size=n),
        'raw_length': np.random.normal(1800,350,size=n).astype(int),
        'has_signature_word': np.random.binomial(1,0.75,size=n),
        'suspicious_terms_count': np.random.binomial(3,0.10,size=n),
        'has_amount': np.random.binomial(1,0.55,size=n),
        'max_fraud_sim': np.random.uniform(0.10,0.95,size=n),
        'mean_fraud_sim': np.random.uniform(0.05,0.80,size=n)
    })
    base_prob = (
        0.15 * (data['suspicious_terms_count'] > 1).astype(int) +
        0.55 * data['max_fraud_sim'] +
        0.30 * (1 - data['has_signature_word']) +
        0.1
    )
    prob = np.clip(base_prob, 0, 1)
    data['label'] = np.random.binomial(1, prob)
    return data

def tune_threshold():
    df = generate_synthetic()
    X = df.drop(columns=['label'])
    y = df['label']
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.25, random_state=42, stratify=y)
    clf = RandomForestClassifier(n_estimators=200, random_state=42)
    clf.fit(X_train, y_train)
    proba = clf.predict_proba(X_test)[:,1]
    thresholds = np.linspace(0.01,0.99,99)
    best_f1 = 0
    best_th = 0.5
    for th in thresholds:
        preds = (proba > th).astype(int)
        f1 = f1_score(y_test, preds)
        if f1 > best_f1:
            best_f1 = f1
            best_th = th
    # also produce ROC AUC
    fpr, tpr, _ = roc_curve(y_test, proba)
    roc_auc = auc(fpr, tpr)
    print(f"Suggested threshold (F1-optimized): {best_th:.3f}, F1: {best_f1:.3f}, ROC AUC: {roc_auc:.3f}")
    return {'threshold': best_th, 'f1': best_f1, 'roc_auc': roc_auc}

if __name__ == '__main__':
    tune_threshold()
