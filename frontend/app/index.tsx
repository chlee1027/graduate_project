import React, { useCallback, useState } from "react";
import { Text, TouchableOpacity, View } from "react-native";
import { Stack, useFocusEffect, useRouter } from "expo-router";
import { Ionicons } from "@expo/vector-icons";
import { useUserStore } from "../src/store/userStore";
import client from "../src/api/client";
import { Button, Card, colors, Screen, Section, Stat } from "../src/ui";

const DAY_TONE: Record<string, string> = {
  gym: colors.brand,
  home: colors.brand,
  stretch: "#A7C8B9",
};

export default function Home() {
  const { userId, isOnboarded } = useUserStore();
  const router = useRouter();
  const [status, setStatus] = useState<any>(null);

  const fetchStatus = useCallback(async () => {
    if (!userId || !isOnboarded) return;
    try {
      const response = await client.get(`/api/stats/${userId}/summary`);
      setStatus(response.data);
    } catch (error) {
      console.error("Failed to fetch user status:", error);
    }
  }, [userId, isOnboarded]);

  // 운동을 마치고 돌아오면 숫자를 다시 읽는다
  useFocusEffect(
    useCallback(() => {
      fetchStatus();
    }, [fetchStatus])
  );

  if (!isOnboarded) {
    return (
      <Screen edges={["top", "bottom"]} footer={<Button label="시작하기" onPress={() => router.push("/onboarding")} />}>
        <Stack.Screen options={{ headerShown: false }} />
        <View className="pt-16">
          <Text className="text-[13px] font-semibold text-brand mb-3">Fitness AI</Text>
          <Text className="text-[30px] leading-10 font-bold text-ink">오늘 컨디션에 맞는{"\n"}운동 하나</Text>
          <Text className="text-[15px] leading-6 text-zinc-500 mt-4">
            몸 상태와 남은 시간을 알려 주면 운동을 하나 골라 드려요. 끝나고 남긴 기록으로 다음 추천이 달라집니다.
          </Text>
        </View>
        <View className="mt-12">
          {[
            ["기본 정보 입력", "숙련도, 장소, 주의할 부위"],
            ["오늘 컨디션 선택", "피로도와 운동할 수 있는 시간"],
            ["운동하고 기록", "완료 여부, 힘든 정도, 통증"],
          ].map(([t, d], i) => (
            <View key={t} className="flex-row py-3.5 border-b border-line">
              <Text className="w-7 text-[15px] font-semibold text-zinc-400">{i + 1}</Text>
              <View className="flex-1">
                <Text className="text-[15px] font-semibold text-ink">{t}</Text>
                <Text className="text-[13px] text-zinc-500 mt-0.5">{d}</Text>
              </View>
            </View>
          ))}
        </View>
      </Screen>
    );
  }

  const done = status?.completed_days_this_week ?? 0;
  const goal = status?.weekly_goal ?? 0;
  const pct = goal ? Math.min(100, Math.round((done / goal) * 100)) : 0;

  return (
    <Screen>
      <Stack.Screen
        options={{
          title: "",
          headerShown: true,
          // 온보딩에서 넘어오면 앞 화면이 스택에 남으므로, 홈에서는 뒤로 가기를 감춘다
          headerBackVisible: false,
          headerLeft: () => null,
          gestureEnabled: false,
          headerRight: () => (
            <TouchableOpacity onPress={() => router.push("/profile")} className="mr-4" accessibilityLabel="내 정보">
              <Ionicons name="person-circle-outline" size={26} color={colors.ink} />
            </TouchableOpacity>
          ),
        }}
      />
      <Text className="text-[24px] leading-8 font-bold text-ink mb-6">오늘의 운동</Text>

      <Card>
        <View className="flex-row">
          <Stat label="연속 운동" value={status?.current_streak ?? 0} unit="일" />
          <Stat label="이번 주" value={`${done}/${goal}`} unit="회" />
          <Stat label="달성" value={pct} unit="%" />
        </View>
        <View className="h-1.5 bg-canvas rounded-full mt-4 overflow-hidden">
          <View style={{ width: `${pct}%`, backgroundColor: colors.brand }} className="h-full rounded-full" />
        </View>
      </Card>

      <View className="mt-4">
        <Button label="오늘 운동 추천받기" onPress={() => router.push("/recommend")} />
        <View className="h-2" />
        <Button label="코치에게 질문하기" variant="secondary" onPress={() => router.push("/chat")} />
      </View>

      {status?.activity_chart ? (
        <Section
          label="최근 7일"
          right={
            <TouchableOpacity onPress={() => router.push("/stats/weekly")}>
              <Text className="text-[13px] text-zinc-500">기록 보기</Text>
            </TouchableOpacity>
          }
          style={{ marginTop: 32 }}
        >
          <View className="flex-row justify-between">
            {status.activity_chart.map((day: any) => (
              <View key={day.date} className="items-center">
                <View
                  style={{ backgroundColor: day.completed ? DAY_TONE[day.type] || colors.brand : colors.canvas }}
                  className="w-9 h-9 rounded-lg"
                />
                <Text className={`text-[12px] mt-1.5 ${day.completed ? "text-ink font-semibold" : "text-zinc-400"}`}>{day.day_name}</Text>
              </View>
            ))}
          </View>
          <View className="flex-row mt-4">
            <View className="flex-row items-center mr-4">
              <View style={{ backgroundColor: colors.brand }} className="w-2.5 h-2.5 rounded-sm mr-1.5" />
              <Text className="text-[12px] text-zinc-500">운동</Text>
            </View>
            <View className="flex-row items-center">
              <View style={{ backgroundColor: DAY_TONE.stretch }} className="w-2.5 h-2.5 rounded-sm mr-1.5" />
              <Text className="text-[12px] text-zinc-500">스트레칭</Text>
            </View>
          </View>
        </Section>
      ) : null}
    </Screen>
  );
}
