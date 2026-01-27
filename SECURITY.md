# Security Policy

## Reporting a Vulnerability

If you find a major security issue:
1.  **Please open a GitHub Issue.**
2.  Mark it with a "security" label if possible.
3.  Please do not post sensitive data (passwords/keys) in public issues.

## Known Vulnerabilities (Scanner False Positives)

If you run a security scan (like Docker Scout or Trivy) on the `homebills` image, you may see "High" severity alerts. **We are aware of these, and they are not exploitable in this application.**

* **`pip`, `wheel`, `setuptools`:** These vulnerabilities are flagged in the build tools. These tools are only used during the creation of the Docker image and are **not** active or accessible when the application is running.
* **`deb / debian` System Libraries:** You may see alerts for system libraries. We update the base image regularly, but some upstream patches may take time to arrive.

**Status:** These are considered safe/low risk for this specific deployment.
