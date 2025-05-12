from scripts.transform_features import calculate_features, get_connection

def test_transform_output_not_empty():
    conn = get_connection()
    df = calculate_features(conn)
    assert not df.empty, "Transformed feature set is empty"

def test_columns_exist():
    conn = get_connection()
    df = calculate_features(conn)
    expected_columns = {'client_id', 'paid_loans', 'days_since_late', 'profit_rate_90d'}
    assert expected_columns.issubset(set(df.columns)), "Missing expected feature columns"

def test_decision_values():
    conn = get_connection()
    df = calculate_features(conn)
    assert 'decision' in df.columns, "'decision' column is missing"
    unique_values = set(df['decision'].dropna().unique())
    expected_values = {"ACCEPT", "REJECT"}
    assert unique_values.issubset(expected_values), f"Unexpected decision values found: {unique_values}"
