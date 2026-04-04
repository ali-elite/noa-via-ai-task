# API Rate Limiting and Enterprise Tier Upgrades

## Overview of Rate Limits
To ensure the stability and fairness of our platform, we enforce API rate limits across our different tiers.

### Basic Tier
- 100 requests per minute
- 10,000 requests per month
- Best for testing, small personal projects, and light automation.

### Pro Tier
- 500 requests per minute
- 100,000 requests per month
- Ideal for growing startups and moderate production workloads.

### Enterprise Tier
- Custom rate limits (starting at 5,000 requests per minute)
- Unlimited monthly requests
- Dedicated IP addresses available.

## Handling HTTP 429 Errors
If you exceed your rate limit, the API will return a `429 Too Many Requests` HTTP status code. Look for the `Retry-After` header in the response, which tells you how many seconds to wait before trying again. We strongly recommend implementing exponential backoff in your API clients.

## Upgrading to Enterprise
If you consistently hit rate limits on the Pro plan, it's time to consider an Enterprise upgrade. Enterprise plans include:
- Custom volume agreements
- Dedicated account manager
- Custom SLA
- SAML/SSO integration

To upgrade, please contact our sales team at sales@example.com or open a ticket with the "Sales Inquiry" category.
