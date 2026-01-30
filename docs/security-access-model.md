# Security and Access Model

# Repository Governance, Access & Security

## Executive Summary

This document outlines the governance structure, access control policies, and security best practices for the CV extraction project repository. Given the sensitive nature of CV data and proprietary codebase, we implement strict access controls and security measures aligned with data protection regulations and industry best practices.

---

## 1. Repository Visibility & Justification

### Decision: PRIVATE Repository

**Rationale:**

The repository is configured as **PRIVATE** due to the following critical factors:

1. **Sensitive Data Handling**
   - The project processes Curriculum Vitae (CV) data containing personal information (names, contact details, work history, education)
   - This constitutes personally identifiable information (PII) subject to data protection regulations (GDPR, CCPA)
   - Exposure would violate privacy agreements with data subjects

2. **Proprietary Codebase**
   - The CV extraction logic and data processing pipeline represent competitive intellectual property
   - The extraction algorithms and parsing strategies are business-critical assets
   - Public exposure would diminish competitive advantage

3. **Client Confidentiality**
   - The codebase is developed for a specific client under contractual obligation
   - The client expects exclusive access to the solution
   - Unauthorized public access violates contractual terms

4. **Regulatory Compliance**
   - Data protection regulations require appropriate access controls
   - GDPR Article 32 requires security measures appropriate to the risk level
   - Private repository status is a foundational security control


## 2. Teams, Roles & Permissions

### Role Definitions

#### 1. **Owner** (Repository Owner)
**Count:** 1 (Hiring Company Admin)

**Permissions:**
- Transfer repository ownership
- Delete repository
- Manage all teams and members
- Bypass branch protection (emergency only)
- Full workflow management
- Audit logs access

**Responsibilities:**
- Approve new team members
- Monitor compliance
- Respond to security incidents
- Review contract requirements
---

#### 2. **Admin** (Co-Administrators)
**Count:** 2 minimum (1 from hiring company, 1 from our company)

**Permissions:**
- Manage team membership
- Configure branch protection rules
- Manage secrets and variables
- Access audit logs
- Review and approve PRs (with merge authority)
- Configure actions and workflows
- Manage security settings

**Responsibilities:**
- Enforce access control policies
- Monitor security compliance
- Conduct regular access reviews
- Respond to access requests
- Maintain audit logs
- Lead incident response

---

#### 3. **Maintainer** (Core Development Team)
**Count:** developers (only those specified in contract)

**Permissions:**
- Push to feature branches
- Create pull requests
- Review and approve PRs (but cannot self-approve)
- Merge PRs to main branch (after approval process)
- Create and manage release branches
- Push to develop/staging branches
- Access CI/CD logs for their changes
- Cannot: Delete branches, manage members, modify branch protection

**Responsibilities:**
- Implement features and fixes
- Conduct thorough code reviews
- Ensure code quality standards
- Document changes
- Maintain changelog
- Write tests and validation

---


#### 4. **Observer/Read-Only** (Optional)
**Count:** 1-2 (e.g., project managers, stakeholders)


**Permissions:**
- View repository and code
- Read pull requests and discussions
- View workflows and CI/CD status
- Cannot: Push, merge, or modify anything

**Responsibilities:**
- Track project progress
- Facilitate communication
- Support reporting


---



## 3. Branch Protection Rules

### Protected Branches Configuration

#### **Main Branch** (Production)

**Enforcement Level:** STRICT - All rules mandatory

```yaml
Branch: main

Protection Rules:
  1. Require pull request reviews before merging
     - Minimum 2 approvals required
     - Dismisses stale pull request approvals when new commits pushed
     - Require approval from code owners
  
  2. Require status checks to pass
     - Require branches to be up-to-date before merging
     - Status checks required:
       * CI/CD pipeline (tests, builds)
       * Security scanning (GitLeaks, SAST)
       * Code quality gates (linting, coverage thresholds)
       * All checks must pass before merge eligible
  
  3. Require branches to be up-to-date before merging
     - Prevents merging stale branches
     - Ensures all tests run against latest code
  
  4. Require conversation resolution before merging
     - All comments must be resolved
     - Prevents merging with unaddressed concerns
  
  5. Restrict who can push to matching branches
     - Only Admins can force-push (emergency only)
     - Enforces workflow through PRs
  
  6. Block direct pushes
     - All changes must go through PR process
     - No exceptions (admin force-push logged and audited)
```


#### **Develop/Staging Branch** (Integration)

**Enforcement Level:** MEDIUM - Collaborative workflow

```yaml
Branch: develop

Protection Rules:
  1. Require pull request reviews before merging
     - Minimum 1 approval required
     - Allows faster iteration for non-production
  
  2. Require status checks to pass
     - CI/CD pipeline must pass
     - Security scanning (GitLeaks) mandatory
     - Code quality checks
  
  3. Require conversation resolution
     - Feedback must be addressed
  
  4. Dismiss stale approvals on new commits
     - Ensures fresh review of changes
  
  5. No linear history requirement
     - Allows merge commits for better history tracking
```

### Branch Protection Rule Enforcement

```bash
# Configuration via GitHub API/UI

# Main branch enforcement
gh api repos/{owner}/{repo}/branches/main/protection \
  --input - << 'EOF'
{
  "required_status_checks": {
    "strict": true,
    "contexts": ["ci/build", "security/gitleaks", "code-quality/coverage"]
  },
  "required_pull_request_reviews": {
    "dismiss_stale_reviews": true,
    "require_code_owner_reviews": true,
    "required_approving_review_count": 2
  },
  "enforce_admins": true,
  "restrict_who_can_push": {
    "teams": ["admin-team"]
  },
  "require_linear_history": true,
  "required_conversation_resolution": true,
  "required_deployments": {
    "strict_required_status_checks_policy": true,
    "environments": ["staging"]
  }
}
EOF
```

### Branch Naming Conventions

Protected branches enforce naming patterns:

```
Main Production:      main
Integration:          develop
Feature Work:         feature/tkk-###-description
Bug Fixes:           bugfix/tkk-###-description
Hotfixes:            hotfix/tkk-###-description
Releases:            release/v*.*.* (semver)
Documentation:       docs/tkk-###-description
```

---

## 4. Security Best Practices

### 4.1 Secrets Management

#### **Problem Statement**
Secrets (API keys, database credentials, tokens) must never be committed to version control, even in private repositories. Compromised secrets can lead to data breaches, unauthorized access, and compliance violations.

#### **Implementation Strategy**

**Never Commit Secrets:**

```bash
# ❌ WRONG - Never do this
OPENAI_API_KEY=sk-1234567890abcdef  # In code
DATABASE_URL=postgresql://user:password@host  # In config

# ✅ CORRECT - Use environment variables
echo "OPENAI_API_KEY=sk-1234567890abcdef" >> .env
echo ".env" >> .gitignore  # Ensure .env is ignored
```

**GitHub Secrets Management:**

1. **Repository Secrets**
   ```
   Location: Settings → Secrets and variables → Repository secrets
   
   Configured Secrets:
   - API_KEY_OPENAI
   - DATABASE_PASSWORD
   - AWS_ACCESS_KEY_ID
   - AWS_SECRET_ACCESS_KEY
   - PAT_GITHUB (for actions)
   - DEPLOY_TOKEN
   
   Access Level:
   - Only available to GitHub Actions workflows
   - Not accessible via API calls outside workflows
   - Automatically masked in logs
   ```

2. **Environment Secrets**
   ```
   Location: Settings → Secrets and variables → Environment secrets
   
   Production Environment:
   - Restricted to Production deployment jobs only
   - Requires special access approval
   - Separate credentials from development
   
   Staging Environment:
   - Available to staging deployments
   - Can be less restricted than production
   - Used for pre-production validation
   
   Development Environment:
   - Used locally (through .env files)
   - Never committed to repository
   ```

#### **Secret Detection Controls**

See Section 4.3 (GitLeaks Strategy) for automated secret detection.

### 4.2 Personal Access Tokens (PATs)

#### **What is a PAT?**

A Personal Access Token is a GitHub-generated credential that provides programmatic access to your account. It's used for:
- Git operations via command line (cloning, pushing)
- API calls to GitHub
- GitHub Actions workflows
- CI/CD pipelines

#### **PAT Configuration for Our Project**

**Token Generation:**

```bash
# Navigate to GitHub Settings → Developer settings → Personal access tokens → Tokens (classic)
# OR → Fine-grained personal access tokens (recommended)

# For this project, required scopes:
✅ repo (full control of private repositories)
✅ read:org (read org data)
✅ workflow (manage Actions workflows)
❌ admin:repo_hook (not needed for this project)
❌ delete_repo (never enable)
```

**PAT Security Rules:**

````
1. Token Generation
   ✅ Use fine-grained tokens with minimal scope
   ✅ Set expiration (30 days)
   ✅ Use unique token per use case
   ❌ Never share PAT in messages/docs
   ❌ Never commit PAT to repository
````

### 4.3 Pre-Commit Strategy: GitLeaks

#### **What is GitLeaks?**

GitLeaks is an open-source tool that scans repositories for secrets (API keys, passwords, tokens) before they're committed. It prevents accidental secret leakage at the source.

#### **Installation & Setup**

```bash
# Install GitLeaks
brew install gitleaks  # macOS
# OR
sudo apt-get install gitleaks  # Linux
# OR via pip
pip install detect-secrets

# Install as git pre-commit hook
git config core.hooksPath .githooks

# Create hook directory
mkdir -p .githooks
chmod +x .githooks
```

#### **Pre-Commit Hook Configuration**

**File: `.githooks/pre-commit`**

```bash
#!/bin/bash
# Pre-commit hook for GitLeaks secret detection

echo "🔍 Running GitLeaks secret detection..."

# Run GitLeaks scan on staged files
gitleaks detect --verbose --no-git \
  --log-level debug \
  -b HEAD \
  --exit-code 1

if [ $? -eq 1 ]; then
    echo "❌ GitLeaks found potential secrets in your commit!"
    echo ""
    echo "Secrets detected. Commit aborted to prevent secret leakage."
    echo ""
    echo "If this is a false positive:"
    echo "1. Exclude the pattern in .gitleaksignore"
    echo "2. Or remove the secret and use environment variables"
    echo ""
    exit 1
else
    echo "✅ GitLeaks scan passed - no secrets detected"
    exit 0
fi
```

### 4.4 Code Owners & Security Review

**File: `.github/CODEOWNERS`**

```
# Code Owners - Enforce security review for sensitive changes

# Default reviewers for all changes
* @hiring-company-lead @our-company-lead

# Sensitive areas require all maintainers
/src/data_processing/ @hiring-company-lead @our-company-lead @maintainer-1 @maintainer-2
/src/authentication/ @hiring-company-lead @our-company-lead
/src/cv_parsing/ @maintainer-1 @maintainer-2
/.github/workflows/ @hiring-company-lead @our-company-lead

# Security & configuration files
.github/workflows/*.yml @hiring-company-lead @our-company-lead
.gitleaks.toml @hiring-company-lead @our-company-lead
.github/dependabot.yml @hiring-company-lead

# Documentation
docs/ @documentation-owner @hiring-company-lead
```

### 4.5 Additional Security Measures

#### **Dependency Scanning**

```yaml
# .github/dependabot.yml
version: 2
updates:
  - package-ecosystem: "pip"
    directory: "/"
    schedule:
      interval: "weekly"
    reviewers:
      - "hiring-company-lead"
      - "our-company-lead"
    security-updates-only: true
    auto-merge: false

  - package-ecosystem: "github-actions"
    directory: "/"
    schedule:
      interval: "weekly"
```

---

## 5. Access Control

### Access Request Process

**For any new developer to gain access:**

1. **Documentation**
   - Access request filed with both company approvals
   - Signed authorization from both companies
   - Kept in audit trail (GitHub organization logs)

2. **Onboarding**
   - Repository collaborator added with appropriate role
   - Credentials provided securely
   - NDA/Confidentiality agreement signed

3. **Offboarding**
   - Immediate removal upon contract termination
   - All credentials revoked
   - Audit log entry created

### Access Revocation Checklist

When a team member leaves the project:

```
☐ Remove from repository collaborators
☐ Revoke GitHub access token
☐ Revoke API keys/credentials
☐ Remove from organization teams
☐ Revoke SSH key access
☐ Check audit logs for last activity
☐ Document in security log
☐ Notify both company admins
☐ Archive conversation history
☐ Verify no leftover access points
```

---

## Conclusion

This governance framework ensures:

1. **Security:** Sensitive CV data is protected through access controls and secret management
2. **Compliance:** GDPR/CCPA-ready with appropriate safeguards
3. **Integrity:** Code quality maintained through branch protection and peer review
4. **Least Privilege:** Team members have only necessary access

The combination of **private repository visibility**, **role-based access control**, **branch protection rules**, and **automated security scanning** creates a comprehensive security posture appropriate for handling sensitive data.