import React, { useEffect, useState } from "react";
import { ActivityIndicator, Linking, Modal, ScrollView, Text, TouchableOpacity, View } from "react-native";
import { Stack, useRouter } from "expo-router";
import { useUserStore } from "../src/store/userStore";
import client from "../src/api/client";
import { errorMessage, notify } from "../src/utils/dialog";
import { Button, Card, colors, PlainText, Screen, Section, Segmented } from "../src/ui";

// 추천 엔진은 피로도와 가용 시간을 보고 고른다(docs/simulation_eval.md).
const FATIGUE = [
  { value: 0, hint: "아주 가뿐해요" },
  { value: 1, hint: "가뿐해요" },
  { value: 2, hint: "보통이에요" },
  { value: 3, hint: "조금 지쳤어요" },
  { value: 4, hint: "많이 지쳤어요" },
  { value: 5, hint: "쉬어야 할 것 같아요" },
];
const MINUTES = [10, 15, 20, 30, 45, 60];
const INTENSITY: Record<string, string> = { low: "저강도", medium: "중강도", high: "고강도" };

type Conditions = { location: "gym" | "home"; stretching: boolean; fatigue: number; minutes: number };

export default function Recommend() {
  const router = useRouter();
  const { userId } = useUserStore();
  const [loading, setLoading] = useState(true);
  const [rec, setRec] = useState<any>(null);
  const [location, setLocation] = useState<"gym" | "home">("gym");
  const [stretching, setStretching] = useState(false);
  const [fatigue, setFatigue] = useState(2);
  const [minutes, setMinutes] = useState(30);
  const [guide, setGuide] = useState<any>(null);
  const [guideLoading, setGuideLoading] = useState(false);

  // 바뀐 값만 넘기면 나머지는 지금 화면 값을 쓴다(상태 갱신 전에 불러도 새 값이 들어가도록).
  const fetchRecommendation = async (changes: Partial<Conditions> = {}) => {
    const c: Conditions = { location, stretching, fatigue, minutes, ...changes };
    setLoading(true);
    try {
      // 최근 순응도·평균 RPE·스트릭은 서버가 기록으로 계산한다.
      const response = await client.post("/api/recommend/", {
        user_id: userId,
        location: c.location,
        available_minutes: c.minutes,
        fatigue: c.fatigue,
        want_stretching: c.stretching,
      });
      setRec(response.data);
    } catch (error) {
      console.error(error);
      notify("추천을 불러오지 못했어요", errorMessage(error, "잠시 뒤에 다시 시도해 주세요."));
    } finally {
      setLoading(false);
    }
  };

  const openGuide = async () => {
    if (!rec) return;
    setGuideLoading(true);
    try {
      const response = await client.post("/api/chatbot/exercise-guide", {
        exercise_name: rec.selected_plan.name,
        target_parts: rec.selected_plan.target_parts,
      });
      setGuide(response.data);
    } catch (error) {
      console.error(error);
      notify("가이드를 불러오지 못했어요", errorMessage(error, "잠시 뒤에 다시 시도해 주세요."));
    } finally {
      setGuideLoading(false);
    }
  };

  useEffect(() => {
    if (userId) {
      fetchRecommendation();
    } else {
      router.replace("/onboarding");
    }
  }, [userId]);

  const plan = rec?.selected_plan;
  const amount = plan ? (plan.type === "time-based" ? `${plan.sets}세트` : `${plan.sets}세트 × ${plan.reps}회`) : "";

  return (
    <Screen
      footer={
        plan ? (
          <Button
            label="운동 시작"
            disabled={loading}
            onPress={() =>
              router.push({ pathname: `/workout/[id]`, params: { id: plan.plan_id, recommendation_id: rec.recommendation_id } })
            }
          />
        ) : null
      }
    >
      <Stack.Screen options={{ title: "오늘의 추천" }} />

      <Section label="장소">
        <Segmented
          options={[{ label: "헬스장", value: "gym" }, { label: "집", value: "home" }]}
          value={location}
          onChange={(v) => {
            setLocation(v as "gym" | "home");
            fetchRecommendation({ location: v as "gym" | "home" });
          }}
        />
      </Section>

      <Section label="지금 피로도" right={<Text className="text-[13px] text-ink font-semibold">{FATIGUE[fatigue].hint}</Text>}>
        <Segmented
          options={FATIGUE.map((f) => ({ label: String(f.value), value: f.value }))}
          value={fatigue}
          onChange={(v) => {
            setFatigue(v);
            fetchRecommendation({ fatigue: v });
          }}
        />
      </Section>

      <Section label="운동할 수 있는 시간" right={<Text className="text-[13px] text-ink font-semibold">{minutes}분</Text>}>
        <Segmented
          options={MINUTES.map((m) => ({ label: String(m), value: m }))}
          value={minutes}
          onChange={(v) => {
            setMinutes(v);
            fetchRecommendation({ minutes: v });
          }}
        />
      </Section>

      <Section label={stretching ? "회복용 스트레칭" : "추천 운동"} style={{ marginTop: 8 }}>
        <Card>
          {loading || !plan ? (
            <View className="h-36 items-center justify-center">
              {loading ? <ActivityIndicator color={colors.ink} /> : <Text className="text-zinc-500">추천 결과가 없어요.</Text>}
            </View>
          ) : (
            <View>
              <Text className="text-[22px] leading-8 font-bold text-ink">{plan.name}</Text>
              <Text className="text-[14px] text-zinc-500 mt-1">
                {INTENSITY[plan.intensity] || plan.intensity} · {plan.minutes}분 · {amount}
              </Text>
              {rec.reason ? (
                <View className="mt-4 pt-4 border-t border-line">
                  <Text className="text-[13px] font-semibold text-zinc-500 mb-1">고른 이유</Text>
                  <Text className="text-[14px] leading-[22px] text-zinc-700">{rec.reason}</Text>
                </View>
              ) : null}
              <View className="flex-row mt-4 -mx-1">
                <View className="flex-1 mx-1">
                  <Button label="운동 방법 보기" variant="secondary" onPress={openGuide} loading={guideLoading} />
                </View>
                {plan.video_url ? (
                  <View className="flex-1 mx-1">
                    <Button label="영상" variant="secondary" onPress={() => Linking.openURL(plan.video_url)} />
                  </View>
                ) : null}
              </View>
            </View>
          )}
        </Card>
      </Section>

      <View className="flex-row justify-between">
        <TouchableOpacity onPress={() => fetchRecommendation()} disabled={loading} className="py-2">
          <Text className="text-[14px] text-zinc-500">다른 운동 보기</Text>
        </TouchableOpacity>
        <TouchableOpacity
          onPress={() => {
            setStretching(!stretching);
            fetchRecommendation({ stretching: !stretching });
          }}
          disabled={loading}
          className="py-2"
        >
          <Text className="text-[14px] text-zinc-500">{stretching ? "일반 운동으로 돌아가기" : "가볍게 스트레칭만 할래요"}</Text>
        </TouchableOpacity>
      </View>
      {stretching ? (
        <Text className="text-[13px] text-zinc-500 mt-2">스트레칭은 회복 세션이라 주간 목표 횟수에는 넣지 않아요.</Text>
      ) : null}

      <Modal visible={!!guide} animationType="slide" transparent onRequestClose={() => setGuide(null)}>
        <View className="flex-1 justify-end bg-black/40">
          <View className="bg-white rounded-t-2xl h-[75%] w-full self-center" style={{ maxWidth: 480 }}>
            <View className="flex-row justify-between items-center px-5 h-14 border-b border-line">
              <Text className="text-[16px] font-semibold text-ink">{plan?.name}</Text>
              <TouchableOpacity onPress={() => setGuide(null)}>
                <Text className="text-[15px] text-zinc-500">닫기</Text>
              </TouchableOpacity>
            </View>
            <ScrollView contentContainerStyle={{ padding: 20, paddingBottom: 32 }}>
              <PlainText text={guide?.guide_text || ""} />
              <View className="mt-6">
                <Button label="유튜브에서 자세 영상 찾기" variant="secondary" onPress={() => Linking.openURL(guide?.youtube_url)} />
              </View>
              <Text className="text-[12px] text-zinc-400 mt-4">AI 가 쓴 설명이에요. 운동 중 통증이 있으면 바로 멈추세요.</Text>
            </ScrollView>
          </View>
        </View>
      </Modal>
    </Screen>
  );
}
