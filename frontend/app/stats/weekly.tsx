import React, { useEffect, useState } from "react";
import { Text, View } from "react-native";
import { Stack } from "expo-router";
import { useUserStore } from "../../src/store/userStore";
import client from "../../src/api/client";
import { Loading, Screen, Title } from "../../src/ui";

export default function WeeklyDetails() {
  const { userId } = useUserStore();
  const [logs, setLogs] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchLogs = async () => {
      try {
        const response = await client.get(`/api/stats/${userId}/weekly-details`);
        setLogs(response.data);
      } catch (error) {
        console.error("Failed to fetch weekly details:", error);
      } finally {
        setLoading(false);
      }
    };
    if (userId) fetchLogs();
  }, [userId]);

  if (loading) return <Loading />;

  const totalMin = logs.reduce((s, l) => s + (l.minutes || 0), 0);
  return (
    <Screen>
      <Stack.Screen options={{ title: "운동 기록" }} />
      <Title sub={logs.length ? `${logs.length}번, 모두 ${totalMin}분` : undefined}>최근 7일</Title>

      {logs.length === 0 ? (
        <Text className="text-[14px] text-zinc-500">최근 7일 동안 기록이 없어요.</Text>
      ) : (
        <View className="border-t border-line">
          {logs.map((log, i) => (
            <View key={log.log_id} className={`flex-row items-center py-4 ${i === logs.length - 1 ? "" : "border-b border-line"}`}>
              <View className="flex-1">
                <Text className="text-[15px] font-semibold text-ink">{log.plan_name}</Text>
                <Text className="text-[13px] text-zinc-500 mt-0.5">
                  {log.date} {log.time} · {log.is_stretching ? "스트레칭" : log.location === "gym" ? "헬스장" : "집"} · {log.sets}세트
                </Text>
              </View>
              <View className="items-end">
                <Text className="text-[15px] font-semibold text-ink">{log.minutes}분</Text>
                <Text className="text-[12px] text-zinc-500">{Math.round(log.calories)}kcal</Text>
              </View>
            </View>
          ))}
        </View>
      )}
    </Screen>
  );
}
