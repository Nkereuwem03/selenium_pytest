"""Utility functions for reading from and writing to Excel files."""

import openpyxl
from openpyxl.styles import PatternFill


GREEN_FILL = PatternFill(start_color="60b212", end_color="60b212", fill_type="solid")

RED_FILL = PatternFill(start_color="ff0000", end_color="ff0000", fill_type="solid")


def load_sheet(file, sheet_name):
    """
    Loads a specified sheet from an Excel file.

    Args:
        file (str): The path to the Excel file.
        sheet_name (str): The name of the sheet to load.

    Returns:
        openpyxl.worksheet.worksheet.Worksheet: The loaded sheet.
    """
    workbook = openpyxl.load_workbook(file)
    if sheet_name not in workbook.sheetnames:
        raise ValueError(f"Sheet '{sheet_name}' does not exist in the workbook.")
    return workbook[sheet_name]


def get_workbook(file):
    """
    Loads the entire workbook from an Excel file.

    Args:
        file (str): The path to the Excel file.

    Returns:
        openpyxl.workbook.workbook.Workbook: The loaded workbook.
    """
    return openpyxl.load_workbook(file)


def get_row_count(file, sheet_name):
    """
    Gets the total number of rows in a specified Excel sheet.

    Args:
        file (str): The path to the Excel file.
        sheet_name (str): The name of the sheet within the Excel file.

    Returns:
        int: The number of rows in the sheet.
    """
    sheet = load_sheet(file, sheet_name)
    return sheet.max_row


def get_column_count(file, sheet_name):
    """
    Gets the total number of columns in a specified Excel sheet.

    Args:
        file (str): The path to the Excel file.
        sheet_name (str): The name of the sheet within the Excel file.

    Returns:
        int: The number of columns in the sheet.
    """
    sheet = load_sheet(file, sheet_name)
    rows = sheet.max_row
    return rows


def read_data(file, sheet_name, row_num, col_num):
    """
    Reads data from a specific cell in an Excel sheet.

    Args:
        file (str): The path to the Excel file.
        sheet_name (str): The name of the sheet within the Excel file.
        row_num (int): The row number of the cell (1-indexed).
        col_num (int): The column number of the cell (1-indexed).

    Returns:
        any: The value from the specified cell.
    """
    sheet = load_sheet(file, sheet_name)
    data = sheet.cell(row_num, col_num).value
    return data


def write_data(file, sheet_name, row_num, col_num, data):
    """
    Writes data to a specific cell in an Excel sheet and saves the workbook.

    Args:
        file (str): The path to the Excel file.
        sheet_name (str): The name of the sheet within the Excel file.
        row_num (int): The row number of the cell (1-indexed).
        col_num (int): The column number of the cell (1-indexed).
        data (any): The data to write to the cell.
    """
    sheet = load_sheet(file, sheet_name)
    sheet.cell(row_num, col_num).value = data
    workbook = get_workbook(file)
    workbook.save(file)


def fill_green_colour(file, sheet_name, row_num, col_num):
    """
    Fills a specific cell in an Excel sheet with a green background color.

    Args:
        file (str): The path to the Excel file.
        sheet_name (str): The name of the sheet within the Excel file.
        row_num (int): The row number of the cell (1-indexed).
        col_num (int): The column number of the cell (1-indexed).
    """
    sheet = load_sheet(file, sheet_name)

    sheet.cell(row_num, col_num).fill = GREEN_FILL
    workbook = get_workbook(file)
    workbook.save(file)


def fill_red_colour(file, sheet_name, row_num, col_num):
    """
    Fills a specific cell in an Excel sheet with a red background color.

    Args:
        file (str): The path to the Excel file.
        sheet_name (str): The name of the sheet within the Excel file.
        row_num (int): The row number of the cell (1-indexed).
        col_num (int): The column number of the cell (1-indexed).
    """
    sheet = load_sheet(file, sheet_name)
    sheet.cell(row_num, col_num).fill = RED_FILL
    workbook = get_workbook(file)
    workbook.save(file)
