"use client";

import { useRef, useState, useSyncExternalStore } from "react";

import { LearnerApiError, putLearningPreferences, type LearningPreferences } from "@/lib/api/learner";

import { decodePreferenceDraft, levels, preferenceCommand, preferenceFields, timeZoneIssue } from "./preference-fields";
import { LearnerField, SaveForm } from "./save-form";

const timeZones = [
  "Asia/Ho_Chi_Minh", "Asia/Bangkok", "Asia/Singapore", "Asia/Tokyo", "Australia/Sydney",
  "Europe/London", "Europe/Paris", "America/New_York", "America/Los_Angeles", "UTC",
];

const levelsLabel = {
  A1: "Mới bắt đầu", A2: "Sơ cấp", B1: "Trung cấp", B2: "Trung cấp cao",
  C1: "Nâng cao", C2: "Thành thạo",
};

const subscribeDraft = () => () => {};
const serverDraft = () => null;

function readDraft(key: string | null) {
  if (!key) return null;
  try {
    return window.sessionStorage.getItem(key);
  } catch {
    return null;
  }
}

function saveDraft(key: string | null, value: string | null) {
  if (!key) return;
  try {
    if (value === null) window.sessionStorage.removeItem(key);
    else window.sessionStorage.setItem(key, value);
  } catch {
    // The form remains usable when the browser blocks draft storage.
  }
}

export function PreferenceForm({ initial, userId, onboarding = false }: {
  initial: LearningPreferences;
  userId: string;
  onboarding?: boolean;
}) {
  const [current, setCurrent] = useState(initial);
  const [edits, setEdits] = useState<ReturnType<typeof preferenceFields>>();
  const requestKey = useRef<{ command: string; key: string }>(null);
  const draftKey = onboarding ? `nhip-anh:onboarding:${userId}` : null;
  const rawDraft = useSyncExternalStore(subscribeDraft, () => readDraft(draftKey), serverDraft);
  const fields = edits ?? decodePreferenceDraft(rawDraft, current) ?? preferenceFields(current);

  function update(name: keyof typeof fields, value: string) {
    const next = { ...fields, [name]: value };
    setEdits(next);
    saveDraft(draftKey, JSON.stringify({ revision: current.revision, fields: next }));
  }

  async function save() {
    const result = preferenceCommand(fields, current);
    if ("issue" in result) return result.issue;

    const command = JSON.stringify(result.body);
    if (requestKey.current?.command !== command) {
      requestKey.current = { command, key: crypto.randomUUID() };
    }
    let saved: LearningPreferences;
    try {
      saved = await putLearningPreferences(userId, result.body, requestKey.current.key);
    } catch (error) {
      if (error instanceof LearnerApiError && error.status === 422 && result.body.timezone !== current.timezone) {
        return timeZoneIssue;
      }
      throw error;
    }
    if (onboarding) {
      saveDraft(draftKey, null);
      window.location.replace("/dashboard");
    } else {
      setCurrent(saved);
      setEdits(undefined);
    }
  }

  return (
    <SaveForm
      label={onboarding ? "Lưu và tiếp tục" : "Lưu tùy chọn học tập"}
      successMessage={onboarding ? "Đã lưu hồ sơ học tập." : "Đã lưu tùy chọn học tập."}
      action={save}
    >
      {(issue) => (
        <>
          <fieldset className="min-w-0 space-y-4">
            <legend className="mb-3 text-lg/6 font-semibold">Kế hoạch học</legend>
            <LearnerField label="Trình độ hiện tại" name="current_cefr" issue={issue}>
              {(props) => (
                <select {...props} required value={fields.current_cefr} onChange={(event) => update("current_cefr", event.target.value)}>
                  <option value="" disabled>Chọn trình độ</option>
                  {levels.map((level) => <option key={level} value={level}>{level} · {levelsLabel[level]}</option>)}
                </select>
              )}
            </LearnerField>
            <LearnerField label="Mục tiêu học" name="target_kind" issue={issue}>
              {(props) => (
                <select {...props} value={fields.target_kind} onChange={(event) => update("target_kind", event.target.value)}>
                  <option value="">Chưa đặt mục tiêu</option>
                  <option value="general">Cải thiện tiếng Anh nói chung</option>
                  <option value="exam">Chuẩn bị cho kỳ thi</option>
                </select>
              )}
            </LearnerField>
            {fields.target_kind === "exam" && (
              <LearnerField label="Kỳ thi" name="target_code" issue={issue}>
                {(props) => (
                  <select {...props} required value={fields.target_code} onChange={(event) => update("target_code", event.target.value)}>
                    <option value="" disabled>Chọn kỳ thi</option>
                    <option value="ielts">IELTS</option>
                    <option value="toeic">TOEIC</option>
                  </select>
                )}
              </LearnerField>
            )}
          </fieldset>
          <fieldset className="min-w-0 space-y-4">
            <legend className="mb-3 text-lg/6 font-semibold">Khu vực và ngôn ngữ</legend>
            <LearnerField label="Múi giờ" name="timezone" hint="Chọn hoặc nhập đúng tên IANA, ví dụ Asia/Ho_Chi_Minh." issue={issue}>
              {(props) => (
                <>
                  <input
                    {...props}
                    autoCapitalize="none"
                    autoComplete="off"
                    list={`${props.id}-zones`}
                    maxLength={128}
                    required
                    spellCheck={false}
                    value={fields.timezone}
                    onChange={(event) => update("timezone", event.target.value)}
                  />
                  <datalist id={`${props.id}-zones`}>
                    {timeZones.map((zone) => <option key={zone} value={zone} />)}
                  </datalist>
                </>
              )}
            </LearnerField>
            <LearnerField label="Ngôn ngữ ưu tiên" name="locale" issue={issue}>
              {(props) => (
                <select {...props} value={fields.locale} onChange={(event) => update("locale", event.target.value)}>
                  <option value="vi">Tiếng Việt</option>
                  <option value="en" lang="en">English</option>
                </select>
              )}
            </LearnerField>
            {!onboarding && (
              <LearnerField label="Giọng tiếng Anh" name="default_accent" issue={issue}>
                {(props) => (
                  <select {...props} value={fields.default_accent} onChange={(event) => update("default_accent", event.target.value)}>
                    <option value="system">Theo hệ thống</option>
                    <option value="uk">Anh</option>
                    <option value="us">Mỹ</option>
                  </select>
                )}
              </LearnerField>
            )}
          </fieldset>
        </>
      )}
    </SaveForm>
  );
}
