# DRHL Response-Cascade Oracle

DRHL no longer determines whether an access-control vulnerability exists by comparing database state before and after an attack request. Database snapshots are still used to isolate crawler side effects and to restore the test application, but vulnerability confirmation is response based.

For each generated attack vector, DRHL sends a forced request with the attacking role and evaluates the response through a cascaded oracle:

1. Public-page rules. If the target is configured as a public page, successful access is not considered a vulnerability.
2. Redirect evidence. Redirects to login, warning, error, forbidden, or denial pages indicate that access control was enforced.
3. Denial markers. DRHL checks denial strings configured in the application profile and denial messages extracted from source code.
4. Invalid-resource markers. If the response indicates that the target object does not exist, DRHL treats the request as not confirmed rather than vulnerable.
5. Protected-content markers. For selected applications, DRHL can require protected content to appear before reporting exposure.
6. Normal response. If the response is a normal HTTP 200 resource page without redirect or denial evidence, DRHL reports the page as vulnerable.

This oracle is intentionally conservative for missing or invalid resources and avoids treating database side effects as the primary vulnerability signal.
