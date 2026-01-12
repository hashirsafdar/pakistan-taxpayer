#!/bin/bash
set -euo pipefail

YEAR="${1:-2018}"

# Find the PDF file in the year directory (any filename)
PDF_DIR="docs/data/$YEAR"
if [ -d "$PDF_DIR" ]; then
    PDF=$(find "$PDF_DIR" -maxdepth 1 -name "*.pdf" -type f | head -1)
else
    # Fallback to old location for backwards compatibility
    PDF="data/TaxpayersDirectory${YEAR}.pdf"
fi

COMPANIES_CSV="$PDF_DIR/companies.csv"
AOP_CSV="$PDF_DIR/aop.csv"
INDIVIDUALS_CSV="$PDF_DIR/individuals.csv"

# Determine if year has serial numbers (2017, 2018 have them; 2013-2016 don't)
HAS_SERIAL="false"
if [ "$YEAR" = "2017" ] || [ "$YEAR" = "2018" ]; then
    HAS_SERIAL="true"
fi

echo "=== Fast PDF Extraction using pdftotext + awk ==="
echo

if [ ! -f "$PDF" ]; then
    echo "Error: $PDF not found"
    exit 1
fi

echo "Step 1: Extracting all text from PDF (this will take a few minutes)..."
echo "  This extracts all pages at once..."

pdftotext -layout "$PDF" - | \
perl -ne '
BEGIN {
    open($comp_fh, ">", "'"$COMPANIES_CSV"'") or die $!;
    open($aop_fh, ">", "'"$AOP_CSV"'") or die $!;
    open($ind_fh, ">", "'"$INDIVIDUALS_CSV"'") or die $!;
    $has_serial = "'"$HAS_SERIAL"'" eq "true";
    $year = "'"$YEAR"'";

    # Determine format based on year:
    # 2013: all ntn_8 (no individuals)
    # 2014-2016: ntn_8 for companies/AOP, cnic_13/cnic_14 for individuals
    # 2017-2018: ntn_7 for companies/AOP (truncated), cnic_13 for individuals (truncated)

    if ($year eq "2013") {
        # 2013: only companies/AOP with ntn_8, no individuals section
        print $comp_fh "name,ntn_8,tax_paid\n";
        print $aop_fh "name,ntn_8,tax_paid\n";
        print $ind_fh "name,ntn_8,tax_paid\n";  # probably empty
    } elsif ($has_serial) {
        # 2017-2018: has serial numbers, use 7-digit NTN and 13-digit CNIC
        print $comp_fh "sr,name,ntn_7,tax_paid\n";
        print $aop_fh "sr,name,ntn_7,tax_paid\n";
        print $ind_fh "sr,name,cnic,tax_paid\n";
    } else {
        # 2014-2016: no serial numbers, use 8-digit NTN and CNIC (no distinction between 13/14 digits)
        print $comp_fh "name,ntn_8,tax_paid\n";
        print $aop_fh "name,ntn_8,tax_paid\n";
        print $ind_fh "name,cnic,tax_paid\n";
    }

    $company_count = 0;
    $aop_count = 0;
    $individual_count = 0;
    $in_aop_section = 0;
    $in_individual_section = 0;
    $auto_sr = 0;
}

# Detect section headers
if (/ASSOCIATION OF PERSONS?/) {
    $in_aop_section = 1;
    next;
}
if (/^\s*INDIVIDUALS?\s*$/) {
    # INDIVIDUAL (2013) or INDIVIDUALS (2014+)
    $in_aop_section = 0;
    $in_individual_section = 1;
    next;
}

# Match based on whether PDFs have serial numbers
if ($has_serial) {
    # For 2017, 2018: has explicit serial numbers
    if (/^\s*(\d+)\s+(.+?)\s+(\d{7}[-\d]*|\d{13}[-\d]*)\s+([-\d,]+)\s*$/) {
        $sr = $1;
        $name = $2;
        $regno = $3;
        $tax_str = $4;
        $auto_sr = $sr;
    } else {
        next;
    }
} else {
    # For 2013-2016: no serial numbers, auto-generate
    if (/^\s*(.+?)\s+(\d{7}[-\d]*|\d{13}[-\d]*)\s+([-\d,]+)\s*$/) {
        $auto_sr++;
        $sr = $auto_sr;
        $name = $1;
        $regno = $2;
        $tax_str = $3;
    } else {
        next;
    }
}

# Remove hyphens from registration number
$regno =~ s/-//g;

$name =~ s/\s+/ /g;
$name =~ s/^\s+|\s+$//g;
$name =~ s/"/""/g;

$tax_paid = ($tax_str eq "-") ? 0 : ($tax_str =~ s/,//gr);

# Determine type by length: 7-8 digits = NTN (companies/AOP), 13-14 digits = CNIC (individuals)
$regno_len = length($regno);

if ($regno_len >= 13) {
    # Individual (CNIC): 13 or 14 digits
    if ($has_serial) {
        # 2017-2018: truncate to 13 digits
        $regno_val = substr($regno, 0, 13);
        print $ind_fh "$sr,\"$name\",$regno_val,$tax_paid\n";
    } else {
        # 2014-2016: use CNIC as-is (no split into cnic_13/cnic_14)
        print $ind_fh "\"$name\",$regno,$tax_paid\n";
    }
    $individual_count++;
    if ($individual_count % 10000 == 0) {
        print STDERR "  Individuals: $individual_count\n";
    }
} elsif ($regno_len >= 7) {
    # Company/AOP (NTN): 7 or 8 digits, OR individuals with short CNICs
    if ($in_individual_section) {
        # In individual section: treat as CNIC regardless of length
        if ($has_serial) {
            # 2017-2018
            print $ind_fh "$sr,\"$name\",$regno,$tax_paid\n";
        } else {
            # 2014-2016
            print $ind_fh "\"$name\",$regno,$tax_paid\n";
        }
        $individual_count++;
        if ($individual_count % 10000 == 0) {
            print STDERR "  Individuals: $individual_count\n";
        }
    } else {
        # Company/AOP (NTN): 7 or 8 digits
        my $row;
        if ($year eq "2013") {
            # 2013: use 8-digit NTN as-is
            $row = "\"$name\",$regno,$tax_paid\n";
        } elsif ($has_serial) {
            # 2017-2018: truncate to 7 digits
            $regno_val = substr($regno, 0, 7);
            $row = "$sr,\"$name\",$regno_val,$tax_paid\n";
        } else {
            # 2014-2016: use 8-digit NTN as-is
            $row = "\"$name\",$regno,$tax_paid\n";
        }

        if ($in_aop_section) {
            print $aop_fh $row;
            $aop_count++;
            if ($aop_count % 10000 == 0) {
                print STDERR "  AOP: $aop_count\n";
            }
        } else {
            print $comp_fh $row;
            $company_count++;
            if ($company_count % 10000 == 0) {
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
echo "Step 2: Verifying CSV files (Year: $YEAR)..."
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
echo "Done! Run 'bash scripts/create_parquet_duckdb.sh $YEAR' to create Parquet files."
