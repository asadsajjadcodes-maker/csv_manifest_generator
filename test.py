from pathlib import Path
from core.scanner import scan_directory, export_to_csv




# Test scanning the current working directory
target_folder = Path.cwd()
    
print(f"\n--- Testing Day 1 Core Scanner on: {target_folder} ---")
    
# Step 1: Perform full scan
results = scan_directory(target_folder)
    
# Step 2: Display first 3 scanned records in terminal
print(f"\nTotal Files Audited: {len(results)}")
print("Sample Metadata extracted:")
for record in results[:3]:
    print(f"  - {record['Filename']} | {record['Size_MB']} MB | {record['Last_Modified']}")

# Step 3: Export manifest report to CSV
output_manifest = target_folder / "logs" / "test_manifest.csv"
export_to_csv(results, output_manifest)
print(f"\nDone! CSV saved to: {output_manifest}\n")