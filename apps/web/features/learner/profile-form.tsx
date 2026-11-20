"use client";

import { useState } from "react";

import { readText } from "@/features/auth/flow";
import { patchLearnerProfile, type LearnerProfile, type ProfilePatch } from "@/lib/api/learner";

import { LearnerField, SaveForm } from "./save-form";

export function ProfileForm({ initial, userId }: { initial: LearnerProfile; userId: string }) {
  const [current, setCurrent] = useState(initial);
  const [displayName, setDisplayName] = useState(initial.display_name);
  const [bio, setBio] = useState(initial.bio ?? "");

  async function save(data: FormData) {
    const name = readText(data, "display_name").trim();
    const bio = readText(data, "bio");
    if (!name || Array.from(name).length > 80) {
      return { field: "display_name", message: "Tên hiển thị cần có từ 1 đến 80 ký tự." };
    }
    if (Array.from(bio).length > 500) {
      return { field: "bio", message: "Giới thiệu tối đa 500 ký tự." };
    }

    const patch: ProfilePatch = {};
    if (name !== current.display_name) patch.display_name = name;
    if (bio !== (current.bio ?? "")) patch.bio = bio || null;
    const saved = Object.keys(patch).length ? await patchLearnerProfile(userId, patch) : current;
    setCurrent(saved);
    setDisplayName(saved.display_name);
    setBio(saved.bio ?? "");
  }

  return (
    <SaveForm label="Lưu hồ sơ" successMessage="Đã lưu hồ sơ." action={save}>
      {(issue) => (
        <>
          <LearnerField label="Tên hiển thị" name="display_name" issue={issue}>
            {(props) => (
              <input
                {...props}
                autoComplete="nickname"
                required
                value={displayName}
                onChange={(event) => setDisplayName(event.target.value)}
              />
            )}
          </LearnerField>
          <LearnerField label="Giới thiệu" name="bio" hint="Tùy chọn, tối đa 500 ký tự." issue={issue}>
            {(props) => (
              <textarea {...props} rows={4} value={bio} onChange={(event) => setBio(event.target.value)} />
            )}
          </LearnerField>
        </>
      )}
    </SaveForm>
  );
}
