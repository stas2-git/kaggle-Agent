import pandas as pd
import numpy as np
import os
from typing import Dict, Any, List, Tuple, Optional
from fresh_rebuild_v1.security import validate_file_path, scan_for_prompt_injection
from fresh_rebuild_v1.schemas import MetricsRecord, Anomaly, DriverResult, Contributor

def load_portfolio_data(file_path: str, workspace_root: str) -> pd.DataFrame:
    # 1. Validate file path
    abs_path = validate_file_path(file_path, workspace_root)
    
    # 2. Check if file exists
    if not os.path.exists(abs_path):
        raise FileNotFoundError(f"Portfolio data file not found: {file_path}")
        
    # 3. Load CSV
    try:
        df = pd.read_csv(abs_path)
    except Exception as e:
        raise ValueError(f"Failed to parse CSV: {str(e)}")
        
    return df

def validate_portfolio_data(df: pd.DataFrame) -> Dict[str, Any]:
    required_cols = [
        "valuation_month", "policy_year", "business_segment", "coverage", 
        "state", "underwriter", "account_count", "written_premium", 
        "earned_premium", "incurred_loss", "claim_count", "avg_retention", 
        "avg_limit", "rate_change_pct", "benchmark_adequacy", "notes"
    ]
    
    # Check blocking errors
    blocking_errors = []
    warnings = []
    
    # Missing columns
    missing_cols = [col for col in required_cols if col not in df.columns]
    if missing_cols:
        blocking_errors.append(f"Missing required columns: {', '.join(missing_cols)}")
        return {
            "status": "fail",
            "blocking_errors": blocking_errors,
            "warnings": warnings,
            "row_count": len(df),
            "valid_row_count": 0,
            "injection_flags": []
        }
        
    # Empty dataset
    if len(df) == 0:
        blocking_errors.append("Dataset is empty")
        return {
            "status": "fail",
            "blocking_errors": blocking_errors,
            "warnings": warnings,
            "row_count": 0,
            "valid_row_count": 0,
            "injection_flags": []
        }
        
    # Check types and parse dates
    try:
        pd.to_datetime(df["valuation_month"], format="%Y-%m", errors="raise")
    except Exception:
        blocking_errors.append("valuation_month column contains unparsable dates (expected YYYY-MM)")
        
    # Check numeric columns
    numeric_cols = ["written_premium", "earned_premium", "incurred_loss", "claim_count", "account_count"]
    for col in numeric_cols:
        if not pd.api.types.is_numeric_dtype(df[col]):
            blocking_errors.append(f"Column '{col}' must be numeric")
            
    if blocking_errors:
        return {
            "status": "fail",
            "blocking_errors": blocking_errors,
            "warnings": warnings,
            "row_count": len(df),
            "valid_row_count": 0,
            "injection_flags": []
        }
        
    # Scan warnings
    # Null values in grouping columns
    grouping_cols = ["valuation_month", "business_segment", "coverage", "state", "underwriter"]
    for col in grouping_cols:
        if df[col].isnull().any():
            warnings.append(f"Null values detected in grouping column: {col}")
            
    # Negative premium or claim count
    if (df["written_premium"] < 0).any():
        warnings.append("Negative written_premium detected")
    if (df["earned_premium"] < 0).any():
        warnings.append("Negative earned_premium detected")
    if (df["incurred_loss"] < 0).any():
        warnings.append("Negative incurred_loss detected")
    if (df["claim_count"] < 0).any():
        warnings.append("Negative claim_count detected")
        
    # Earned premium equals zero for rows with incurred losses
    zero_ep_with_loss = df[(df["earned_premium"] == 0) & (df["incurred_loss"] > 0)]
    if len(zero_ep_with_loss) > 0:
        warnings.append("Earned premium is zero on rows with positive incurred losses")
        
    # Scan notes for injection
    injection_flags = []
    for idx, row in df.iterrows():
        notes = row.get("notes")
        if notes and isinstance(notes, str) and scan_for_prompt_injection(notes):
            injection_flags.append({
                "row_index": idx,
                "notes_content": notes
            })
            warnings.append(f"Prompt injection pattern detected in notes at row {idx}")
            
    status = "pass_with_warnings" if warnings else "pass"
    
    return {
        "status": status,
        "blocking_errors": [],
        "warnings": warnings,
        "row_count": len(df),
        "valid_row_count": len(df),
        "injection_flags": injection_flags
    }

def calculate_portfolio_metrics(df: pd.DataFrame, group_by: List[str] = ["valuation_month", "business_segment"]) -> List[MetricsRecord]:
    # Group and aggregate
    grouped = df.groupby(group_by)
    records = []
    
    for keys, group in grouped:
        if len(group_by) == 1:
            key_dict = {group_by[0]: keys}
        else:
            key_dict = dict(zip(group_by, keys))
            
        written_premium = float(group["written_premium"].sum())
        earned_premium = float(group["earned_premium"].sum())
        incurred_loss = float(group["incurred_loss"].sum())
        claim_count = int(group["claim_count"].sum())
        account_count = int(group["account_count"].sum())
        
        # Loss ratio
        loss_ratio = incurred_loss / earned_premium if earned_premium > 0 else 0.0
        
        # Claim frequency proxy
        claim_frequency = claim_count / account_count if account_count > 0 else 0.0
        
        # Average premium per account
        avg_premium = written_premium / account_count if account_count > 0 else 0.0
        
        # Weighted averages (weighted by written_premium)
        total_wp = group["written_premium"].sum()
        
        if total_wp > 0:
            avg_retention = float((group["avg_retention"] * group["written_premium"]).sum() / total_wp)
            rate_change_pct = float((group["rate_change_pct"] * group["written_premium"]).sum() / total_wp)
            benchmark_adequacy = float((group["benchmark_adequacy"] * group["written_premium"]).sum() / total_wp)
        else:
            avg_retention = float(group["avg_retention"].mean()) if not group["avg_retention"].empty else 0.0
            rate_change_pct = float(group["rate_change_pct"].mean()) if not group["rate_change_pct"].empty else 0.0
            benchmark_adequacy = float(group["benchmark_adequacy"].mean()) if not group["benchmark_adequacy"].empty else 0.0
            
        records.append(MetricsRecord(
            valuation_month=key_dict.get("valuation_month", ""),
            business_segment=key_dict.get("business_segment", ""),
            written_premium=written_premium,
            earned_premium=earned_premium,
            incurred_loss=incurred_loss,
            claim_count=claim_count,
            account_count=account_count,
            loss_ratio=loss_ratio,
            rate_change_pct=rate_change_pct,
            benchmark_adequacy=benchmark_adequacy,
            avg_retention=avg_retention
        ))
        
    return records

def detect_anomalies(metrics: List[MetricsRecord], latest_month: str, threshold_config: Optional[Dict[str, Any]] = None) -> List[Anomaly]:
    if not threshold_config:
        threshold_config = {
            "loss_ratio": {"moderate": 0.10, "severe": 0.20},
            "written_premium": {"moderate": 0.15, "severe": 0.30},
            "claim_count": {"moderate": 0.25, "severe": 0.50},
            "rate_change": {"moderate": 0.05, "severe": 0.10},
            "benchmark_adequacy": {"moderate": 0.05, "severe": 0.10},
            "retention": {"moderate": 0.10, "severe": 0.25}
        }
        
    # Get all segments
    segments = set(m.business_segment for m in metrics)
    anomalies = []
    
    # Parse latest month
    latest_dt = pd.to_datetime(latest_month, format="%Y-%m")
    
    # Find prior month
    all_months = sorted(list(set(pd.to_datetime(m.valuation_month, format="%Y-%m") for m in metrics)))
    try:
        latest_idx = all_months.index(latest_dt)
        if latest_idx > 0:
            prior_dt = all_months[latest_idx - 1]
            prior_month = prior_dt.strftime("%Y-%m")
        else:
            prior_month = None
    except ValueError:
        prior_month = None
        
    if not prior_month:
        return [] # No prior period to compare
        
    anomaly_counter = 1
    
    for segment in segments:
        curr_rec = next((m for m in metrics if m.business_segment == segment and m.valuation_month == latest_month), None)
        prior_rec = next((m for m in metrics if m.business_segment == segment and m.valuation_month == prior_month), None)
        
        if not curr_rec or not prior_rec:
            continue
            
        # Helper to register anomaly
        def add_anomaly(metric_name: str, curr_val: float, prior_val: float, abs_chg: float, pct_chg: float, severity: str, desc: str):
            nonlocal anomaly_counter
            anomalies.append(Anomaly(
                anomaly_id=f"ANOM_{anomaly_counter:03d}",
                metric=metric_name,
                business_segment=segment,
                current_value=curr_val,
                prior_value=prior_val,
                absolute_change=abs_chg,
                percent_change=pct_chg,
                severity=severity,
                explanation=desc,
                requires_human_review=(severity == "high")
            ))
            anomaly_counter += 1

        # 1. Loss Ratio (absolute increase)
        lr_diff = curr_rec.loss_ratio - prior_rec.loss_ratio
        if lr_diff >= threshold_config["loss_ratio"]["severe"]:
            add_anomaly("loss_ratio", curr_rec.loss_ratio, prior_rec.loss_ratio, lr_diff, 
                        lr_diff / prior_rec.loss_ratio if prior_rec.loss_ratio > 0 else 0.0, "high",
                        f"Loss ratio increased by {lr_diff*100:.1f} percentage points (from {prior_rec.loss_ratio*100:.1f}% to {curr_rec.loss_ratio*100:.1f}%)")
        elif lr_diff >= threshold_config["loss_ratio"]["moderate"]:
            add_anomaly("loss_ratio", curr_rec.loss_ratio, prior_rec.loss_ratio, lr_diff, 
                        lr_diff / prior_rec.loss_ratio if prior_rec.loss_ratio > 0 else 0.0, "moderate",
                        f"Loss ratio increased by {lr_diff*100:.1f} percentage points (from {prior_rec.loss_ratio*100:.1f}% to {curr_rec.loss_ratio*100:.1f}%)")

        # 2. Written Premium (percentage change)
        if prior_rec.written_premium > 0:
            wp_pct = (curr_rec.written_premium - prior_rec.written_premium) / prior_rec.written_premium
            wp_abs = curr_rec.written_premium - prior_rec.written_premium
            if abs(wp_pct) >= threshold_config["written_premium"]["severe"]:
                add_anomaly("written_premium", curr_rec.written_premium, prior_rec.written_premium, wp_abs, wp_pct, "high",
                            f"Written premium changed by {wp_pct*100:.1f}% (from {prior_rec.written_premium:,.2f} to {curr_rec.written_premium:,.2f})")
            elif abs(wp_pct) >= threshold_config["written_premium"]["moderate"]:
                add_anomaly("written_premium", curr_rec.written_premium, prior_rec.written_premium, wp_abs, wp_pct, "moderate",
                            f"Written premium changed by {wp_pct*100:.1f}% (from {prior_rec.written_premium:,.2f} to {curr_rec.written_premium:,.2f})")

        # 3. Claim Count (percentage increase)
        if prior_rec.claim_count > 0:
            cc_pct = (curr_rec.claim_count - prior_rec.claim_count) / prior_rec.claim_count
            cc_abs = float(curr_rec.claim_count - prior_rec.claim_count)
            if cc_pct >= threshold_config["claim_count"]["severe"]:
                add_anomaly("claim_count", float(curr_rec.claim_count), float(prior_rec.claim_count), cc_abs, cc_pct, "high",
                            f"Claim count increased by {cc_pct*100:.1f}% (from {prior_rec.claim_count} to {curr_rec.claim_count})")
            elif cc_pct >= threshold_config["claim_count"]["moderate"]:
                add_anomaly("claim_count", float(curr_rec.claim_count), float(prior_rec.claim_count), cc_abs, cc_pct, "moderate",
                            f"Claim count increased by {cc_pct*100:.1f}% (from {prior_rec.claim_count} to {curr_rec.claim_count})")

        # 4. Rate Change Deterioration (prior - current in percentage points)
        rc_deterioration = prior_rec.rate_change_pct - curr_rec.rate_change_pct
        if rc_deterioration >= threshold_config["rate_change"]["severe"]:
            add_anomaly("rate_change_pct", curr_rec.rate_change_pct, prior_rec.rate_change_pct, -rc_deterioration, 
                        -rc_deterioration / prior_rec.rate_change_pct if prior_rec.rate_change_pct != 0 else 0.0, "high",
                        f"Rate change deteriorated by {rc_deterioration*100:.1f} percentage points (from {prior_rec.rate_change_pct*100:.1f}% to {curr_rec.rate_change_pct*100:.1f}%)")
        elif rc_deterioration >= threshold_config["rate_change"]["moderate"]:
            add_anomaly("rate_change_pct", curr_rec.rate_change_pct, prior_rec.rate_change_pct, -rc_deterioration, 
                        -rc_deterioration / prior_rec.rate_change_pct if prior_rec.rate_change_pct != 0 else 0.0, "moderate",
                        f"Rate change deteriorated by {rc_deterioration*100:.1f} percentage points (from {prior_rec.rate_change_pct*100:.1f}% to {curr_rec.rate_change_pct*100:.1f}%)")

        # 5. Benchmark Adequacy Deterioration (prior - current)
        ba_deterioration = prior_rec.benchmark_adequacy - curr_rec.benchmark_adequacy
        if ba_deterioration >= threshold_config["benchmark_adequacy"]["severe"]:
            add_anomaly("benchmark_adequacy", curr_rec.benchmark_adequacy, prior_rec.benchmark_adequacy, -ba_deterioration,
                        -ba_deterioration / prior_rec.benchmark_adequacy if prior_rec.benchmark_adequacy > 0 else 0.0, "high",
                        f"Benchmark adequacy index decreased by {ba_deterioration:.2f} (from {prior_rec.benchmark_adequacy:.2f} to {curr_rec.benchmark_adequacy:.2f})")
        elif ba_deterioration >= threshold_config["benchmark_adequacy"]["moderate"]:
            add_anomaly("benchmark_adequacy", curr_rec.benchmark_adequacy, prior_rec.benchmark_adequacy, -ba_deterioration,
                        -ba_deterioration / prior_rec.benchmark_adequacy if prior_rec.benchmark_adequacy > 0 else 0.0, "moderate",
                        f"Benchmark adequacy index decreased by {ba_deterioration:.2f} (from {prior_rec.benchmark_adequacy:.2f} to {curr_rec.benchmark_adequacy:.2f})")

        # 6. Retention Decrease (percentage change)
        if prior_rec.avg_retention > 0:
            ret_pct = (curr_rec.avg_retention - prior_rec.avg_retention) / prior_rec.avg_retention
            ret_abs = curr_rec.avg_retention - prior_rec.avg_retention
            if ret_pct <= -threshold_config["retention"]["severe"]:
                add_anomaly("avg_retention", curr_rec.avg_retention, prior_rec.avg_retention, ret_abs, ret_pct, "high",
                            f"Average retention decreased by {abs(ret_pct)*100:.1f}% (from {prior_rec.avg_retention:,.2f} to {curr_rec.avg_retention:,.2f})")
            elif ret_pct <= -threshold_config["retention"]["moderate"]:
                add_anomaly("avg_retention", curr_rec.avg_retention, prior_rec.avg_retention, ret_abs, ret_pct, "moderate",
                            f"Average retention decreased by {abs(ret_pct)*100:.1f}% (from {prior_rec.avg_retention:,.2f} to {curr_rec.avg_retention:,.2f})")

    return anomalies

def investigate_anomaly_drivers(df: pd.DataFrame, anomaly: Anomaly, latest_month: str, 
                                dimensions: List[str] = ["coverage", "state", "policy_year", "underwriter"], 
                                top_n: int = 5) -> List[DriverResult]:
    # Parse latest and prior months
    latest_dt = pd.to_datetime(latest_month, format="%Y-%m")
    all_months = sorted(list(set(pd.to_datetime(m, format="%Y-%m") for m in df["valuation_month"])))
    
    try:
        latest_idx = all_months.index(latest_dt)
        if latest_idx > 0:
            prior_month = all_months[latest_idx - 1].strftime("%Y-%m")
        else:
            return []
    except ValueError:
        return []

    # Filter dataframe for the segment under review
    segment_df = df[df["business_segment"] == anomaly.business_segment]
    
    curr_segment_df = segment_df[segment_df["valuation_month"] == latest_month]
    prior_segment_df = segment_df[segment_df["valuation_month"] == prior_month]
    
    driver_results = []
    
    # Overall segment totals (denominators)
    curr_segment_ep = curr_segment_df["earned_premium"].sum()
    prior_segment_ep = prior_segment_df["earned_premium"].sum()
    
    curr_segment_wp = curr_segment_df["written_premium"].sum()
    prior_segment_wp = prior_segment_df["written_premium"].sum()
    
    for dim in dimensions:
        if dim not in df.columns:
            continue
            
        # Get all unique values for the dimension in either month
        dim_values = sorted(list(set(curr_segment_df[dim].dropna().unique()) | set(prior_segment_df[dim].dropna().unique())))
        
        contributors = []
        
        for val in dim_values:
            curr_slice = curr_segment_df[curr_segment_df[dim] == val]
            prior_slice = prior_segment_df[prior_segment_df[dim] == val]
            
            # Values for current and prior slice
            curr_wp = curr_slice["written_premium"].sum()
            prior_wp = prior_slice["written_premium"].sum()
            curr_ep = curr_slice["earned_premium"].sum()
            prior_ep = prior_slice["earned_premium"].sum()
            curr_il = curr_slice["incurred_loss"].sum()
            prior_il = prior_slice["incurred_loss"].sum()
            
            # Contribution based on anomaly metric type
            contribution = 0.0
            current_metric_val = 0.0
            prior_metric_val = 0.0
            
            if anomaly.metric == "loss_ratio":
                # Contribution = (Loss_curr_k / EP_curr_total) - (Loss_prior_k / EP_prior_total)
                term1 = curr_il / curr_segment_ep if curr_segment_ep > 0 else 0.0
                term2 = prior_il / prior_segment_ep if prior_segment_ep > 0 else 0.0
                contribution = term1 - term2
                current_metric_val = curr_il / curr_ep if curr_ep > 0 else 0.0
                prior_metric_val = prior_il / prior_ep if prior_ep > 0 else 0.0
                
            elif anomaly.metric == "written_premium":
                # Contribution = (WP_curr_k - WP_prior_k) / WP_prior_total
                contribution = (curr_wp - prior_wp) / prior_segment_wp if prior_segment_wp > 0 else 0.0
                current_metric_val = curr_wp
                prior_metric_val = prior_wp
                
            elif anomaly.metric == "claim_count":
                # Contribution = (CC_curr_k - CC_prior_k) / CC_prior_total
                prior_cc_total = prior_segment_df["claim_count"].sum()
                curr_cc = curr_slice["claim_count"].sum()
                prior_cc = prior_slice["claim_count"].sum()
                contribution = (curr_cc - prior_cc) / prior_cc_total if prior_cc_total > 0 else 0.0
                current_metric_val = float(curr_cc)
                prior_metric_val = float(prior_cc)
                
            elif anomaly.metric == "benchmark_adequacy":
                # Contribution = (WP_curr_k * BA_curr_k / WP_curr_total) - (WP_prior_k * BA_prior_k / WP_prior_total)
                curr_ba_wt = (curr_slice["benchmark_adequacy"] * curr_slice["written_premium"]).sum()
                prior_ba_wt = (prior_slice["benchmark_adequacy"] * prior_slice["written_premium"]).sum()
                term1 = curr_ba_wt / curr_segment_wp if curr_segment_wp > 0 else 0.0
                term2 = prior_ba_wt / prior_segment_wp if prior_segment_wp > 0 else 0.0
                contribution = term1 - term2
                current_metric_val = curr_ba_wt / curr_wp if curr_wp > 0 else (curr_slice["benchmark_adequacy"].mean() if not curr_slice.empty else 0.0)
                prior_metric_val = prior_ba_wt / prior_wp if prior_wp > 0 else (prior_slice["benchmark_adequacy"].mean() if not prior_slice.empty else 0.0)
                
            elif anomaly.metric == "rate_change_pct":
                curr_rc_wt = (curr_slice["rate_change_pct"] * curr_slice["written_premium"]).sum()
                prior_rc_wt = (prior_slice["rate_change_pct"] * prior_slice["written_premium"]).sum()
                term1 = curr_rc_wt / curr_segment_wp if curr_segment_wp > 0 else 0.0
                term2 = prior_rc_wt / prior_segment_wp if prior_segment_wp > 0 else 0.0
                contribution = term1 - term2
                current_metric_val = curr_rc_wt / curr_wp if curr_wp > 0 else (curr_slice["rate_change_pct"].mean() if not curr_slice.empty else 0.0)
                prior_metric_val = prior_rc_wt / prior_wp if prior_wp > 0 else (prior_slice["rate_change_pct"].mean() if not prior_slice.empty else 0.0)
                
            elif anomaly.metric == "avg_retention":
                curr_ret_wt = (curr_slice["avg_retention"] * curr_slice["written_premium"]).sum()
                prior_ret_wt = (prior_slice["avg_retention"] * prior_slice["written_premium"]).sum()
                term1 = curr_ret_wt / curr_segment_wp if curr_segment_wp > 0 else 0.0
                term2 = prior_ret_wt / prior_segment_wp if prior_segment_wp > 0 else 0.0
                contribution = term1 - term2
                current_metric_val = curr_ret_wt / curr_wp if curr_wp > 0 else (curr_slice["avg_retention"].mean() if not curr_slice.empty else 0.0)
                prior_metric_val = prior_ret_wt / prior_wp if prior_wp > 0 else (prior_slice["avg_retention"].mean() if not prior_slice.empty else 0.0)
                
            if abs(contribution) > 1e-6 or abs(current_metric_val - prior_metric_val) > 1e-6:
                contributors.append(Contributor(
                    value=str(val),
                    current_value=float(current_metric_val),
                    prior_value=float(prior_metric_val),
                    contribution_to_change=float(contribution),
                    notes=f"Driver slice for {dim} = {val}"
                ))
                
        # Sort contributors by absolute contribution descending
        contributors.sort(key=lambda c: abs(c.contribution_to_change), reverse=True)
        
        # Take top N
        top_contributors = contributors[:top_n]
        
        if top_contributors:
            driver_results.append(DriverResult(
                anomaly_id=anomaly.anomaly_id,
                dimension=dim,
                top_contributors=top_contributors
            ))
            
    return driver_results
