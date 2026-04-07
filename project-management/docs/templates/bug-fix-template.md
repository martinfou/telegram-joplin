---
template_version: 1.1.0
last_updated: 2025-01-27
compatible_with: [feature-request, sprint-planning, product-backlog]
requires: [markdown-support]
---

# Bug Fix Template

This is a generic template for creating defect fix items. Copy this template when reporting defects or creating defect fix items in the backlog.

## Usage

1. Copy this template
2. Assign unique ID (e.g., DEF-001, DEF-015, or use your ID format)
3. Fill in all sections, especially reproduction steps
4. Save to: `backlog/defects/[ID]-[bug-description].md`
5. Add entry to main product backlog table

---

# Bug Fix: [ID] - [Defect description]

**Status**: ⭕ Not Started  
**Priority**: 🔴 Critical / 🟠 High / 🟡 Medium / 🟢 Low  
**Story Points**: [X] (Fibonacci: 1, 2, 3, 5, 8, 13)  
**Created**: [YYYY-MM-DD]  
**Updated**: [YYYY-MM-DD]  
**Assigned Sprint**: [Sprint Number or "Backlog"]

## Description

[Clear, concise description of the defect. One or two sentences summarizing the issue.]

Example:
- User registration fails when email contains special characters
- Dashboard shows incorrect total count after filtering

## Steps to Reproduce

1. [Step 1 - specific action: e.g., "Navigate to Settings > Profile"]
2. [Step 2 - specific action: e.g., "Enter email: 'user+test@example.com'"]
3. [Step 3 - specific action: e.g., "Click 'Save' button"]
4. [Observed behavior - what happens: e.g., "Error message appears: 'Invalid email format'"]

**Tips**:
- Be specific and detailed
- Include exact values/inputs if relevant
- Number each step sequentially
- Include precondition if needed (e.g., "User must be logged in")
- Test the steps yourself to ensure they reproduce the defect
- Include environment details if relevant to reproduction

Example:
1. Navigate to Settings > Profile
2. Enter email: "user+test@example.com"
3. Click "Save"
4. Error message appears: "Invalid email format"

## Expected Behavior

[What should happen when following the steps above.]

Example:
- Email should be saved successfully with validation passing
- Success message should appear: "Profile updated"

## Actual Behavior

[What actually happens when following the steps above. Include error messages, crashes, incorrect behavior, etc.]

Example:
- Error message appears: "Invalid email format"
- Email is not saved
- User cannot proceed

## Environment

[Platform-specific environment details. Adapt this section to your application type.]

### For Web Applications:
- **Browser**: [Chrome, Firefox, Safari, etc.]
- **Browser Version**: [Version number]
- **OS**: [Windows, macOS, Linux]
- **OS Version**: [Version number]
- **Screen Resolution**: [if relevant]

### For Mobile Applications:
- **Device**: [Device model, e.g., iPhone 13, Pixel 6]
- **OS**: [iOS, Android]
- **OS Version**: [Version number, e.g., iOS 16.0, Android 14]
- **App Version**: [Version number]

### For Backend/API:
- **Server Environment**: [Production, Staging, Development]
- **API Version**: [Version number]
- **Database Version**: [if relevant]

### General:
- **User Role**: [Admin, User, Guest, etc. - if relevant]
- **Account Type**: [Free, Premium, etc. - if relevant]

## Screenshots/Logs

[If applicable, include screenshots, error logs, stack traces, or console output.]

**Format**:
- Use markdown image syntax: `![Description](path/to/image.png)`
- Use code blocks for logs:
  ```
  Error: Invalid email format
  Stack trace:
  at validateEmail() ...
  ```

## Technical Details

[Technical information about the defect. Include any relevant technical context, edge cases, or patterns observed.]

Examples:
- The email validation regex doesn't handle the '+' character
- Race condition when multiple users update the same record
- Missing null check causes NullPointerException

## Root Cause

[Analysis of the root cause. May be filled in after investigation.]

Example:
- Missing null check in validation logic
- Regex pattern doesn't include expected character class

## Solution

[Proposed or implemented solution. Include code changes, configuration updates, or workarounds.]

Example:
- Update email regex to include '+' character
- Add null check before validation
- Update unit tests to cover this case

## Reference Documents

- [Document Name 1] - [Section/Page]
- [Document Name 2] - [Section/Page]

Examples:
- API documentation - Validation rules section
- User guide - Registration section
- Architecture documentation - Authentication flow

## Technical References

[Links to specific code locations, classes, or files. Adapt format to your tech stack.]

**Format examples**:
- Class: `SecurityUtils` (or domain-specific class)
- Method: `format_error_message()` (or domain-specific method)
- File: `src/security_utils.py` (or `src/handlers/core.py`)
- Line: Line 42-45
- Test: `tests/test_greeting_bf010.py` (or domain-specific test)

## Testing

- [ ] Unit test added/updated
- [ ] Integration test added/updated
- [ ] Manual testing completed
- [ ] Tested in multiple browsers/environments (if applicable)
- [ ] Regression testing completed (if applicable)

## Notes

[Additional notes, context, workarounds, or related issues.]

Examples:
- Temporary workaround: Users can use email without '+' character
- Related defect: DEF-012 (similar issue in password validation)
- This defect affects 15% of users with email addresses containing '+'

## History

- [YYYY-MM-DD] - Created
- [YYYY-MM-DD] - Status changed to ⏳ In Progress
- [YYYY-MM-DD] - Assigned to Sprint [X]
- [YYYY-MM-DD] - Root cause identified
- [YYYY-MM-DD] - Status changed to ✅ Completed

---

## Status Values

- ⭕ **Not Started**: Item not yet started
- ⏳ **In Progress**: Item currently being worked on
- ✅ **Completed**: Item finished and verified

## Priority Levels

- 🔴 **Critical**: Blocks core functionality, data loss, security issue, must be fixed immediately
- 🟠 **High**: Significant impact on user experience, should be addressed soon
- 🟡 **Medium**: Minor impact, annoying but workaround exists
- 🟢 **Low**: Cosmetic issue, very minor impact, low priority

## Story Points Guide (Fibonacci)

- **1 Point**: Trivial fix, < 1 hour
- **2 Points**: Simple fix, 1-4 hours
- **3 Points**: Small fix, 4-8 hours
- **5 Points**: Medium fix, 1-2 days
- **8 Points**: Large fix, 2-3 days
- **13 Points**: Very complex fix, requires investigation (consider breaking down)

---

## Template Validation Checklist

Before submitting, ensure:

- [ ] All required fields are filled (Status, Priority, Story Points, Dates)
- [ ] Steps to reproduce are clear and detailed (minimum 3 steps)
- [ ] Expected behavior is clearly documented
- [ ] Actual behavior is clearly documented
- [ ] Environment details are complete (platform, OS, version, etc.)
- [ ] Screenshots/logs are included (if applicable)
- [ ] Root cause is identified (if known)
- [ ] Solution is documented (if implemented)
- [ ] Story points are estimated using Fibonacci sequence
- [ ] Priority is assigned based on impact and urgency
- [ ] Technical references are included (if applicable)
- [ ] Testing checklist is completed (if fix is implemented)
- [ ] Links to related documents are correct
- [ ] File is saved with correct naming convention: `DEF-XXX-defect-description.md`
- [ ] Entry is added to product backlog table
- [ ] Any charts/diagrams use **Mermaid** (see [documentation-standards.md](../processes/documentation-standards.md))
- [ ] Mermaid diagrams validate (wrap labels with `/`, `=`, `:`, etc. in double quotes; test at [mermaid.live](https://mermaid.live/))

