#!/usr/bin/env python3
"""
Clean blocker.txt by removing whitelisted domains that are essential for normal internet usage
"""

WHITELIST = {
    # Payment processors and gateways
    'paypal.com',
    'stripe.com',
    'square.com',
    'authorize.net',
    'braintree.com',
    '2checkout.com',
    'checkout.com',
    'adyen.com',
    'worldpay.com',
    'payu.com',
    'razorpay.com',
    'paytm.com',
    'payoneer.com',
    'skrill.com',
    'neteller.com',
    'wise.com',
    'transferwise.com',

    # Major banks
    'chase.com',
    'bankofamerica.com',
    'wellsfargo.com',
    'citibank.com',
    'citigroup.com',
    'capitalone.com',
    'usbank.com',
    'pnc.com',
    'td.com',
    'suntrust.com',
    'bbt.com',
    'hsbc.com',
    'barclays.com',
    'lloyds.com',
    'santander.com',
    'rbs.com',
    'natwest.com',
    'deutsche-bank.com',
    'commerzbank.com',
    'ing.com',
    'rabobank.com',

    # Credit card companies
    'visa.com',
    'mastercard.com',
    'americanexpress.com',
    'discover.com',
    'dinersclub.com',

    # Major tech companies (core domains)
    'google.com',
    'apple.com',
    'microsoft.com',
    'amazon.com',
    'facebook.com',
    'twitter.com',
    'linkedin.com',
    'instagram.com',

    # Email providers
    'gmail.com',
    'outlook.com',
    'yahoo.com',
    'hotmail.com',
    'aol.com',
    'protonmail.com',

    # Government and essential services (be careful with these)
    # Only whitelist specific important ones
    'irs.gov',
    'ssa.gov',
    'medicare.gov',
    'medicaid.gov',

    # Common CDN and infrastructure that sites depend on
    'cloudflare.com',
    'akamai.com',
    'fastly.com',
    'stackpath.com',
}

def is_whitelisted(domain):
    """Check if a domain should be whitelisted (not blocked)"""
    domain = domain.lower().strip()
    
    # Handle regex patterns (remove || and ^)
    if domain.startswith('||') and domain.endswith('^'):
        domain = domain[2:-1]
    
    for whitelisted in WHITELIST:
        if domain == whitelisted or domain.endswith('.' + whitelisted):
            return True
    return False

def clean_blocklist(input_file, output_file, removed_file):
    """Clean the blocklist by removing whitelisted domains"""
    cleaned_domains = []
    removed_domains = []
    removed_count = 0

    try:
        with open(input_file, 'r') as f:
            for line in f:
                line_stripped = line.strip()
                if not line_stripped or line_stripped.startswith('#'):
                    cleaned_domains.append(line)
                    continue

                if is_whitelisted(line_stripped):
                    removed_count += 1
                    removed_domains.append(line_stripped)
                    print(f"Removed whitelisted domain: {line_stripped}")
                else:
                    cleaned_domains.append(line)

        # Update the header with new count
        header_updated = False
        for i, line in enumerate(cleaned_domains):
            if line.startswith('# Total unique domains:'):
                # Count actual domains
                domain_count = sum(1 for l in cleaned_domains if l.strip() and not l.startswith('#'))
                cleaned_domains[i] = f'# Total unique domains: {domain_count}\n'
                header_updated = True
                break

        with open(output_file, 'w') as f:
            f.writelines(cleaned_domains)

        # Write removed domains to separate file
        with open(removed_file, 'w') as f:
            f.write("# Whitelisted domains removed from blocker.txt\n")
            f.write(f"# Total removed: {len(removed_domains)}\n")
            f.write("# Date: 2026-03-13\n\n")
            for domain in sorted(removed_domains):
                f.write(domain + '\n')

        print(f"\nCleaning complete:")
        print(f"Removed {removed_count} whitelisted domains")
        print(f"Remaining domains: {sum(1 for l in cleaned_domains if l.strip() and not l.startswith('#'))}")
        print(f"Cleaned blocklist saved to: {output_file}")
        print(f"Removed domains recorded in: {removed_file}")

    except Exception as e:
        print(f"Error cleaning blocklist: {e}")

if __name__ == "__main__":
    clean_blocklist('blocker.txt', 'blocker.txt', 'whitelisted_domains.txt')