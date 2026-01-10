#!/bin/bash
set -euo pipefail

PDF="TaxpayersDirectory2018.pdf"
COMPANIES_CSV="companies.csv"
AOP_CSV="aop.csv"
INDIVIDUALS_CSV="individuals.csv"

echo "=== Fast PDF Extraction using pdftotext + awk ==="
echo

if [ ! -f "$PDF" ]; then
    echo "Error: $PDF not found"
    exit 1
fi

echo "Step 1: Extracting all text from PDF (this will take a few minutes)..."
echo "  This extracts all 35,445 pages at once..."

pdftotext -layout "$PDF" - | \
perl -ne '
BEGIN {
    open($comp_fh, ">", "'"$COMPANIES_CSV"'") or die $!;
    open($aop_fh, ">", "'"$AOP_CSV"'") or die $!;
    open($ind_fh, ">", "'"$INDIVIDUALS_CSV"'") or die $!;
    print $comp_fh "sr,name,ntn,tax_paid\n";
    print $aop_fh "sr,name,ntn,tax_paid\n";
    print $ind_fh "sr,name,cnic,tax_paid\n";
    $company_count = 0;
    $aop_count = 0;
    $individual_count = 0;
    $in_aop_section = 0;
}

# Detect section headers
if (/ASSOCIATION OF PERSONS/) {
    $in_aop_section = 1;
    next;
}
if (/^\s*INDIVIDUALS\s*$/) {
    $in_aop_section = 0;
}

if (/^\s*(\d+)\s+(.+?)\s+(\d{7,13})\s+([-\d,]+)\s*$/) {
    $sr = $1;
    $name = $2;
    $regno = $3;
    $tax_str = $4;

    $name =~ s/\s+/ /g;
    $name =~ s/^\s+|\s+$//g;
    $name =~ s/"/""/g;

    $tax_paid = ($tax_str eq "-") ? 0 : ($tax_str =~ s/,//gr);

    if (length($regno) == 13) {
        print $ind_fh "$sr,\"$name\",$regno,$tax_paid\n";
        $individual_count++;
        if ($individual_count % 10000 == 0) {
            print STDERR "  Individuals: $individual_count\n";
        }
    } elsif (length($regno) == 7) {
        if ($in_aop_section) {
            print $aop_fh "$sr,\"$name\",$regno,$tax_paid\n";
            $aop_count++;
            if ($aop_count % 1000 == 0) {
                print STDERR "  AOP: $aop_count\n";
            }
        } else {
            print $comp_fh "$sr,\"$name\",$regno,$tax_paid\n";
            $company_count++;
            if ($company_count % 1000 == 0) {
                print STDERR "  Companies: $company_count\n";
            }
        }
    }
}

END {
    close($comp_fh);
    close($aop_fh);
    close($ind_fh);
    print STDERR "\nExtraction complete!\n";
    print STDERR "  Companies: $company_count\n";
    print STDERR "  Association of Persons (AOP): $aop_count\n";
    print STDERR "  Individuals: $individual_count\n";
}
'

echo
echo "Step 2: Verifying CSV files..."
if [ -f "$COMPANIES_CSV" ]; then
    comp_lines=$(wc -l < "$COMPANIES_CSV")
    comp_size=$(ls -lh "$COMPANIES_CSV" | awk '{print $5}')
    echo "  ✓ $COMPANIES_CSV: $comp_lines lines, $comp_size"
else
    echo "  ✗ $COMPANIES_CSV not created"
fi

if [ -f "$AOP_CSV" ]; then
    aop_lines=$(wc -l < "$AOP_CSV")
    aop_size=$(ls -lh "$AOP_CSV" | awk '{print $5}')
    echo "  ✓ $AOP_CSV: $aop_lines lines, $aop_size"
else
    echo "  ✗ $AOP_CSV not created"
fi

if [ -f "$INDIVIDUALS_CSV" ]; then
    ind_lines=$(wc -l < "$INDIVIDUALS_CSV")
    ind_size=$(ls -lh "$INDIVIDUALS_CSV" | awk '{print $5}')
    echo "  ✓ $INDIVIDUALS_CSV: $ind_lines lines, $ind_size"
else
    echo "  ✗ $INDIVIDUALS_CSV not created"
fi

echo
echo "Done! Run 'python3 scripts/create_database.py' to load into SQLite."
