import inspect
import json

from portfolio_agent import adk_tools


class FakeToolContext:
    def __init__(self):
        self.state = {}


def _successful_adapter_flow():
    context = FakeToolContext()
    loaded = adk_tools.load_portfolio_data("tests/golden/loss_ratio_spike.csv", context)
    validated = adk_tools.validate_portfolio_data(loaded["dataset_ref"], context)
    metrics = adk_tools.calculate_portfolio_metrics(
        loaded["dataset_ref"],
        ["valuation_month", "business_segment"],
        context,
    )
    anomalies = adk_tools.detect_anomalies(metrics["metrics_ref"], "2026-06", context)
    return context, loaded, validated, metrics, anomalies


def test_adapter_results_are_json_serializable_and_preserve_deterministic_values():
    context, loaded, validated, metrics, anomalies = _successful_adapter_flow()

    json.dumps(loaded)
    json.dumps(validated)
    json.dumps(metrics)
    json.dumps(anomalies)

    assert loaded["status"] == "success"
    assert validated["validation_status"] == "pass"
    assert metrics["metrics_records"]

    loss_ratio_anomalies = [
        anomaly
        for anomaly in anomalies["anomalies"]
        if anomaly["metric"] == "loss_ratio" and anomaly["business_segment"] == "Public D&O"
    ]
    assert loss_ratio_anomalies
    assert loss_ratio_anomalies[0]["severity"] == "high"
    assert loss_ratio_anomalies[0]["requires_human_review"] is True
    assert context.state[adk_tools.STATE_DATASETS]


def test_validation_is_required_before_calculations():
    context = FakeToolContext()
    loaded = adk_tools.load_portfolio_data("tests/golden/loss_ratio_spike.csv", context)

    result = adk_tools.calculate_portfolio_metrics(
        loaded["dataset_ref"],
        ["valuation_month", "business_segment"],
        context,
    )

    assert result["status"] == "error"
    assert result["reason_code"] == "validation_required"


def test_metrics_adapter_rejects_noncanonical_grouping():
    context = FakeToolContext()
    loaded = adk_tools.load_portfolio_data("tests/golden/loss_ratio_spike.csv", context)
    adk_tools.validate_portfolio_data(loaded["dataset_ref"], context)

    result = adk_tools.calculate_portfolio_metrics(
        loaded["dataset_ref"],
        ["policy_year", "valuation_month"],
        context,
    )

    assert result["status"] == "error"
    assert result["reason_code"] == "unsupported_metric_group_by"


def test_driver_analysis_requires_real_anomaly_id():
    context, loaded, _validated, metrics, anomalies = _successful_adapter_flow()

    result = adk_tools.investigate_anomaly_drivers(
        loaded["dataset_ref"],
        anomalies["anomaly_ref"],
        "ANOM_DOES_NOT_EXIST",
        ["coverage"],
        3,
        context,
    )

    assert result["status"] == "error"
    assert result["reason_code"] == "unknown_anomaly_id"


def test_driver_dimensions_are_allowlisted():
    context, loaded, _validated, _metrics, anomalies = _successful_adapter_flow()
    anomaly_id = anomalies["anomalies"][0]["anomaly_id"]

    result = adk_tools.investigate_anomaly_drivers(
        loaded["dataset_ref"],
        anomalies["anomaly_ref"],
        anomaly_id,
        ["coverage", "secret_column"],
        3,
        context,
    )

    assert result["status"] == "error"
    assert result["reason_code"] == "unauthorized_driver_dimension"


def test_driver_analysis_success_uses_opaque_refs_and_limits_top_contributors():
    context, loaded, _validated, _metrics, anomalies = _successful_adapter_flow()
    anomaly_id = anomalies["anomalies"][0]["anomaly_id"]

    result = adk_tools.investigate_anomaly_drivers(
        loaded["dataset_ref"],
        anomalies["anomaly_ref"],
        anomaly_id,
        ["coverage", "state"],
        2,
        context,
    )

    json.dumps(result)
    assert result["status"] == "success"
    assert result["driver_ref"].startswith("drivers:")
    assert {item["dimension"] for item in result["driver_results"]} == {"coverage", "state"}
    assert all(len(item["top_contributors"]) <= 2 for item in result["driver_results"])


def test_model_facing_adapters_do_not_expose_artifact_paths_or_defaults():
    adapter_functions = [
        adk_tools.load_portfolio_data,
        adk_tools.validate_portfolio_data,
        adk_tools.calculate_portfolio_metrics,
        adk_tools.detect_anomalies,
        adk_tools.investigate_anomaly_drivers,
    ]

    forbidden_name_parts = ("output", "report", "trace", "artifact", "path_out")
    for function in adapter_functions:
        signature = inspect.signature(function)
        for parameter in signature.parameters.values():
            assert parameter.default is inspect.Parameter.empty
            assert not any(part in parameter.name for part in forbidden_name_parts)
