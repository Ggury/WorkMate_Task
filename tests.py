import os
import tempfile
from io import StringIO
from unittest.mock import patch

import pytest

from DataLoader import DataProcessor
from main import main
from Reports import REPORTS_MAP, MedianCoffeeSpentReport

TEST_DATA_FULL_SET = """student,date,coffee_spent,sleep_hours,study_hours,mood,exam
Алексей Смирнов,2024-06-01,450,4.5,12,норм,Математика
Алексей Смирнов,2024-06-02,500,4.0,14,устал,Математика
Алексей Смирнов,2024-06-03,550,3.5,16,зомби,Математика
Дарья Петрова,2024-06-01,200,7.0,6,отл,Математика
Дарья Петрова,2024-06-02,250,6.5,8,норм,Математика
Дарья Петрова,2024-06-03,300,6.0,9,норм,Математика
Иван Кузнецов,2024-06-01,600,3.0,15,зомби,Математика
Иван Кузнецов,2024-06-02,650,2.5,17,зомби,Математика
Иван Кузнецов,2024-06-03,700,2.0,18,не выжил,Математика
Мария Соколова,2024-06-01,100,8.0,3,отл,Математика
Мария Соколова,2024-06-02,120,8.5,2,отл,Математика
Мария Соколова,2024-06-03,150,7.5,4,отл,Математика
Павел Новиков,2024-06-01,380,5.0,10,норм,Математика
Павел Новиков,2024-06-02,420,4.5,11,устал,Математика
Павел Новиков,2024-06-03,470,4.0,13,устал,Математика
Елена Волкова,2024-06-01,280,6.0,8,норм,Математика
Елена Волкова,2024-06-02,310,5.5,9,норм,Математика
Елена Волкова,2024-06-03,340,5.0,10,устал,Математика
Дмитрий Морозов,2024-06-01,520,3.5,14,зомби,Математика
Дмитрий Морозов,2024-06-02,570,3.0,15,зомби,Математика
Дмитрий Морозов,2024-06-03,620,2.5,17,не выжил,Математика
Анна Белова,2024-06-01,180,7.5,5,отл,Математика
Анна Белова,2024-06-02,210,7.0,6,норм,Математика
Анна Белова,2024-06-03,190,8.0,4,отл,Математика
Сергей Козлов,2024-06-01,400,4.0,11,устал,Математика
Сергей Козлов,2024-06-02,440,3.5,12,зомби,Математика
Сергей Козлов,2024-06-03,480,3.0,14,зомби,Математика
Ольга Новикова,2024-06-01,150,8.0,4,отл,Математика
Ольга Новикова,2024-06-02,180,7.5,5,отл,Математика
Ольга Новикова,2024-06-03,200,7.0,6,норм,Математика
Никита Соловьев,2024-06-01,480,4.0,13,устал,Математика
Никита Соловьев,2024-06-02,530,3.5,15,зомби,Математика
Никита Соловьев,2024-06-03,580,3.0,16,зомби,Математика
Татьяна Васильева,2024-06-01,220,7.0,7,норм,Математика
Татьяна Васильева,2024-06-02,250,6.5,8,норм,Математика
Татьяна Васильева,2024-06-03,280,6.0,9,устал,Математика
Артем Григорьев,2024-06-01,350,5.5,9,норм,Математика
Артем Григорьев,2024-06-02,390,5.0,10,устал,Математика
Артем Григорьев,2024-06-03,430,4.5,12,устал,Математика
Виктория Федорова,2024-06-01,120,8.0,3,отл,Математика
Виктория Федорова,2024-06-02,140,8.5,2,отл,Математика
Виктория Федорова,2024-06-03,160,7.5,4,отл,Математика
Михаил Павлов,2024-06-01,500,3.5,15,зомби,Математика
Михаил Павлов,2024-06-02,550,3.0,16,зомби,Математика
Михаил Павлов,2024-06-03,600,2.5,18,не выжил,Математика
"""

TEST_DATA_MISSING_PERFORMANCE = """student,coffee_spent,sleep_hours,study_hours,mood,exam
Алексей Смирнов,450,4.5,12,норм,Математика
Алексей Смирнов,500,4.0,14,устал,Математика
Алексей Смирнов,550,3.5,16,зомби,Математика
Дарья Петрова,200,7.0,6,отл,Математика
Дарья Петрова,250,6.5,8,норм,Математика
Дарья Петрова,300,6.0,9,норм,Математика
Иван Кузнецов,600,3.0,15,зомби,Математика
Иван Кузнецов,650,2.5,17,зомби,Математика
Иван Кузнецов,700,2.0,18,не выжил,Математика
Мария Соколова,100,8.0,3,отл,Математика
Мария Соколова,120,8.5,2,отл,Математика
Мария Соколова,150,7.5,4,отл,Математика
"""

TEST_DATA_INVALID_Median = """student,coffee_spent,sleep_hours,study_hours,mood,exam
Error Person,Broken Data,Abracadabre,NAN,NAN,неважно,
"""


@pytest.fixture
def create_csv_file():
    temp_files = []

    def _creator(content: str):
        temp_file = tempfile.NamedTemporaryFile(
            mode="w", delete=False, encoding="utf-8", suffix=".csv"
        )
        temp_file.write(content)
        temp_file.close()
        temp_files.append(temp_file.name)
        return temp_file.name

    yield _creator
    for fp in temp_files:
        if os.path.exists(fp):
            os.remove(fp)


def test_processor_load_multiple_files_success(create_csv_file):
    file_path = create_csv_file(TEST_DATA_FULL_SET)

    processor = DataProcessor([file_path])
    data = processor.loaddata()

    assert len(data) == 45
    assert data[0].name == "Алексей Смирнов"


def test_processor_file_not_found():
    processor = DataProcessor(["non_existent_file.csv"])
    with patch("sys.exit") as mock_exit:
        processor.loaddata()
        mock_exit.assert_called_with(1)


def test_processor_missing_required_column(create_csv_file):
    bad_data = (
        "student,coffee_spent,sleep_hours,study_hours,mood,exam\nIvan,100,8,4,ok,Math"
    )
    file_path = create_csv_file(bad_data)
    processor = DataProcessor([file_path])

    with patch("sys.stderr", new=StringIO()) as mock_stderr:
        processor.loaddata()
        assert "File is missing required columns" in mock_stderr.getvalue()


@pytest.mark.parametrize(
    "index, expected_name, expected_median",
    [
        (0, "Иван Кузнецов", 650),
        (1, "Дмитрий Морозов", 570),
        (14, "Мария Соколова", 120),
    ],
)
def test_median_report_generation(create_csv_file, index, expected_name, expected_median):
    file_path = create_csv_file(TEST_DATA_FULL_SET)
    processor = DataProcessor([file_path])
    data = processor.loaddata()

    report = MedianCoffeeSpentReport(data)
    report_body = report.CreateReport()

    assert len(report_body) == 15
    assert report_body[index][0] == expected_name
    assert report_body[index][1] == expected_median


@pytest.mark.parametrize(
    "report_name, expected_class, should_exist",
    [
        (MedianCoffeeSpentReport.REPORT_NAME, MedianCoffeeSpentReport, True),
        ("fake-report", None, False),
        ("average-sleep", None, False),
        ("", None, False),
    ],
)
def test_report_map_logic(report_name, expected_class, should_exist):
    if should_exist:
        assert report_name in REPORTS_MAP
        assert REPORTS_MAP[report_name] is expected_class
    else:
        assert report_name not in REPORTS_MAP


def test_main_execution_flow(create_csv_file):
    """Интеграционный тест вызова main через argparse"""
    file_path = create_csv_file(TEST_DATA_FULL_SET)
    test_args = ["main.py", "--files", file_path, "--report", "median-coffee"]

    with patch("sys.argv", test_args):
        with patch("sys.stdout", new=StringIO()) as mock_stdout:
            main()
            assert "Алексей Смирнов" in mock_stdout.getvalue()
            assert "650" in mock_stdout.getvalue()


def test_processor_invalid_date_format_skips_row(create_csv_file):
    invalid_data = (
        "student,date,coffee_spent,sleep_hours,study_hours,mood,exam\n"
        "Valid Student,2024-06-01,200,8,4,ok,Math\n"
        "Bad Date Student,01-06-2024,300,5,10,tired,Math\n"
    )
    file_path = create_csv_file(invalid_data)
    processor = DataProcessor([file_path])

    with patch("sys.stderr", new=StringIO()) as mock_stderr:
        data = processor.loaddata()
        assert len(data) == 1
        assert data[0].name == "Valid Student"

        assert "Warning: Wrong date format" in mock_stderr.getvalue()
