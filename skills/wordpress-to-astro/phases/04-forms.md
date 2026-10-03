# Phase 4: Forms

Write `docs/forms.md`. When raising forms with the user, explain in plain English that the form plugin both shows the form and *processes* the answers (spam checks, email or CRM delivery, thank-you page), that a static site cannot process them, and what the options are (`reference/feature-translation.md`, Forms).

- Find every page containing a `<form>` (including embedded form-plugin markup such as Gravity Forms, CF7, HubSpot, Salesforce web-to-lead).
- For each form: page URLs, action, method, hidden fields, every field's name/type/label/required status, and the plugin or provider if identifiable. Distinguish values that are per-render tokens (nonces, signed state, captcha response fields) from stable ones.
- Group forms that share common fields or are the same form reused across pages.
- **Keep the form markup exactly as served.** In the Astro source, add a clearly visible comment immediately above each form: `<!-- TODO(manual): Hook this form up to Salesforce and server-side code. See docs/forms.md#<form-id> -->`. Do not wire up submission. The Astro source does not exist until Phase 5, so add the comments there. If the markup is stored as verbatim fragments, the comment will be emitted into the built HTML: log that in `docs/deviations.md` as an additive comment and have the verifier ignore it.

### Optional: submit forms to capture the flow (`--submit-forms` only)

Skip this whole subsection unless the flag is set and the authorisation in `policies/before-starting.md` was confirmed. When it is set, submit each **distinct** form once (a form reused across pages is submitted once, from one page) and record what happens.

**Dummy data rules**
- Every email address uses `@example.com`, and is unique per form so submissions can be traced (for example `migration-test+<form-id>@example.com`). No other domain, ever.
- Use obviously fake values: name "Test Person", company "Example Ltd", website `https://example.com`, a reserved fictional phone number (UK `07700 900123`, US `555-0100`), and a message that says it is an automated migration test and can be ignored.
- Choose valid options for selects, radios and checkboxes. Leave honeypot and hidden fields as served.

**Never submit**
- Forms involving payment, checkout or card details, login, registration, account creation or password reset, or file uploads.
- Forms protected by a CAPTCHA or other bot detection. Do not attempt to bypass them.
- Search forms (these are handled in Phase 8).
- Any form that cannot be submitted with the default tools, such as one that needs a JavaScript-driven browser flow. Record these as "not submitted: requires browser".

For each form that is submitted, add an "Observed flow" entry to `docs/forms.md`: the request URL and method, the field names and dummy values sent, any validation messages seen when required fields are missing, the response status, any redirect chain, the confirmation or thank-you page (URL, title, and cached HTML), and each step of a multi-step form. Add thank-you and other result pages to `docs/site-structure.md` as pages (they are often not linked anywhere) and cache them like any other page.

Keep a record of every submission in `docs/forms-submission-log.md`: timestamp, form id, page URL, endpoint, and the exact dummy values used, so the site owner can find and delete the test entries. If a submission fails or the site blocks it, log that and move on without retrying.
