import assert from "node:assert/strict";
import { test } from "node:test";

import { decodePreferenceDraft, preferenceCommand, preferenceFields } from "../../features/learner/preference-fields.ts";
import type { LearningPreferences } from "../../lib/api/learner.ts";

const defaults: LearningPreferences = {
  locale: "vi",
  timezone: "UTC",
  current_cefr: null,
  target_kind: null,
  target_code: null,
  exam_date: null,
  default_accent: "system",
  ai_opt_in: false,
  social_opt_in: false,
  onboarding_completed_at: null,
  revision: 0,
};

test("a new learner can save an IANA alias without choosing an exam", () => {
  const fields = { ...preferenceFields(defaults), current_cefr: "B1", timezone: " Asia/Ho_Chi_Minh " };
  assert.deepEqual(preferenceCommand(fields, defaults), {
    body: {
      current_cefr: "B1",
      target_kind: null,
      target_code: null,
      exam_date: null,
      timezone: "Asia/Ho_Chi_Minh",
      locale: "vi",
      default_accent: "system",
      ai_opt_in: false,
      social_opt_in: false,
      expected_revision: 0,
    },
  });
});

test("invalid CEFR, timezone, and missing exam identify the relevant field", () => {
  const fields = { ...preferenceFields(defaults), current_cefr: "A1" };
  for (const [change, field] of [
    [{ current_cefr: "C3" }, "current_cefr"],
    [{ timezone: "Asia//Tokyo" }, "timezone"],
    [{ timezone: "+07:00" }, "timezone"],
    [{ target_kind: "exam" }, "target_code"],
  ] as const) {
    const result = preferenceCommand({ ...fields, ...change }, defaults);
    assert.equal("issue" in result && result.issue.field, field);
  }
});

test("changing the target exam discards its old date and preserves settings managed by the server", () => {
  const current: LearningPreferences = {
    ...defaults,
    current_cefr: "B2",
    target_kind: "exam",
    target_code: "toeic",
    exam_date: "2027-06-01",
    onboarding_completed_at: "2026-11-20T10:00:00Z",
    ai_opt_in: true,
    social_opt_in: true,
    revision: 4,
  };
  const fields = preferenceFields(current);
  const retain = preferenceCommand(fields, current);
  assert.equal("body" in retain && retain.body.exam_date, "2027-06-01");

  const update = preferenceCommand({ ...fields, target_code: "ielts" }, current);
  assert.ok("body" in update);
  assert.equal(update.body.exam_date, null);
  assert.equal(update.body.ai_opt_in, true);
  assert.equal(update.body.social_opt_in, true);
  assert.equal(update.body.expected_revision, 4);
});

test("an onboarding draft restores only on its original revision and ignores malformed storage", () => {
  const fields = { ...preferenceFields(defaults), current_cefr: "A2", timezone: "Asia/Tokyo" };
  const draft = JSON.stringify({ fields, revision: 0 });
  assert.deepEqual(decodePreferenceDraft(draft, defaults), fields);
  assert.equal(decodePreferenceDraft(draft, { ...defaults, revision: 1 }), undefined);
  assert.equal(decodePreferenceDraft("{", defaults), undefined);
  assert.equal(decodePreferenceDraft(JSON.stringify({ fields: { locale: "vi" }, revision: 0 }), defaults), undefined);
});
