import pandas as pd
import numpy as np
from pathlib import Path
from typing import List, Tuple, Dict, Any
from portfolio_agent.core.security import validate_file_path, scan_text_for_injection
from portfolio_agent.core.schemas import MetricsRecord, AnomalyRecord, DriverResult, DriverContributor

def load_portfolio_data(file_path: str, workspace_root: str = None) -> pd.DataFrame:
    """
    Validate path and load synthetic portfolio CSV.
    """
    valid_path = validate_file_path(file_path, workspace_root)
    if not valid_path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")
    return pd.read_csv(valid_path)

def validate_portfolio_data(df: pd.DataFrame) -> Tuple[pd.DataFrame, List[str], List[str]]:
    """
    Validate schema, required columns, and data quality.
    Returns (clean_df, errors, warnings).
    """
    errors: List[str] = []
    warnings: List[str] = []

    # 1. Check for empty dataset
    if df.empty:
        errors.append("Dataset is empty.")
        return df, errors, warnings

    # 2. Check for required columns
    required_cols = [
        "valuation_month", "policy_year", "business_segment", "coverage", 
        "state", "underwriter", "account_count", "written_premium", 
        "earned_premium", "incurred_loss", "claim_count", "avg_retention", 
        "avg_limit", "rate_change_pct", "benchmark_adequacy"
    ]
    missing_cols = [col for col in required_cols if col not in df.columns]
    if missing_cols:
        errors.append(f"Missing required columns: {missing_cols}")
        return df, errors, warnings

    # 3. Check valuation_month parseability
    month_pattern = re_compile = r"^\d{4}-\d{2}$"
    import re
    invalid_months = df[~df["valuation_month"].astype(str).str.match(month_pattern)]
    if not invalid_months.empty:
        errors.append(f"Invalid valuation_month format in rows: {invalid_months.index.tolist()}")

    # 4. Check for non-numeric core columns
    numeric_cols = ["written_premium", "earned_premium", "incurred_loss", "claim_count", "account_count"]
    for col in numeric_cols:
        if not pd.api.types.is_numeric_dtype(df[col]):
            errors.append(f"Column '{col}' is non-numeric.")

    if errors:
        return df, errors, warnings

    # 5. Warnings: Null values in grouping keys
    grouping_keys = ["business_segment", "coverage", "state", "underwriter"]
    for col in grouping_keys:
        if df[col].isnull().any():
            warnings.append(f"Null values detected in grouping column '{col}'.")

    # 6. Warnings: Negative values in core metrics
    for col in ["written_premium", "earned_premium", "incurred_loss", "claim_count"]:
        if (df[col] < 0).any():
            warnings.append(f"Negative values detected in column '{col}'.")

    # 7. Warnings: Earned premium equals 0 with incurred losses
    zero_ep_loss = df[(df["earned_premium"] == 0) & (df["incurred_loss"] > 0)]
    if not zero_ep_loss.empty:
        warnings.append("Rows detected with zero earned premium but positive incurred losses.")

    # 8. Warnings: Scan notes for prompt injection
    if "notes" in df.columns:
        injections = df[df["notes"].apply(lambda x: scan_text_for_injection(str(x)))]
        if not injections.empty:
            warnings.append(f"Suspicious notes / prompt injection attempt detected on rows: {injections.index.tolist()}")

    return df, errors, warnings

def calculate_portfolio_metrics(df: pd.DataFrame, group_by: List[str] = None) -> List[MetricsRecord]:
    """
    Calculate deterministic portfolio metrics by month and segment.
    """
    if group_by is None:
        group_by = ["valuation_month", "business_segment"]

    records: List[MetricsRecord] = []
    
    # Group and aggregate
    grouped = df.groupby(group_by)
    
    for keys, group in grouped:
        val_month = keys[0] if isinstance(keys, tuple) else val_month
        bus_seg = keys[1] if isinstance(keys, tuple) else keys
        
        # Simple sums
        written = float(group["written_premium"].sum())
        earned = float(group["earned_premium"].sum())
        loss = float(group["incurred_loss"].sum())
        claims = int(group["claim_count"].sum())
        accounts = int(group["account_count"].sum())
        
        # Loss ratio calculation
        loss_ratio = loss / earned if earned > 0 else 0.0
        
        # Weighted averages (weighting by written premium)
        total_wp = group["written_premium"].sum()
        if total_wp > 0:
            weights = group["written_premium"] / total_wp
            avg_ret = float(np.average(group["avg_retention"], weights=weights))
            rate_chg = float(np.average(group["rate_change_pct"], weights=weights))
            bench_ad = float(np.average(group["benchmark_adequacy"], weights=weights))
        else:
            avg_ret = float(group["avg_retention"].mean())
            rate_chg = float(group["rate_change_pct"].mean())
            bench_ad = float(group["benchmark_adequacy"].mean())
            
        records.append(
            MetricsRecord(
                valuation_month=val_month,
                business_segment=bus_seg,
                written_premium=written,
                earned_premium=earned,
                incurred_loss=loss,
                claim_count=claims,
                account_count=accounts,
                loss_ratio=loss_ratio,
                rate_change_pct=rate_chg,
                benchmark_adequacy=bench_ad,
                avg_retention=avg_ret
            )
        )
        
    return records

def detect_anomalies(metrics: List[MetricsRecord], latest_month: str) -> List[AnomalyRecord]:
    """
    Identify anomalies comparing the latest month to the previous month.
    """
    anomalies: List[AnomalyRecord] = []
    
    # Index metrics by segment and month for fast lookup
    metric_map: Dict[Tuple[str, str], MetricsRecord] = {
        (m.valuation_month, m.business_segment): m for m in metrics
    }
    
    # Calculate previous month date YYYY-MM
    try:
        yr, mo = map(int, latest_month.split("-"))
        if mo == 1:
            prior_yr, prior_mo = yr - 1, 12
        else:
            prior_yr, prior_mo = yr, mo - 1
        prior_month = f"{prior_yr:04d}-{prior_mo:02d}"
    except Exception:
        # Fallback if YYYY-MM parsing fails
        return anomalies

    latest_records = [m for m in metrics if m.valuation_month == latest_month]
    
    for cur in latest_records:
        prior = metric_map.get((prior_month, cur.business_segment))
        if not prior:
            continue  # No baseline comparison period
            
        segment = cur.business_segment
        
        # Check Loss Ratio Anomaly (+10 pts moderate, +20 pts severe)
        lr_change = cur.loss_ratio - prior.loss_ratio
        if lr_change >= 0.10:
            severity = "high" if lr_change >= 0.20 else "moderate"
            anomalies.append(
                AnomalyRecord(
                    anomaly_id=f"ANOM_{latest_month}_{segment.replace(' ', '_')}_LR",
                    metric="loss_ratio",
                    business_segment=segment,
                    current_value=cur.loss_ratio,
                    prior_value=prior.loss_ratio,
                    absolute_change=lr_change,
                    percent_change=lr_change / prior.loss_ratio if prior.loss_ratio > 0 else 0.0,
                    severity=severity,
                    explanation=f"Loss ratio increased by {lr_change * 100:.1f} percentage points (from {prior.loss_ratio * 100:.1f}% to {cur.loss_ratio * 100:.1f}%).",
                    requires_human_review=True if severity == "high" else False
                )
            )

        # Check Premium Anomaly (+/-15% moderate, +/-30% severe)
        if prior.written_premium > 0:
            wp_change_pct = (cur.written_premium - prior.written_premium) / prior.written_premium
            if abs(wp_change_pct) >= 0.15:
                severity = "high" if abs(wp_change_pct) >= 0.30 else "moderate"
                anomalies.append(
                    AnomalyRecord(
                        anomaly_id=f"ANOM_{latest_month}_{segment.replace(' ', '_')}_WP",
                        metric="written_premium",
                        business_segment=segment,
                        current_value=cur.written_premium,
                        prior_value=prior.written_premium,
                        absolute_change=cur.written_premium - prior.written_premium,
                        percent_change=wp_change_pct,
                        severity=severity,
                        explanation=f"Written premium changed by {wp_change_pct * 100:.1f}% (from {prior.written_premium:,.0f} to {cur.written_premium:,.0f}).",
                        requires_human_review=True if severity == "high" else False
                    )
                )

        # Check Benchmark Adequacy Anomaly (< 0.90 is moderate/severe)
        if cur.benchmark_adequacy < 0.90:
            severity = "high" if cur.benchmark_adequacy < 0.80 else "moderate"
            anomalies.append(
                AnomalyRecord(
                    anomaly_id=f"ANOM_{latest_month}_{segment.replace(' ', '_')}_BA",
                    metric="rate_adequacy",
                    business_segment=segment,
                    current_value=cur.benchmark_adequacy,
                    prior_value=prior.benchmark_adequacy,
                    absolute_change=cur.benchmark_adequacy - prior.benchmark_adequacy,
                    percent_change=(cur.benchmark_adequacy - prior.benchmark_adequacy) / prior.benchmark_adequacy if prior.benchmark_adequacy > 0 else 0.0,
                    severity=severity,
                    explanation=f"Benchmark adequacy score deteriorated to {cur.benchmark_adequacy:.2f} (from {prior.benchmark_adequacy:.2f}).",
                    requires_human_review=True  # Pricing related issues require human review
                )
            )

        # Check Claim Count Anomaly (+25% moderate, +50% severe, increase only)
        if prior.claim_count > 0:
            cc_change_pct = (cur.claim_count - prior.claim_count) / prior.claim_count
            if cc_change_pct >= 0.25:
                severity = "high" if cc_change_pct >= 0.50 else "moderate"
                anomalies.append(
                    AnomalyRecord(
                        anomaly_id=f"ANOM_{latest_month}_{segment.replace(' ', '_')}_CC",
                        metric="claim_count",
                        business_segment=segment,
                        current_value=float(cur.claim_count),
                        prior_value=float(prior.claim_count),
                        absolute_change=float(cur.claim_count - prior.claim_count),
                        percent_change=cc_change_pct,
                        severity=severity,
                        explanation=f"Claim count increased by {cc_change_pct * 100:.1f}% (from {prior.claim_count} to {cur.claim_count}).",
                        requires_human_review=True if severity == "high" else False
                    )
                )

        # Check Rate Change Deterioration (-5 pts moderate, -10 pts severe, decrease only)
        rc_change = cur.rate_change_pct - prior.rate_change_pct
        if rc_change <= -0.05:
            severity = "high" if rc_change <= -0.10 else "moderate"
            anomalies.append(
                AnomalyRecord(
                    anomaly_id=f"ANOM_{latest_month}_{segment.replace(' ', '_')}_RC",
                    metric="rate_change",
                    business_segment=segment,
                    current_value=cur.rate_change_pct,
                    prior_value=prior.rate_change_pct,
                    absolute_change=rc_change,
                    percent_change=rc_change / prior.rate_change_pct if prior.rate_change_pct != 0 else 0.0,
                    severity=severity,
                    explanation=f"Rate change deteriorated by {abs(rc_change) * 100:.1f} percentage points (from {prior.rate_change_pct * 100:.1f}% to {cur.rate_change_pct * 100:.1f}%).",
                    requires_human_review=True if severity == "high" else False
                )
            )

        # Check Retention Decrease (-10% moderate, -25% severe, decrease only)
        if prior.avg_retention > 0:
            ret_change_pct = (cur.avg_retention - prior.avg_retention) / prior.avg_retention
            if ret_change_pct <= -0.10:
                severity = "high" if ret_change_pct <= -0.25 else "moderate"
                anomalies.append(
                    AnomalyRecord(
                        anomaly_id=f"ANOM_{latest_month}_{segment.replace(' ', '_')}_RET",
                        metric="avg_retention",
                        business_segment=segment,
                        current_value=cur.avg_retention,
                        prior_value=prior.avg_retention,
                        absolute_change=cur.avg_retention - prior.avg_retention,
                        percent_change=ret_change_pct,
                        severity=severity,
                        explanation=f"Average retention decreased by {abs(ret_change_pct) * 100:.1f}% (from {prior.avg_retention:,.0f} to {cur.avg_retention:,.0f}).",
                        requires_human_review=True if severity == "high" else False
                    )
                )

    return anomalies

def investigate_anomaly_drivers(df: pd.DataFrame, anomaly: AnomalyRecord, dimensions: List[str] = None) -> List[DriverResult]:
    """
    Slices the raw dataframe across dimensions to find top contributors to an anomaly.
    """
    if dimensions is None:
        dimensions = ["coverage", "state", "underwriter", "policy_year"]

    # Deduce latest month and prior month from anomaly ID or metadata
    # Anomaly ID format: ANOM_2026-06_Segment_Metric
    try:
        latest_month = anomaly.anomaly_id.split("_")[1]
        yr, mo = map(int, latest_month.split("-"))
        prior_month = f"{yr - 1:04d}-12" if mo == 1 else f"{yr:04d}-{mo - 1:02d}"
    except Exception:
        return []

    segment = anomaly.business_segment
    metric = anomaly.metric

    # Filter data for this segment and the comparison months
    df_seg = df[df["business_segment"] == segment]
    df_cur = df_seg[df_seg["valuation_month"] == latest_month]
    df_pri = df_seg[df_seg["valuation_month"] == prior_month]

    results: List[DriverResult] = []

    for dim in dimensions:
        if dim not in df.columns:
            continue
            
        contributors: List[DriverContributor] = []
        
        # Calculate metric values by dimension value for both periods
        if metric == "loss_ratio":
            # Current by dimension
            cur_grp = df_cur.groupby(dim).agg({"incurred_loss": "sum", "earned_premium": "sum"})
            # Prior by dimension
            pri_grp = df_pri.groupby(dim).agg({"incurred_loss": "sum", "earned_premium": "sum"})
            
            total_earned_cur = df_cur["earned_premium"].sum()
            total_earned_pri = df_pri["earned_premium"].sum()
            
            all_vals = set(cur_grp.index).union(set(pri_grp.index))
            
            for val in all_vals:
                cur_loss = cur_grp.loc[val, "incurred_loss"] if val in cur_grp.index else 0.0
                cur_earned = cur_grp.loc[val, "earned_premium"] if val in cur_grp.index else 0.0
                
                pri_loss = pri_grp.loc[val, "incurred_loss"] if val in pri_grp.index else 0.0
                pri_earned = pri_grp.loc[val, "earned_premium"] if val in pri_grp.index else 0.0
                
                cur_lr = cur_loss / cur_earned if cur_earned > 0 else 0.0
                pri_lr = pri_loss / pri_earned if pri_earned > 0 else 0.0
                
                # Contribution formula:
                # cell_cur_loss/total_cur_earned - cell_pri_loss/total_pri_earned
                contrib = (cur_loss / total_earned_cur if total_earned_cur > 0 else 0.0) - \
                          (pri_loss / total_earned_pri if total_earned_pri > 0 else 0.0)
                          
                contributors.append(
                    DriverContributor(
                        value=str(val),
                        current_value=cur_lr,
                        prior_value=pri_lr,
                        contribution_to_change=float(contrib),
                        notes=f"Earned Premium: {cur_earned:,.0f}"
                    )
                )
        elif metric == "written_premium":
            cur_grp = df_cur.groupby(dim)["written_premium"].sum()
            pri_grp = df_pri.groupby(dim)["written_premium"].sum()
            total_pri_wp = df_pri["written_premium"].sum()
            
            all_vals = set(cur_grp.index).union(set(pri_grp.index))
            
            for val in all_vals:
                cur_wp = cur_grp.loc[val] if val in cur_grp.index else 0.0
                pri_wp = pri_grp.loc[val] if val in pri_grp.index else 0.0
                
                # Contribution: absolute change relative to the prior period total
                contrib = (cur_wp - pri_wp) / total_pri_wp if total_pri_wp > 0 else 0.0
                
                contributors.append(
                    DriverContributor(
                        value=str(val),
                        current_value=float(cur_wp),
                        prior_value=float(pri_wp),
                        contribution_to_change=float(contrib),
                        notes=f"Change: {cur_wp - pri_wp:+,.0f}"
                    )
                )
        elif metric == "rate_adequacy":
            # Group by dimension and calculate average or weighted average benchmark_adequacy
            cur_grp_wp = df_cur.groupby(dim)["written_premium"].sum()
            pri_grp_wp = df_pri.groupby(dim)["written_premium"].sum()

            # Using groupby-apply to calculate weighted average
            cur_grp_ba = df_cur.groupby(dim).apply(lambda g: np.average(g["benchmark_adequacy"], weights=g["written_premium"]) if g["written_premium"].sum() > 0 else g["benchmark_adequacy"].mean())
            pri_grp_ba = df_pri.groupby(dim).apply(lambda g: np.average(g["benchmark_adequacy"], weights=g["written_premium"]) if g["written_premium"].sum() > 0 else g["benchmark_adequacy"].mean())

            total_cur_wp = df_cur["written_premium"].sum()
            total_pri_wp = df_pri["written_premium"].sum()

            all_vals = set(cur_grp_ba.index).union(set(pri_grp_ba.index))

            for val in all_vals:
                cur_ba = float(cur_grp_ba.loc[val]) if val in cur_grp_ba.index else 0.0
                pri_ba = float(pri_grp_ba.loc[val]) if val in pri_grp_ba.index else 0.0

                cur_wp = float(cur_grp_wp.loc[val]) if val in cur_grp_wp.index else 0.0
                pri_wp = float(pri_grp_wp.loc[val]) if val in pri_grp_wp.index else 0.0

                # Weighted contribution to the change in benchmark adequacy
                cur_share = cur_wp / total_cur_wp if total_cur_wp > 0 else 0.0
                pri_share = pri_wp / total_pri_wp if total_pri_wp > 0 else 0.0

                contrib = (cur_ba * cur_share) - (pri_ba * pri_share)

                contributors.append(
                    DriverContributor(
                        value=str(val),
                        current_value=cur_ba,
                        prior_value=pri_ba,
                        contribution_to_change=float(contrib),
                        notes=f"Change: {cur_ba - pri_ba:+.2f}"
                    )
                )
        elif metric == "claim_count":
            # Additive metric: same pattern as written_premium
            cur_grp = df_cur.groupby(dim)["claim_count"].sum()
            pri_grp = df_pri.groupby(dim)["claim_count"].sum()
            total_pri_cc = df_pri["claim_count"].sum()

            all_vals = set(cur_grp.index).union(set(pri_grp.index))

            for val in all_vals:
                cur_cc = cur_grp.loc[val] if val in cur_grp.index else 0.0
                pri_cc = pri_grp.loc[val] if val in pri_grp.index else 0.0

                contrib = (cur_cc - pri_cc) / total_pri_cc if total_pri_cc > 0 else 0.0

                contributors.append(
                    DriverContributor(
                        value=str(val),
                        current_value=float(cur_cc),
                        prior_value=float(pri_cc),
                        contribution_to_change=float(contrib),
                        notes=f"Change: {cur_cc - pri_cc:+,.0f}"
                    )
                )
        elif metric in ("rate_change", "avg_retention"):
            # Premium-weighted-average metric: same pattern as rate_adequacy, parametrized by column
            value_col = "rate_change_pct" if metric == "rate_change" else "avg_retention"

            cur_grp_wp = df_cur.groupby(dim)["written_premium"].sum()
            pri_grp_wp = df_pri.groupby(dim)["written_premium"].sum()

            cur_grp_val = df_cur.groupby(dim).apply(lambda g: np.average(g[value_col], weights=g["written_premium"]) if g["written_premium"].sum() > 0 else g[value_col].mean())
            pri_grp_val = df_pri.groupby(dim).apply(lambda g: np.average(g[value_col], weights=g["written_premium"]) if g["written_premium"].sum() > 0 else g[value_col].mean())

            total_cur_wp = df_cur["written_premium"].sum()
            total_pri_wp = df_pri["written_premium"].sum()

            all_vals = set(cur_grp_val.index).union(set(pri_grp_val.index))

            for val in all_vals:
                cur_v = float(cur_grp_val.loc[val]) if val in cur_grp_val.index else 0.0
                pri_v = float(pri_grp_val.loc[val]) if val in pri_grp_val.index else 0.0

                cur_wp = float(cur_grp_wp.loc[val]) if val in cur_grp_wp.index else 0.0
                pri_wp = float(pri_grp_wp.loc[val]) if val in pri_grp_wp.index else 0.0

                cur_share = cur_wp / total_cur_wp if total_cur_wp > 0 else 0.0
                pri_share = pri_wp / total_pri_wp if total_pri_wp > 0 else 0.0

                contrib = (cur_v * cur_share) - (pri_v * pri_share)

                contributors.append(
                    DriverContributor(
                        value=str(val),
                        current_value=cur_v,
                        prior_value=pri_v,
                        contribution_to_change=float(contrib),
                        notes=f"Change: {cur_v - pri_v:+.4f}"
                    )
                )

        # Sort contributors by absolute contribution in descending order
        contributors.sort(key=lambda x: abs(x.contribution_to_change), reverse=True)
        results.append(
            DriverResult(
                anomaly_id=anomaly.anomaly_id,
                dimension=dim,
                top_contributors=contributors[:5]
            )
        )

    return results
