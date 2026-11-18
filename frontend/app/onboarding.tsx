import React, { useState } from "react";
import { FlatList, Modal, Platform, Text, TouchableOpacity, View } from "react-native";
import { Stack, useRouter } from "expo-router";
import { Ionicons } from "@expo/vector-icons";
import { useUserStore } from "../src/store/userStore";
import client from "../src/api/client";
import { notify } from "../src/utils/dialog";
import { Button, Card, Chip, colors, Row, Screen, Section, Segmented, Title } from "../src/ui";

const INJURY_OPTIONS = [
  { id: "knee", label: "무릎" },
  { id: "lower_back", label: "허리" },
  { id: "shoulder", label: "어깨" },
  { id: "wrist", label: "손목" },
  { id: "ankle", label: "발목" },
  { id: "elbow", label: "팔꿈치" },
];

const CURRENT_YEAR = new Date().getFullYear();

export default function Onboarding() {
  const router = useRouter();
  const { setUserId, setIsOnboarded } = useUserStore();
  const [picker, setPicker] = useState<null | "birth" | "height" | "weight">(null);
  const [timeOpen, setTimeOpen] = useState(false);
  const [saving, setSaving] = useState(false);

  const [form, setForm] = useState({
    user_id: "user_" + Math.random().toString(36).slice(2, 7),
    birth_year: 1999,
    sex: "male",
    height_cm: 175,
    weight_kg: 70,
    goal: "muscle_gain",
    experience_level: "beginner",
    injuries: [] as string[],
    weekly_available_days: 3,
    place_preference: "gym",
    equipment: ["dumbbell", "barbell"],
    workout_time: "08:00",
  });
  const set = (patch: Partial<typeof form>) => setForm((f) => ({ ...f, ...patch }));
  const toggleInjury = (id: string) =>
    set({ injuries: form.injuries.includes(id) ? form.injuries.filter((x) => x !== id) : [...form.injuries, id] });

  const submit = async () => {
    setSaving(true);
    try {
      const response = await client.post("/api/onboarding/", { ...form, age: CURRENT_YEAR - form.birth_year });
      if (response.status === 200) {
        // 운동 알림은 기기 앱에서만 예약한다
        if (Platform.OS !== "web") {
          try {
            const { registerForPushNotificationsAsync, scheduleWorkoutNotification } = require("../src/services/notificationService");
            await registerForPushNotificationsAsync();
            const [hour, minute] = form.workout_time.split(":").map(Number);
            await scheduleWorkoutNotification(hour, minute);
          } catch (notifError) {
            console.log("Notification setup skipped or failed:", notifError);
          }
        }
        setUserId(form.user_id);
        setIsOnboarded(true);
        router.replace("/");
      }
    } catch (error) {
      console.error(error);
      notify("저장하지 못했어요", "잠시 뒤에 다시 시도해 주세요.");
    } finally {
      setSaving(false);
    }
  };

  const pickers = {
    birth: { title: "출생연도", unit: "년", data: Array.from({ length: 71 }, (_, i) => CURRENT_YEAR - 15 - i), key: "birth_year" as const },
    height: { title: "키", unit: "cm", data: Array.from({ length: 81 }, (_, i) => i + 140), key: "height_cm" as const },
    weight: { title: "몸무게", unit: "kg", data: Array.from({ length: 111 }, (_, i) => i + 40), key: "weight_kg" as const },
  };
  const active = picker ? pickers[picker] : null;

  const valueText = (v: string) => (
    <View className="flex-row items-center">
      <Text className="text-[15px] font-semibold text-ink mr-1">{v}</Text>
      <Ionicons name="chevron-forward" size={16} color={colors.muted} />
    </View>
  );

  return (
    <Screen footer={<Button label="시작하기" onPress={submit} loading={saving} />}>
      <Stack.Screen options={{ title: "기본 정보" }} />
      <Title sub="추천할 운동의 강도와 종류를 정하는 데 씁니다. 나중에 내 정보에서 바꿀 수 있어요.">나에 대해 알려 주세요</Title>

      <Section label="성별">
        <Segmented
          options={[{ label: "남성", value: "male" }, { label: "여성", value: "female" }]}
          value={form.sex}
          onChange={(v) => set({ sex: v })}
        />
      </Section>

      <Section label="신체 정보">
        <View className="border-t border-line">
          <Row label="출생연도" value={valueText(`${form.birth_year}년`)} onPress={() => setPicker("birth")} />
          <Row label="키" value={valueText(`${form.height_cm}cm`)} onPress={() => setPicker("height")} />
          <Row label="몸무게" value={valueText(`${form.weight_kg}kg`)} onPress={() => setPicker("weight")} last />
        </View>
      </Section>

      <Section label="운동 목표">
        <Segmented
          options={[
            { label: "체중 감량", value: "weight_loss" },
            { label: "근력 증진", value: "muscle_gain" },
            { label: "건강 유지", value: "fitness" },
          ]}
          value={form.goal}
          onChange={(v) => set({ goal: v })}
        />
      </Section>

      <Section label="운동 경험">
        <Segmented
          options={[
            { label: "초급", value: "beginner" },
            { label: "중급", value: "intermediate" },
            { label: "상급", value: "advanced" },
          ]}
          value={form.experience_level}
          onChange={(v) => set({ experience_level: v })}
        />
      </Section>

      <Section label="주로 운동하는 곳">
        <Segmented
          options={[{ label: "헬스장", value: "gym" }, { label: "집", value: "home" }]}
          value={form.place_preference}
          onChange={(v) => set({ place_preference: v })}
        />
      </Section>

      <Section label="일주일에 운동할 수 있는 날" right={<Text className="text-[13px] font-semibold text-ink">{form.weekly_available_days}일</Text>}>
        <Segmented
          options={[1, 2, 3, 4, 5, 6, 7].map((d) => ({ label: String(d), value: d }))}
          value={form.weekly_available_days}
          onChange={(v) => set({ weekly_available_days: v })}
        />
      </Section>

      <Section label="주의할 부위 (선택)">
        <View className="flex-row flex-wrap -m-1">
          {INJURY_OPTIONS.map((o) => (
            <Chip key={o.id} label={o.label} selected={form.injuries.includes(o.id)} onPress={() => toggleInjury(o.id)} />
          ))}
        </View>
        <Text className="text-[13px] text-zinc-500 mt-2">고른 부위에 무리가 가는 운동은 추천하지 않아요.</Text>
      </Section>

      {Platform.OS !== "web" ? (
        <Section label="운동 알림">
          <View className="border-t border-line">
            <Row label="매일" value={valueText(form.workout_time)} onPress={() => setTimeOpen(true)} last />
          </View>
        </Section>
      ) : null}

      {/* 숫자 고르기 */}
      <Modal visible={!!active} transparent animationType="slide" onRequestClose={() => setPicker(null)}>
        <View className="flex-1 justify-end bg-black/40">
          <View className="bg-white rounded-t-2xl h-[55%] w-full self-center" style={{ maxWidth: 480 }}>
            <View className="flex-row justify-between items-center px-5 h-14 border-b border-line">
              <Text className="text-[16px] font-semibold text-ink">{active?.title}</Text>
              <TouchableOpacity onPress={() => setPicker(null)}>
                <Text className="text-[15px] text-zinc-500">닫기</Text>
              </TouchableOpacity>
            </View>
            {active ? (
              <FlatList
                data={active.data}
                keyExtractor={(item) => String(item)}
                initialScrollIndex={Math.max(0, active.data.indexOf(form[active.key]) - 3)}
                getItemLayout={(_, i) => ({ length: 48, offset: 48 * i, index: i })}
                renderItem={({ item }) => {
                  const on = form[active.key] === item;
                  return (
                    <TouchableOpacity
                      onPress={() => {
                        set({ [active.key]: item } as any);
                        setPicker(null);
                      }}
                      className={`h-12 px-5 flex-row items-center justify-between ${on ? "bg-brand-soft" : ""}`}
                    >
                      <Text className={`text-[16px] ${on ? "font-semibold text-brand" : "text-ink"}`}>
                        {item}
                        {active.unit}
                      </Text>
                      {on ? <Ionicons name="checkmark" size={18} color={colors.brand} /> : null}
                    </TouchableOpacity>
                  );
                }}
              />
            ) : null}
          </View>
        </View>
      </Modal>

      {/* 알림 시간 (기기 앱만) */}
      {Platform.OS !== "web" && timeOpen ? (
        <TimeSheet
          value={form.workout_time}
          onClose={() => setTimeOpen(false)}
          onChange={(t) => set({ workout_time: t })}
        />
      ) : null}
    </Screen>
  );
}

function TimeSheet({ value, onChange, onClose }: { value: string; onChange: (t: string) => void; onClose: () => void }) {
  const DateTimePicker = require("@react-native-community/datetimepicker").default;
  const [h, m] = value.split(":").map(Number);
  const date = new Date(2026, 0, 1, h, m);
  return (
    <Modal visible transparent animationType="fade" onRequestClose={onClose}>
      <View className="flex-1 justify-center items-center bg-black/40 px-8">
        <Card style={{ width: "100%", alignItems: "center", padding: 20 }}>
          <Text className="text-[16px] font-semibold text-ink mb-4">알림 시간</Text>
          <DateTimePicker
            value={date}
            mode="time"
            is24Hour
            display={Platform.OS === "ios" ? "spinner" : "default"}
            onChange={(_: any, d?: Date) => {
              if (Platform.OS !== "ios") onClose();
              if (d) onChange(`${String(d.getHours()).padStart(2, "0")}:${String(d.getMinutes()).padStart(2, "0")}`);
            }}
            textColor={colors.ink}
            style={{ width: 250, height: 180 }}
          />
          <View className="w-full mt-4">
            <Button label="확인" onPress={onClose} />
          </View>
        </Card>
      </View>
    </Modal>
  );
}
