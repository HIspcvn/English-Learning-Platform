import assert from "node:assert/strict";
import { test } from "node:test";

import { isLiveResponse } from "../../features/platform-status/probe.ts";

test("recognizes the published liveness response", async () => {
  assert.equal(await isLiveResponse(Response.json({ status: "ok" })), true);
});

test("rejects an API error even if it contains an OK-looking status", async () => {
  assert.equal(await isLiveResponse(Response.json({ status: "ok" }, { status: 503 })), false);
});

test("rejects a different service's successful response", async () => {
  assert.equal(await isLiveResponse(Response.json({ status: "ready" })), false);
});

test("treats invalid JSON from the proxy as unavailable", async () => {
  assert.equal(await isLiveResponse(new Response("<html>Upstream error</html>")), false);
});
