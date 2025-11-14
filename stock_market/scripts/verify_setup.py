"""
Verify Setup for Stock Screener Project
Ensures required folders, files, and dependencies exist before running the screener.
"""

from pathlib import Path
import importlib.util
import sys

# ======================================================================
# Define expected structure
# ======================================================================
BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR.parent / "data"
OUTPUT_DIR = BASE_DIR.parent / "outputs"

REQUIRED_FILES = [
    DATA_DIR / "sp500_companies.csv",
    DATA_DIR / "iShares-Russell-2000-ETF_fund.csv",
    DATA_DIR / "nyse-listed.csv",
    DATA_DIR / "SectorPE.xlsx",
]

REQUIRED_LIBRARIES = ["pandas", "yfinance", "tqdm", "openpyxl"]

# ======================================================================
# Check folders and files
# ======================================================================
def check_structure():
    print("🔍 Checking project folder structure...")

    issues = []

    # Ensure folders exist
    for folder in [DATA_DIR, OUTPUT_DIR]:
        if not folder.exists():
            issues.append(f"❌ Missing folder: {folder}")
        else:
            print(f"✅ Found folder: {folder}")

    # Check required files
    for f in REQUIRED_FILES:
        if not f.exists():
            issues.append(f"❌ Missing file: {f.name}")
        else:
            print(f"✅ Found data file: {f.name}")

    # Check write permissions for output
    try:
        test_file = OUTPUT_DIR / "test_write.txt"
        with open(test_file, "w") as temp:
            temp.write("test")
        test_file.unlink()  # remove file
        print(f"✅ Output folder is writable: {OUTPUT_DIR}")
    except Exception as e:
        issues.append(f"❌ Cannot write to output folder: {e}")

    return issues

# ======================================================================
# Check libraries
# ======================================================================
def check_libraries():
    print("\n🔍 Checking Python dependencies...")
    missing = []
    for lib in REQUIRED_LIBRARIES:
        if importlib.util.find_spec(lib) is None:
            missing.append(lib)
            print(f"❌ Missing library: {lib}")
        else:
            print(f"✅ Found library: {lib}")
    return missing

# ======================================================================
# Main
# ======================================================================
if __name__ == "__main__":
    print("=" * 60)
    print("🔧 STOCK SCREENER ENVIRONMENT CHECK")
    print("=" * 60)

    structure_issues = check_structure()
    missing_libs = check_libraries()

    print("\n" + "=" * 60)

    if not structure_issues and not missing_libs:
        print("🎯 All checks passed! You're ready to run the screener.")
    else:
        print("⚠️  Some issues detected:")
        for issue in structure_issues:
            print("   -", issue)
        for lib in missing_libs:
            print(f"   - Missing library: {lib}")
        print("\n💡 Fix the above before running your screener.")

    print("=" * 60)