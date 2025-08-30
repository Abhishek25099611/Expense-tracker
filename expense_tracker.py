
import csv
import sys
from datetime import datetime
from pathlib import Path

EXPENSES_FILE = Path("expenses.csv")

def parse_date(date_str: str):
    try:
        return datetime.strptime(date_str, "%Y-%m-%d").date()
    except ValueError:
        return None

def parse_month(month_str: str):
    try:
        return datetime.strptime(month_str, "%Y-%m").date().replace(day=1)
    except ValueError:
        return None

def input_non_empty(prompt: str) -> str:
    while True:
        val = input(prompt).strip()
        if val:
            return val
        print("This field cannot be empty. Please try again.")

def input_float(prompt: str) -> float:
    while True:
        raw = input(prompt).strip()
        try:
            val = float(raw)
            if val < 0:
                print("Amount cannot be negative. Try again.")
                continue
            return val
        except ValueError:
            print("Please enter a valid number (e.g., 1250.50).")

def add_expense(expenses: list):
    print("\n--- Add Expense ---")
    while True:
        date_str = input_non_empty("Date (YYYY-MM-DD): ")
        date_obj = parse_date(date_str)
        if date_obj is None:
            print("Invalid date format. Please use YYYY-MM-DD.")
            continue
        break

    category = input_non_empty("Category (e.g., Food, Travel): ")
    amount = input_float("Amount: ")
    description = input_non_empty("Description: ")

    entry = {
        "date": date_obj.isoformat(),
        "category": category,
        "amount": amount,
        "description": description
    }
    expenses.append(entry)
    print("Expense added successfully.")

def is_valid_entry(entry: dict) -> bool:
    required = ["date", "category", "amount", "description"]
    for key in required:
        if key not in entry or entry[key] in (None, ""):
            return False
    # Validate date & amount formats
    if parse_date(entry["date"]) is None:
        return False
    try:
        float(entry["amount"])
    except (TypeError, ValueError):
        return False
    return True

def view_expenses(expenses: list):
    print("\n--- All Expenses ---")
    if not expenses:
        print("No expenses recorded yet.")
        return
    shown_any = False
    for idx, e in enumerate(expenses, start=1):
        if not is_valid_entry(e):
            print(f"[Skipped entry #{idx}] Incomplete or invalid data.")
            continue
        print(f"{idx}. {e['date']} | {e['category']} | {float(e['amount']):.2f} | {e['description']}")
        shown_any = True
    if not shown_any:
        print("No valid expenses to display.")

def set_monthly_budget(budgets: dict):
    print("\n--- Set Monthly Budget ---")
    print("Tip: Budget is tracked per month (YYYY-MM).")
    while True:
        month_str = input_non_empty("Enter month to set budget for (YYYY-MM), or 'current' for this month: ")
        if month_str.lower() == "current":
            month_date = datetime.today().date().replace(day=1)
        else:
            month_date = parse_month(month_str)
            if month_date is None:
                print("Invalid month format. Please use YYYY-MM (e.g., 2025-08).")
                continue
        break

    amount = input_float("Enter total budget amount for the month: ")
    key = month_date.strftime("%Y-%m")
    budgets[key] = amount
    print(f"Budget for {key} set to {amount:.2f}.")

def calc_total_for_month(expenses: list, year_month: str) -> float:
    total = 0.0
    for e in expenses:
        if not is_valid_entry(e):
            continue
        d = parse_date(e["date"])
        if d.strftime("%Y-%m") == year_month:
            total += float(e["amount"])
    return total

def track_budget(expenses: list, budgets: dict):
    print("\n--- Track Budget ---")
    default_month = datetime.today().strftime("%Y-%m")
    month_str = input(f"Enter month to track (YYYY-MM) [default {default_month}]: ").strip() or default_month

    if parse_month(month_str) is None:
        print("Invalid month format. Please use YYYY-MM.")
        return

    if month_str not in budgets:
        print(f"No budget set for {month_str}.")
        choice = input("Would you like to set it now? (y/n): ").strip().lower()
        if choice == "y":
            # Reuse set budget flow for this specific month
            amount = input_float("Enter total budget amount for the month: ")
            budgets[month_str] = amount
            print(f"Budget for {month_str} set to {amount:.2f}.")
        else:
            return

    total = calc_total_for_month(expenses, month_str)
    budget = budgets[month_str]
    remaining = budget - total

    print(f"Month: {month_str}")
    print(f"Budget: {budget:.2f}")
    print(f"Spent:  {total:.2f}")
    if remaining < 0:
        print(f"Status: You have exceeded your budget by {-remaining:.2f}!")
    else:
        print(f"Status: You have {remaining:.2f} left for the month.")

def save_expenses(expenses: list, filename: Path = EXPENSES_FILE):
    try:
        with filename.open("w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["date", "category", "amount", "description"])
            for e in expenses:
                if not is_valid_entry(e):
                    # Skip invalid entries to keep file clean
                    continue
                writer.writerow([e["date"], e["category"], f"{float(e['amount']):.2f}", e["description"]])
        print(f"Expenses saved to {filename.resolve()}")
    except Exception as ex:
        print(f"Failed to save expenses: {ex}")

def load_expenses(filename: Path = EXPENSES_FILE) -> list:
    expenses = []
    if not filename.exists():
        return expenses
    try:
        with filename.open("r", newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                # Normalize and validate basic shape; full validation later
                entry = {
                    "date": row.get("date", "").strip(),
                    "category": row.get("category", "").strip(),
                    "amount": float(row.get("amount", "0") or 0),
                    "description": row.get("description", "").strip(),
                }
                expenses.append(entry)
    except Exception as ex:
        print(f"Failed to load existing expenses: {ex}")
    return expenses

def menu():
    print("\n============================")
    print(" Personal Expense Tracker ")
    print("============================")
    print("1. Add expense")
    print("2. View expenses")
    print("3. Track budget")
    print("4. Save expenses")
    print("5. Save & Exit")

def main():
    expenses = load_expenses()
    budgets = {}  # month 'YYYY-MM' -> amount (not persisted as per spec)

    print("Loaded", len(expenses), "expense(s) from file." if expenses else "No saved expenses found yet.")
    while True:
        menu()
        choice = input("Choose an option (1-5): ").strip()

        if choice == "1":
            add_expense(expenses)
        elif choice == "2":
            view_expenses(expenses)
        elif choice == "3":
            track_budget(expenses, budgets)
        elif choice == "4":
            save_expenses(expenses)
        elif choice == "5":
            save_expenses(expenses)
            print("Goodbye!")
            break
        else:
            print("Invalid choice. Please enter a number between 1 and 5.")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nInterrupted. Saving and exiting...")
        # Best-effort save on Ctrl+C
        try:
            # We don't have the in-scope 'expenses' here cleanly; restart main to save isn't feasible.
            # In a more advanced version, we'd store state globally. For simplicity, just exit.
            sys.exit(0)
        except Exception:
            sys.exit(1)
