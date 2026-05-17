import React, { useEffect, useState } from "react";
import { View, Text, ScrollView, ActivityIndicator, TouchableOpacity } from "react-native";
import { Stack, useRouter } from "expo-router";
import { useUserStore } from "../../src/store/userStore";
import client from "../../src/api/client";
import { SafeAreaView } from "react-native-safe-area-context";
import { Ionicons } from "@expo/vector-icons";

export default function WeeklyDetails() {
  const { userId } = useUserStore();
  const router = useRouter();
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

  return (
    <SafeAreaView className="flex-1 bg-white">
      <Stack.Screen options={{ 
        title: "이번 주 운동 기록", 
        headerShown: true,
        headerTitleStyle: { fontWeight: "900", fontSize: 18 },
        headerShadowVisible: false,
        headerLeft: () => (
          <TouchableOpacity onPress={() => router.back()} className="ml-2">
            <Ionicons name="chevron-back" size={28} color="#111827" />
          </TouchableOpacity>
        )
      }} />
      
      {loading ? (
        <View className="flex-1 justify-center items-center">
          <ActivityIndicator size="large" color="#2563eb" />
        </View>
      ) : (
        <ScrollView className="flex-1" showsVerticalScrollIndicator={false}>
          <View className="p-6">
            <View className="mb-8">
              <Text className="text-2xl font-black text-gray-900">활동 리스트 📊</Text>
              <Text className="text-gray-400 font-bold text-xs uppercase mt-1">최근 7일간의 기록입니다</Text>
            </View>

            {logs.length === 0 ? (
              <View className="py-20 items-center">
                <Text className="text-4xl mb-4">💨</Text>
                <Text className="text-gray-400 font-bold">아직 이번 주 운동 기록이 없어요.</Text>
              </View>
            ) : (
              <View className="space-y-4">
                {logs.map((log) => (
                  <View key={log.log_id} className="bg-gray-50 p-5 rounded-[32px] border border-gray-100 flex-row items-center mb-4">
                    <View className={`w-12 h-12 rounded-2xl items-center justify-center mr-4 ${
                      log.is_stretching ? "bg-emerald-100" : log.location === "gym" ? "bg-blue-100" : "bg-purple-100"
                    }`}>
                      <Text className="text-xl">
                        {log.is_stretching ? "🧘" : log.location === "gym" ? "🏋️" : "🏠"}
                      </Text>
                    </View>
                    
                    <View className="flex-1">
                      <Text className="font-black text-gray-900 text-base mb-0.5">{log.plan_name}</Text>
                      <View className="flex-row items-center">
                        <Text className="text-gray-400 text-xs font-bold">{log.date} · {log.time}</Text>
                      </View>
                    </View>

                    <View className="items-end">
                      <Text className="text-blue-600 font-black text-lg">{log.minutes}분</Text>
                      <Text className="text-gray-400 text-[10px] font-bold uppercase">{log.sets} 세트</Text>
                    </View>
                  </View>
                ))}
              </View>
            )}
          </View>
        </ScrollView>
      )}
    </SafeAreaView>
  );
}
