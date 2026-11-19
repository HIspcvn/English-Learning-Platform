import assert from "node:assert/strict";
import { test } from "node:test";

import { loginDestination, takeEmailProof, validateNewPassword, validatePassword } from "../../features/auth/flow.ts";

test("login uses the fixed learner route that matches onboarding status", () => {
  assert.equal(loginDestination(false), "/onboarding");
  assert.equal(loginDestination(true), "/dashboard");
});

test("email proof is taken once from the fragment and removed from the current entry", () => {
  let hash = "#token=" + "a".repeat(43);
  const location = { get hash() { return hash; }, pathname: "/verify", search: "" };
  const replacements: string[] = [];
  const history = {
    state: { router: true },
    replaceState(state: unknown, _unused: string, url?: string | URL | null) {
      assert.deepEqual(state, { router: true });
      replacements.push(String(url));
      hash = "";
    },
  };
  assert.equal(takeEmailProof(location, history), "a".repeat(43));
  assert.equal(takeEmailProof(location, history), "");
  assert.deepEqual(replacements, ["/verify"]);
});

test("malformed and repeated proof values are stripped without being used", () => {
  let replacement: string | URL | null | undefined;
  const history = { state: null, replaceState: (_state: unknown, _unused: string, url?: string | URL | null) => { replacement = url; } };
  const location = { hash: `#token=${"a".repeat(43)}&token=${"b".repeat(43)}`, pathname: "/reset-password", search: "?token=unused" };
  assert.equal(takeEmailProof(location, history), "");
  assert.equal(replacement, "/reset-password");
});

test("password validation enforces the API length and confirms the actual password", () => {
  const password = "🍏".repeat(12);
  assert.equal(validateNewPassword(password, password), undefined);
  assert.equal(validateNewPassword("🍏".repeat(11), "🍏".repeat(11))?.field, "password");
  assert.equal(validateNewPassword("a".repeat(129), "a".repeat(129))?.field, "password");
  assert.equal(validateNewPassword(password, password + " ")?.field, "confirmation");
});

test("login rejects a password outside the API's 12–128 code-point range", () => {
  assert.equal(validatePassword("🍏".repeat(11))?.field, "password");
  assert.equal(validatePassword("🍏".repeat(12)), undefined);
  assert.equal(validatePassword("🍏".repeat(128)), undefined);
  assert.equal(validatePassword("🍏".repeat(129))?.field, "password");
});
