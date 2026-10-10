"""
BeforePay — Isolation Forest Anomaly Estimator
------------------------------------------------
Implementation of the Isolation Forest algorithm (Liu, Ting, Zhou)
trained on normal payment telemetry baselines to generate first-pass anomaly scores.
"""

import math
import random
from razorpay_client import RazorpaySyntheticClient
from feature_pipeline import FeatureEngineeringPipeline

def avg_path_length_c(n):
    """Average path length of unsuccessful search in Binary Search Tree (c(n))."""
    if n <= 1:
        return 0.0
    if n == 2:
        return 1.0
    return 2.0 * (math.log(n - 1) + 0.5772156649) - (2.0 * (n - 1.0) / n)

class IsolationTreeNode:
    def __init__(self, left=None, right=None, split_feature=None, split_val=None, size=0, is_leaf=False):
        self.left = left
        self.right = right
        self.split_feature = split_feature
        self.split_val = split_val
        self.size = size
        self.is_leaf = is_leaf

class IsolationTree:
    def __init__(self, max_depth=8):
        self.max_depth = max_depth
        self.root = None

    def fit(self, X, current_depth=0):
        n_samples = len(X)
        if n_samples <= 1 or current_depth >= self.max_depth:
            return IsolationTreeNode(size=n_samples, is_leaf=True)

        n_features = len(X[0])
        feature_idx = random.randint(0, n_features - 1)

        feat_vals = [row[feature_idx] for row in X]
        min_v, max_v = min(feat_vals), max(feat_vals)

        if min_v == max_v:
            return IsolationTreeNode(size=n_samples, is_leaf=True)

        split_val = random.uniform(min_v, max_v)

        left_X = [row for row in X if row[feature_idx] < split_val]
        right_X = [row for row in X if row[feature_idx] >= split_val]

        if not left_X or not right_X:
            return IsolationTreeNode(size=n_samples, is_leaf=True)

        left_child = self.fit(left_X, current_depth + 1)
        right_child = self.fit(right_X, current_depth + 1)

        return IsolationTreeNode(
            left=left_child,
            right=right_child,
            split_feature=feature_idx,
            split_val=split_val,
            size=n_samples,
            is_leaf=False
        )

    def path_length(self, node, x, current_depth=0):
        if node.is_leaf or node.left is None or node.right is None:
            return current_depth + avg_path_length_c(node.size)

        if x[node.split_feature] < node.split_val:
            return self.path_length(node.left, x, current_depth + 1)
        else:
            return self.path_length(node.right, x, current_depth + 1)

class IsolationForestBaseline:
    def __init__(self, n_estimators=50, max_samples=128):
        self.n_estimators = n_estimators
        self.max_samples = max_samples
        self.trees = []
        self.c_factor = avg_path_length_c(max_samples)
        self.pipeline = FeatureEngineeringPipeline()
        self.is_fitted = False

    def fit_baseline(self, normal_transactions=None):
        """Fits the Isolation Forest on normal baseline payment sequences."""
        if normal_transactions is None:
            client = RazorpaySyntheticClient(seed=42)
            dataset = client.generate_dataset(normal_count=500, scam_count=0)
            normal_transactions = dataset

        X = [self.pipeline.extract(tx)["feature_vector"] for tx in normal_transactions]

        self.trees = []
        max_depth = math.ceil(math.log2(max(2, self.max_samples)))

        for _ in range(self.n_estimators):
            subsample = random.sample(X, min(len(X), self.max_samples))
            tree = IsolationTree(max_depth=max_depth)
            tree.root = tree.fit(subsample)
            self.trees.append(tree)

        self.is_fitted = True

    def compute_anomaly_score(self, tx_payload):
        """
        Calculates first-pass Isolation Forest anomaly score.
        Returns a score in 0 - 100 range.
        """
        if not self.is_fitted:
            self.fit_baseline()

        x = self.pipeline.extract(tx_payload)["feature_vector"]

        # Average path length h(x) across all trees
        paths = [tree.path_length(tree.root, x) for tree in self.trees]
        avg_path = sum(paths) / float(len(paths))

        # Raw isolation anomaly score s = 2^(- avg_path / c)
        raw_s = 2.0 ** (- (avg_path / (self.c_factor + 1e-5)))

        # Feature boost multipliers for severe telemetry signals
        # (active call, pasted VPA, new payee, amount Z-score)
        call_active = x[14]
        is_new_payee = x[3]
        pasted_vpa = x[16]
        screen_share = x[17]
        amount_z = x[7] * 10.0

        boost = 1.0 + 0.45 * call_active + 0.35 * is_new_payee + 0.30 * pasted_vpa + 0.40 * screen_share + 0.25 * min(3.0, amount_z / 4.0)

        boosted_score = raw_s * boost
        
        # Scale to 0 - 100 range
        scaled_score = min(100.0, max(0.0, round(boosted_score * 110.0, 1)))

        return {
            "isolation_forest_raw_score": round(raw_s, 4),
            "average_path_length": round(avg_path, 2),
            "isolation_forest_score_100": scaled_score,
            "telemetry_boost_multiplier": round(boost, 2)
        }

if __name__ == "__main__":
    iforest = IsolationForestBaseline(n_estimators=40, max_samples=100)
    iforest.fit_baseline()

    client = RazorpaySyntheticClient(seed=42)
    norm_tx = client.generate_normal_transaction("cust_synth_0001")
    scam_tx = client.generate_scam_transaction("cust_synth_0001", "DIGITAL_ARREST")

    norm_res = iforest.compute_anomaly_score(norm_tx)
    scam_res = iforest.compute_anomaly_score(scam_tx)

    print("--- Isolation Forest First-Pass Anomaly Scores ---")
    print(f"Normal Payment Score: {norm_res['isolation_forest_score_100']}/100 (Path Length: {norm_res['average_path_length']})")
    print(f"Digital Arrest Scam Score: {scam_res['isolation_forest_score_100']}/100 (Path Length: {scam_res['average_path_length']})")
