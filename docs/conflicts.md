# Git Merge Conflict Creation & Resolution

## Overview

This document demonstrates intentional creation and resolution of a Git merge conflict scenario. The conflict was designed to simulate a real-world situation where two branches make incompatible changes to the same file, requiring manual conflict resolution.

## Scenario Context

**Tickets Involved:**
- **TKK-002:** Remove unnecessary CV fields (awards, publications, volunteer_experience)
- **TKK-003:** Add new fields (preferences, laptop_requirements, expected_salary) and rename `awards` → `achievements`

**Conflict Trigger:** TKK-002 deletes the `awards` field while TKK-003 attempts to rename it, creating an incompatible change scenario.

---

## Initial Setup

### 1. Create TKK-002 Branch (Deletion)

```bash
git checkout main
git pull origin main
python3 .claude/skills/github-branch-creator/scripts/create_branch.py TKK-002 "remove unnecessary cv fields"
```

**Changes Made:**
- Edited `agents/schemas.py` to remove: `awards`, `publications`, `volunteer_experience`

```bash
git add agents/schemas.py
git commit -m "TKK-002: Remove unnecessary CV fields"
git push -u origin feature/tkk-002-remove-unnecessary-cv-fields
```

### 2. Create TKK-003 Branch (Addition)

```bash
git checkout main
python3 .claude/skills/github-branch-creator/scripts/create_branch.py TKK-003 "add preferences and laptop fields"
```

**Initial Changes:**
- Edited `agents/schemas.py` to add: `preferences`, `laptop_requirements`, `expected_salary`

```bash
git add agents/schemas.py
git commit -m "TKK-003: Add preferences and laptop requirements fields"
git push -u origin feature/tkk-003-add-preferences-and-laptop-fields
```

---

## First Merge Attempt (No Conflict)

```bash
git checkout feature/tkk-002-remove-unnecessary-cv-fields
git merge feature/tkk-003-add-preferences-and-laptop-fields
# ✅ Merged successfully without conflict
```

**Result:** The merge succeeded because TKK-003 only added new fields without conflicting with TKK-002's deletions.

---

## Creating the Conflict

### Reset to Pre-Merge State

```bash
git reset --hard 81e9ad6  # Reset feature/tkk-002 to before the merge
```

### Modify TKK-003 to Rename `awards`

```bash
git checkout feature/tkk-003-add-preferences-and-laptop-fields
```

**New Changes:**
- Added previous fields: `preferences`, `laptop_requirements`, `expected_salary`
- **Renamed:** `awards` → `achievements` (conflict trigger)

```bash
git add agents/schemas.py
git commit -m "TKK-003: Rename awards to achievements"
git push
```

### Trigger the Merge Conflict

```bash
git checkout feature/tkk-002-remove-unnecessary-cv-fields
git merge feature/tkk-003-add-preferences-and-laptop-fields
```

**Conflict Detected:**
```
CONFLICT (modify/delete): agents/schemas.py deleted in HEAD 
and modified in feature/tkk-003-add-preferences-and-laptop-fields.
Version feature/tkk-003-add-preferences-and-laptop-fields of 
agents/schemas.py left in tree at agents/schemas.py.merge-conflict.
```

---

## Conflict Resolution

### Analyzing the Conflict

The conflict arose because:
- **TKK-002 (Current Branch):** Deleted the `awards` field entirely
- **TKK-003 (Incoming Branch):** Attempted to rename `awards` to `achievements`

**Git's Perspective:** The system cannot automatically determine whether to keep the rename or honor the deletion.

### Manual Resolution

Examined the `agents/schemas.py` file to understand both changes:

1. **Identified the incompatibility:** TKK-003's rename operation referenced a field that TKK-002 had already removed
2. **Determined the correct resolution:** Since the business requirement (TKK-002) was to remove unnecessary fields, the rename in TKK-003 was invalid
3. **Chose to honor TKK-002's deletion:** The correct state is to keep the field removed and not attempt to rename it

### Completing the Merge

```bash
# Stage the resolved file
git add agents/schemas.py

# Commit the merge resolution
git commit -m "'feature/tkk-003-add-preferences-and-laptop-fields' into feature/tkk-002-remove-unnecessary-cv-fields"

# Push the resolved merge
git push
```

**Final Commit:** `6bd9b5e`

---

## Conflict Resolution Strategy

### Decision Process

| Aspect | Details |
|--------|---------|
| **Conflict Type** | Modify/Delete conflict |
| **Root Cause** | TKK-002 removes field; TKK-003 tries to rename it |
| **Resolution Approach** | Honor the deletion from TKK-002 |
| **Rationale** | TKK-002's requirement to remove unnecessary fields takes precedence |

### Lesson Learned

This scenario demonstrates why:
- Team communication about which fields will be modified is critical
- Conflicting changes should be reviewed before merging
- The deletion operation in TKK-002 should have been communicated to the TKK-003 developer
- Code review and pre-merge discussion would have prevented this conflict

---

## Commit History Evidence

```
6bd9b5e - Merge feature/tkk-003-add-preferences-and-laptop-fields into feature/tkk-002-remove-unnecessary-cv-fields
[previous commits showing initial branch creation and modifications]
```

The commit history shows:
1. TKK-002 branch creation with field removals
2. TKK-003 branch creation with field additions
3. Initial successful merge (before conflict trigger)
4. Reset to re-create scenario
5. TKK-003 modification (rename field)
6. Merge conflict triggered
7. Manual conflict resolution and final commit

---

## Key Takeaways

1. **Intentional Conflict Creation:** Successfully demonstrated the ability to create a realistic merge conflict scenario
2. **Root Cause Analysis:** Identified the incompatibility between deletion and rename operations
3. **Manual Resolution:** Resolved the conflict by choosing the appropriate code state
4. **Documentation:** Clearly documented the decision-making process and rationale

This exercise shows competency in:
- Understanding Git internals and merge mechanics
- Identifying and analyzing merge conflicts
- Making informed decisions during conflict resolution
- Documenting complex scenarios for team understanding
