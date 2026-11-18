// PII pre-filter: cheap rules first, AI second.
// Parses ugc.json and flags emails and phone numbers with regex before anything is sent to Claude.
// Claude still checks for PII the regex can't see (street addresses, names), but these flags are
// deterministic: if the regex fires, the item can never be auto-approved.

const raw = $('Get ugc.json').first().json.data;
const ugc = typeof raw === 'string' ? JSON.parse(raw) : raw;

const EMAIL = /[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}/i;
// Nordic phone numbers: 8 digits, optional +45/+46/+47 prefix, spaces or dashes allowed.
// Needs 8+ digits so order numbers (e.g. 48213) are not flagged.
const PHONE = /(?:\+\d{2}[\s-]?)?(?:\d[\s-]?){7,10}\d/;

return ugc.map((item) => {
  const pii_types = [];
  if (EMAIL.test(item.text)) pii_types.push('email');
  if (PHONE.test(item.text)) pii_types.push('phone');
  return {
    json: {
      ...item,
      pii_detected: pii_types.length > 0,
      pii_types,
    },
  };
});
