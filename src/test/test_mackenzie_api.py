def test_mackenzie_api():
    from src.http.get_data_from_mackenzie_api import get_current_day_outputs_data
    data = get_current_day_outputs_data()
    assert data is not None
