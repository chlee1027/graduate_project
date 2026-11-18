import React, { useEffect, useState } from "react";
import { Text, TouchableOpacity, View } from "react-native";
import { Stack, useLocalSearchParams, useRouter } from "expo-router";
import { useUserStore } from "../../src/store/userStore";
import client from "../../src/api/client";
import { confirmAction, notify } from "../../src/utils/dialog";
import { Button, Card, Chip, colors, Loading, Screen, Section, Segmented } from "../../src/ui";

type WorkoutPhase = "WORK" | "REST" | "FEEDBACK";

const PAIN_PARTS = [
  { id: "knee", label: "무릎" },
  { id: "lower_back", label: "허리" },
  { id: "shoulder", label: "어깨" },
  { id: "wrist", label: "손목" },
  { id: "ankle", label: "발목" },
  { id: "neck", label: "목" },
  { id: "hip", label: "골반·고관절" },
];

// RPE: 주관적 운동 강도(1 매우 쉬움 ~ 10 한계). 6~8 이 알맞은 강도.
const RPE_HINT: Record<number, string> = {
  1: "매우 쉬웠어요", 2: "쉬웠어요", 3: "쉬웠어요", 4: "가벼웠어요", 5: "적당히 가벼웠어요",
  6: "알맞았어요", 7: "알맞았어요", 8: "힘들었지만 해냈어요", 9: "아주 힘들었어요", 10: "한계였어요",
};

const formatTime = (seconds: number) => {
  const mins = Math.floor(seconds / 60);
  const secs = seconds % 60;
  return `${mins}:${secs < 10 ? "0" : ""}${secs}`;
};

export default function WorkoutSession() {
  const router = useRouter();
  const { id, recommendation_id } = useLocalSearchParams();
  const { userId } = useUserStore();

  const [loading, setLoading] = useState(true);
  const [rec, setRec] = useState<any>(null);
  const [phase, setPhase] = useState<WorkoutPhase>("WORK");
  const [elapsedSeconds, setElapsedSeconds] = useState(0);
  const [totalElapsedSeconds, setTotalElapsedSeconds] = useState(0);
  const [restTimeLeft, setRestTimeLeft] = useState(0);
  const [currentSet, setCurrentSet] = useState(1);

  const [completed, setCompleted] = useState(true);
  const [rpe, setRpe] = useState(7);
  const [pain, setPain] = useState(false);
  const [painParts, setPainParts] = useState<string[]>([]);
  const [painSeverity, setPainSeverity] = useState<"mild" | "severe">("mild");
  const [saving, setSaving] = useState(false);

  // 운동 중 스톱워치
  useEffect(() => {
    let interval: ReturnType<typeof setInterval> | undefined;
    if (phase === "WORK" && !loading) {
      interval = setInterval(() => setElapsedSeconds((prev) => prev + 1), 1000);
    }
    return () => {
      if (interval) clearInterval(interval);
    };
  }, [phase, loading]);

  // 휴식 카운트다운
  useEffect(() => {
    let interval: ReturnType<typeof setInterval> | undefined;
    if (phase === "REST" && restTimeLeft > 0) {
      interval = setInterval(() => {
        setRestTimeLeft((prev) => {
          const next = prev > 0 ? prev - 1 : 0;
          if (next === 0) startNextSet();
          return next;
        });
      }, 1000);
    }
    return () => {
      if (interval) clearInterval(interval);
    };
  }, [phase, restTimeLeft]);

  useEffect(() => {
    const fetchDetails = async () => {
      try {
        const response = await client.get(`/api/recommend/${recommendation_id}`);
        setRec(response.data);
      } catch (error) {
        console.error(error);
        notify("운동 정보를 불러오지 못했어요");
      } finally {
        setLoading(false);
      }
    };
    fetchDetails();
  }, [recommendation_id]);

  const startNextSet = () => {
    if (currentSet < rec.selected_plan.sets) {
      setCurrentSet(currentSet + 1);
      setElapsedSeconds(0);
      setPhase("WORK");
    } else {
      setPhase("FEEDBACK");
    }
  };

  const handleSetComplete = () => {
    setTotalElapsedSeconds((prev) => prev + elapsedSeconds);
    if (currentSet < rec.selected_plan.sets) {
      setRestTimeLeft(rec.selected_plan.rest_seconds || 60);
      setPhase("REST");
    } else {
      setPhase("FEEDBACK");
    }
  };

  const handleFinishWorkout = async () => {
    setSaving(true);
    try {
      await client.post("/api/log/", {
        recommendation_id,
        user_id: userId,
        plan_id: id,
        completed,
        actual_minutes: Math.max(1, Math.round(totalElapsedSeconds / 60)),
        actual_sets: currentSet,
        rpe,
        pain_occurred: pain,
        pain_parts: pain ? painParts : [],
        pain_severity: pain ? painSeverity : null,
      });
      await client.post("/api/reward/", {
        recommendation_id,
        user_id: userId,
        completed,
        rpe,
        pain_occurred: pain,
        streak: null,
      });
      notify("기록했어요", `운동 시간 ${formatTime(totalElapsedSeconds)}. 다음 추천에 반영됩니다.`);
      router.replace("/");
    } catch (error) {
      console.error(error);
      notify("기록을 저장하지 못했어요", "잠시 뒤에 다시 시도해 주세요.");
    } finally {
      setSaving(false);
    }
  };

  if (loading || !rec) return <Loading />;
  const plan = rec.selected_plan;
  const target = plan.type === "rep-based" ? `${plan.reps}회` : `총 ${plan.minutes}분`;

  if (phase === "FEEDBACK") {
    return (
      <Screen footer={<Button label="기록 저장" onPress={handleFinishWorkout} loading={saving} />}>
        <Stack.Screen options={{ title: "운동 기록" }} />
        <Text className="text-[24px] leading-8 font-bold text-ink">{plan.name}</Text>
        <Text className="text-[14px] text-zinc-500 mt-1 mb-8">
          {currentSet}세트 · {formatTime(totalElapsedSeconds)}
        </Text>

        <Section label="끝까지 했나요?">
          <Segmented
            options={[{ label: "끝까지 했어요", value: "yes" }, { label: "중간에 멈췄어요", value: "no" }]}
            value={completed ? "yes" : "no"}
            onChange={(v) => setCompleted(v === "yes")}
          />
        </Section>

        <Section label="얼마나 힘들었나요?" right={<Text className="text-[13px] font-semibold text-ink">{RPE_HINT[rpe]}</Text>}>
          <View className="flex-row flex-wrap -m-1">
            {[1, 2, 3, 4, 5, 6, 7, 8, 9, 10].map((n) => (
              <TouchableOpacity
                key={n}
                onPress={() => setRpe(n)}
                className={`m-1 w-[17%] h-10 rounded-lg border items-center justify-center ${rpe === n ? "bg-ink border-ink" : "bg-white border-line"}`}
              >
                <Text className={`text-[15px] ${rpe === n ? "text-white font-semibold" : "text-ink"}`}>{n}</Text>
              </TouchableOpacity>
            ))}
          </View>
          <Text className="text-[13px] text-zinc-500 mt-2">1은 아주 쉬움, 10은 한계. 6에서 8이 알맞은 강도예요.</Text>
        </Section>

        <Section label="아픈 곳이 있었나요?">
          <Segmented
            options={[{ label: "없었어요", value: "no" }, { label: "있었어요", value: "yes" }]}
            value={pain ? "yes" : "no"}
            onChange={(v) => setPain(v === "yes")}
          />
        </Section>

        {pain ? (
          <>
            <Section label="어디가 아팠나요? (여러 개 선택)">
              <View className="flex-row flex-wrap -m-1">
                {PAIN_PARTS.map((p) => (
                  <Chip
                    key={p.id}
                    label={p.label}
                    tone="danger"
                    selected={painParts.includes(p.id)}
                    onPress={() =>
                      setPainParts((prev) => (prev.includes(p.id) ? prev.filter((x) => x !== p.id) : [...prev, p.id]))
                    }
                  />
                ))}
              </View>
            </Section>
            <Section label="정도">
              <Segmented
                options={[{ label: "조금 뻐근해요", value: "mild" }, { label: "심하게 아파요", value: "severe" }]}
                value={painSeverity}
                onChange={(v) => setPainSeverity(v as "mild" | "severe")}
              />
              <Text className="text-[13px] text-zinc-500 mt-2">
                {painSeverity === "mild"
                  ? "7일 동안 그 부위에 무리가 가는 운동을 빼고 추천해요."
                  : "그 부위를 주의 부위로 등록해 앞으로 계속 빼고 추천해요."}
              </Text>
            </Section>
          </>
        ) : null}
      </Screen>
    );
  }

  const resting = phase === "REST";
  return (
    <Screen
      footer={
        <View>
          {resting ? (
            <Button label="바로 다음 세트" onPress={startNextSet} />
          ) : (
            <Button label={currentSet === plan.sets ? "마지막 세트 완료" : "세트 완료"} onPress={handleSetComplete} />
          )}
          <View className="h-1" />
          <Button
            label="오늘은 여기까지"
            variant="ghost"
            onPress={() => confirmAction("운동 그만하기", "기록하지 않고 나갈까요?", "나가기", () => router.replace("/"), "계속하기")}
          />
        </View>
      }
    >
      <Stack.Screen options={{ title: plan.name }} />
      <View className="flex-row justify-between items-baseline">
        <Text className="text-[15px] font-semibold text-ink">
          세트 {currentSet} <Text className="text-zinc-400">/ {plan.sets}</Text>
        </Text>
        <Text className="text-[14px] text-zinc-500">목표 {target}</Text>
      </View>
      <View className="flex-row mt-3">
        {Array.from({ length: plan.sets }, (_, i) => (
          <View
            key={i}
            className="flex-1 h-1.5 rounded-full mr-1"
            style={{ backgroundColor: i < currentSet - (resting ? 0 : 1) ? colors.brand : i === currentSet - 1 ? "#A7C8B9" : colors.canvas }}
          />
        ))}
      </View>

      <View className="items-center py-16">
        <Text className="text-[14px] text-zinc-500 mb-2">{resting ? "휴식" : "운동 시간"}</Text>
        <Text className="text-[64px] leading-[72px] font-semibold text-ink" style={{ fontVariant: ["tabular-nums"] }}>
          {formatTime(resting ? restTimeLeft : elapsedSeconds)}
        </Text>
        {resting ? <Text className="text-[14px] text-zinc-500 mt-2">끝나면 다음 세트가 자동으로 시작돼요</Text> : null}
      </View>

      {plan.tip || plan.description ? (
        <Card tone="muted">
          {plan.description ? <Text className="text-[14px] leading-[22px] text-zinc-700">{plan.description}</Text> : null}
          {plan.tip ? <Text className="text-[14px] leading-[22px] text-ink font-semibold mt-1">{plan.tip}</Text> : null}
        </Card>
      ) : null}
    </Screen>
  );
}
