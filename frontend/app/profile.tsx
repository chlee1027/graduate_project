import React, { useEffect, useState } from "react";
import { Modal, ScrollView, Text, TextInput, TouchableOpacity, View } from "react-native";
import { Stack, useRouter } from "expo-router";
import { useUserStore } from "../src/store/userStore";
import client from "../src/api/client";
import { confirmAction, notify } from "../src/utils/dialog";
import { Button, Card, colors, Label, Loading, Row, Screen, Section, Segmented, Stat } from "../src/ui";

const GOAL: Record<string, string> = { muscle_gain: "근력 증진", weight_loss: "체중 감량", fitness: "건강 유지" };
const LEVEL: Record<string, string> = { beginner: "초급", intermediate: "중급", advanced: "상급" };
const PART: Record<string, string> = {
  knee: "무릎", lower_back: "허리", shoulder: "어깨", wrist: "손목", ankle: "발목", elbow: "팔꿈치", neck: "목", hip: "골반·고관절",
};

export default function Profile() {
  const { userId, reset } = useUserStore();
  const router = useRouter();
  const [user, setUser] = useState<any>(null);
  const [stats, setStats] = useState<any>(null);
  const [logs, setLogs] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [editing, setEditing] = useState(false);
  const [saving, setSaving] = useState(false);
  const [form, setForm] = useState<any>({});

  const fetchData = async () => {
    try {
      const [userRes, statsRes, logsRes] = await Promise.all([
        client.get(`/api/user/${userId}`),
        client.get(`/api/stats/${userId}/summary`),
        client.get(`/api/stats/${userId}/weekly-details`),
      ]);
      setUser(userRes.data);
      setStats(statsRes.data);
      setLogs(logsRes.data);
      setForm({
        height_cm: String(userRes.data.height_cm),
        weight_kg: String(userRes.data.weight_kg),
        goal: userRes.data.goal,
        weekly_available_days: userRes.data.weekly_available_days,
      });
    } catch (error) {
      console.error("Failed to fetch profile data:", error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (userId) fetchData();
  }, [userId]);

  const save = async () => {
    setSaving(true);
    try {
      await client.put(`/api/user/${userId}`, {
        age: user.age,
        height_cm: parseFloat(form.height_cm),
        weight_kg: parseFloat(form.weight_kg),
        goal: form.goal,
        weekly_available_days: form.weekly_available_days,
      });
      setEditing(false);
      fetchData();
    } catch (error) {
      console.error("Update failed:", error);
      notify("저장하지 못했어요", "잠시 뒤에 다시 시도해 주세요.");
    } finally {
      setSaving(false);
    }
  };

  const logout = () =>
    confirmAction("로그아웃", "이 기기에서 로그아웃할까요? 기록은 서버에 남아요.", "로그아웃", () => {
      reset();
      router.replace("/");
    });

  if (loading && !user) return <Loading />;

  return (
    <Screen>
      <Stack.Screen options={{ title: "내 정보" }} />

      <Card>
        <View className="flex-row">
          <Stat label="누적 시간" value={stats?.total_workout_minutes ?? 0} unit="분" />
          <Stat label="완료" value={stats?.total_completed_workouts ?? 0} unit="회" />
          <Stat label="소모" value={stats?.total_calories ?? 0} unit="kcal" />
        </View>
      </Card>

      <Section
        label="기본 정보"
        right={
          <TouchableOpacity onPress={() => setEditing(true)}>
            <Text className="text-[13px] font-semibold text-brand">수정</Text>
          </TouchableOpacity>
        }
        style={{ marginTop: 28 }}
      >
        <View className="border-t border-line">
          <Row label="나이" value={`${user?.age}세`} />
          <Row label="키 · 몸무게" value={`${user?.height_cm}cm · ${user?.weight_kg}kg`} />
          <Row label="목표" value={GOAL[user?.goal] || user?.goal} />
          <Row label="숙련도" value={LEVEL[user?.experience_level] || user?.experience_level} />
          <Row label="주간 목표" value={`${user?.weekly_available_days}회`} last />
        </View>
      </Section>

      <Section label="주의할 부위">
        {user?.injuries?.length ? (
          <View className="flex-row flex-wrap -m-1">
            {user.injuries.map((p: string) => (
              <View key={p} className="m-1 h-8 px-3 rounded-lg bg-danger-soft items-center justify-center">
                <Text className="text-[13px] font-semibold text-danger">{PART[p] || p}</Text>
              </View>
            ))}
          </View>
        ) : (
          <Text className="text-[14px] text-zinc-500">없음</Text>
        )}
      </Section>

      <Section label="이번 주 기록">
        {logs.length ? (
          <View className="border-t border-line">
            {logs.map((item, i) => (
              <View key={item.log_id || i} className={`flex-row items-center py-3.5 ${i === logs.length - 1 ? "" : "border-b border-line"}`}>
                <View className="flex-1">
                  <Text className="text-[15px] font-semibold text-ink">{item.plan_name}</Text>
                  <Text className="text-[13px] text-zinc-500 mt-0.5">
                    {item.date} · {item.location === "gym" ? "헬스장" : "집"}
                  </Text>
                </View>
                <View className="items-end">
                  <Text className="text-[15px] font-semibold text-ink">{item.minutes}분</Text>
                  <Text className="text-[12px] text-zinc-500">{Math.round(item.calories)}kcal</Text>
                </View>
              </View>
            ))}
          </View>
        ) : (
          <Text className="text-[14px] text-zinc-500">이번 주 기록이 아직 없어요.</Text>
        )}
      </Section>

      <Button label="로그아웃" variant="danger" onPress={logout} />

      <Modal visible={editing} animationType="slide" transparent onRequestClose={() => setEditing(false)}>
        <View className="flex-1 justify-end bg-black/40">
          <View className="bg-white rounded-t-2xl w-full self-center" style={{ maxWidth: 480, maxHeight: "85%" }}>
            <View className="flex-row justify-between items-center px-5 h-14 border-b border-line">
              <Text className="text-[16px] font-semibold text-ink">기본 정보 수정</Text>
              <TouchableOpacity onPress={() => setEditing(false)}>
                <Text className="text-[15px] text-zinc-500">닫기</Text>
              </TouchableOpacity>
            </View>
            <ScrollView contentContainerStyle={{ padding: 20 }}>
              <View className="flex-row -mx-1.5 mb-6">
                {[
                  ["키 (cm)", "height_cm"],
                  ["몸무게 (kg)", "weight_kg"],
                ].map(([label, key]) => (
                  <View key={key} className="flex-1 mx-1.5">
                    <Label>{label}</Label>
                    <TextInput
                      value={form[key]}
                      onChangeText={(t) => setForm({ ...form, [key]: t })}
                      keyboardType="numeric"
                      className="h-12 px-4 rounded-xl border border-line text-[16px] text-ink"
                    />
                  </View>
                ))}
              </View>
              <Section label="목표">
                <Segmented
                  options={Object.entries(GOAL).map(([value, label]) => ({ label, value }))}
                  value={form.goal}
                  onChange={(v) => setForm({ ...form, goal: v })}
                />
              </Section>
              <Section label="일주일에 운동할 수 있는 날">
                <Segmented
                  options={[1, 2, 3, 4, 5, 6, 7].map((d) => ({ label: String(d), value: d }))}
                  value={form.weekly_available_days}
                  onChange={(v) => setForm({ ...form, weekly_available_days: v })}
                />
              </Section>
              <Button label="저장" onPress={save} loading={saving} />
            </ScrollView>
          </View>
        </View>
      </Modal>
    </Screen>
  );
}
