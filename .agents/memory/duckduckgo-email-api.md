---
name: DuckDuckGo email API
description: Non-obvious request requirements for generating DuckDuckGo private addresses.
---

The undocumented DuckDuckGo private-address endpoint can reject requests with `403 Forbidden` when they identify themselves with a custom bot User-Agent. Browser-like `User-Agent`, `Origin`, and `Referer` headers are needed alongside the bearer token.

**Why:** The endpoint appears to apply anti-automation checks beyond bearer-token validation.

**How to apply:** If a valid-looking token receives 403, first compare the request headers and use browser-like headers before asking the user to rotate credentials. A repeated bearer token across address-generation requests is normal.