import type { FieldIssue } from "../auth/flow";
import type { LearningPreferences, PreferencesCommand } from "../../lib/api/learner";

export const levels = ["A1", "A2", "B1", "B2", "C1", "C2"] as const;
export const timeZoneIssue: FieldIssue = { field: "timezone", message: "Nhập múi giờ IANA hợp lệ, ví dụ Asia/Ho_Chi_Minh." };
const goals = ["general", "exam"] as const;
const exams = ["ielts", "toeic"] as const;
const locales = ["vi", "en"] as const;
const accents = ["system", "uk", "us"] as const;

const fieldNames = ["current_cefr", "target_kind", "target_code", "timezone", "locale", "default_accent"] as const;
type PreferenceValues = Record<(typeof fieldNames)[number], string>;

export function preferenceFields(preferences: LearningPreferences): PreferenceValues {
  return {
    current_cefr: preferences.current_cefr ?? "",
    target_kind: preferences.target_kind ?? "",
    target_code: preferences.target_code ?? "",
    timezone: preferences.timezone,
    locale: preferences.locale,
    default_accent: preferences.default_accent,
  };
}

function includes<const Values extends readonly string[]>(values: Values, value: string): value is Values[number] {
  return (values as readonly string[]).includes(value);
}

export function preferenceCommand(fields: PreferenceValues, previous: LearningPreferences):
  { body: PreferencesCommand } | { issue: FieldIssue } {
  const { current_cefr, target_kind, target_code, default_accent, locale } = fields;
  const timezone = fields.timezone.trim();
  const goal = includes(goals, target_kind) ? target_kind : null;
  const exam = goal === "exam" && includes(exams, target_code) ? target_code : null;

  if (!includes(levels, current_cefr)) {
    return { issue: { field: "current_cefr", message: "Chọn trình độ tiếng Anh hiện tại của bạn." } };
  }
  if (target_kind && !goal) {
    return { issue: { field: "target_kind", message: "Chọn mục tiêu học trong danh sách." } };
  }
  if (goal === "exam" && !exam) {
    return { issue: { field: "target_code", message: "Chọn kỳ thi bạn đang chuẩn bị." } };
  }
  // The API checks membership using its timezone database, which may be newer than the browser's.
  if (timezone.length > 128 || !/^[A-Za-z][A-Za-z0-9_+-]*(\/[A-Za-z0-9_+-]+)*$/.test(timezone)) {
    return { issue: timeZoneIssue };
  }
  if (!includes(locales, locale)) {
    return { issue: { field: "locale", message: "Chọn tiếng Việt hoặc tiếng Anh." } };
  }
  if (!includes(accents, default_accent)) {
    return { issue: { field: "default_accent", message: "Chọn giọng tiếng Anh trong danh sách." } };
  }

  return {
    body: {
      current_cefr,
      target_kind: goal,
      target_code: exam,
      exam_date: exam && exam === previous.target_code ? previous.exam_date : null,
      timezone,
      locale,
      default_accent,
      ai_opt_in: previous.ai_opt_in,
      social_opt_in: previous.social_opt_in,
      expected_revision: previous.revision,
    },
  };
}

export function decodePreferenceDraft(raw: string | null, previous: LearningPreferences): PreferenceValues | undefined {
  if (!raw) return;
  try {
    const { revision, fields } = JSON.parse(raw);
    if (revision !== previous.revision || !fields || typeof fields !== "object") return;

    if (fieldNames.every((name) => typeof fields[name] === "string" && fields[name].length <= 128)) {
      return fields;
    }
  } catch {
    // Draft storage is optional and may contain data from a previous browser version.
  }
}
