import React, { useEffect, useState } from "react";
import { View, Text, TouchableOpacity, ScrollView, ActivityIndicator } from "react-native";
import { useRouter, Stack } from "expo-router";
import { useUserStore } from "../src/store/userStore";
import client from "../src/api/client";
import { SafeAreaView } from "react-native-safe-area-context";

import { Ionicons } from "@expo/vector-icons";

export default function Home() {
  const { userId, isOnboarded } = useUserStore();
  const router = useRouter();
  const [userStatus, setUserStatus] = useState<any>(null);
  const [loading, setLoading] = useState(false);

  const fetchStatus = async () => {
    if (userId && isOnboarded) {
      setLoading(true);
      try {
        const response = await client.get(`/api/stats/${userId}/summary`);
        setUserStatus(response.data);
      } catch (error) {
        console.error("Failed to fetch user status:", error);
      } finally {
        setLoading(false);
      }
    }
  };

  useEffect(() => {
    fetchStatus();
  }, [userId, isOnboarded]);

  const mockYesterday = async () => {
    if (!userId) return;
    try {
      await client.post(`/api/debug/mock-yesterday/${userId}`);
      alert("가짜 운동 기록이 생성되었습니다!");
      fetchStatus(); 
    } catch (error) {
      console.error(error);
    }
  };

  return (
    <SafeAreaView className="flex-1 bg-white" edges={['top']}>
      <Stack.Screen options={{ 
        title: "Fitness AI", 
        headerShown: true,
        headerStyle: { backgroundColor: '#2563eb' },
        headerTintColor: '#fff',
        headerTitleStyle: { fontWeight: "900", fontSize: 20 },
        headerShadowVisible: false,
        headerRight: () => (
          <TouchableOpacity 
            onPress={() => router.push("/profile")}
            className="mr-5"
            activeOpacity={0.7}
          >
            <Ionicons name="person-circle-outline" size={32} color="#fff" />
          </TouchableOpacity>
        )
      }} />
      <ScrollView className="flex-1" showsVerticalScrollIndicator={false}>
        <View className="p-6 pt-2">
          {isOnboarded && (
            <View className="mb-6 bg-blue-600 p-8 rounded-[40px] shadow-xl relative overflow-hidden">
              {/* Background Decorative Circles */}
              <View className="absolute -top-10 -right-10 w-40 h-40 bg-white/10 rounded-full" />
              <View className="absolute -bottom-20 -left-10 w-32 h-32 bg-white/5 rounded-full" />

              <View className="flex-row justify-between items-center relative z-10">
                <View className="flex-1 mr-4">
                  <Text className="text-white text-xl font-black mb-1">안녕하세요! 👋</Text>
                  <Text className="text-blue-100 text-xs font-bold leading-tight">오늘도 건강한 하루를 만들어볼까요?</Text>
                </View>

                <View className="bg-white/20 px-4 py-3 rounded-[24px] border border-white/30 items-center justify-center min-w-[80px]">
                  <Text className="text-2xl mb-0.5">🔥</Text>
                  <Text className="text-white font-black text-base leading-tight">
                    {userStatus?.current_streak || 0}일째
                  </Text>
                  <Text className="text-blue-100 text-[8px] font-bold uppercase tracking-widest">
                    STREAK
                  </Text>
                </View>
              </View>
            </View>
          )}

          {!isOnboarded ? (
            <View className="flex-1 justify-center py-20">
              <Text className="text-4xl font-black text-gray-900 mb-2 text-center">반가워요! ✨</Text>
              <Text className="text-gray-400 mb-10 text-center">당신만을 위한 맞춤 운동 파트너,{"\n"}코치와 함께 시작해볼까요?</Text>
              <TouchableOpacity
                className="bg-blue-600 p-6 rounded-[32px] items-center shadow-lg active:opacity-90"
                onPress={() => router.push("/onboarding")}
              >
                <Text className="text-white font-extrabold text-xl">코치 시작하기 🚀</Text>
              </TouchableOpacity>
            </View>
          ) : (
            <View className="space-y-4">
              <TouchableOpacity
                className="bg-gray-900 p-5 rounded-3xl items-center shadow-lg mb-2 active:opacity-90"
                onPress={() => router.push("/recommend")}
              >
                <View className="flex-row items-center">
                  <Text className="text-white font-extrabold text-lg mr-2">오늘의 운동 추천받기</Text>
                  <Text className="text-white text-xl">✨</Text>
                </View>
              </TouchableOpacity>

              <TouchableOpacity
                className="bg-white p-5 rounded-3xl items-center shadow-sm mb-4 border border-blue-100 active:opacity-90"
                onPress={() => router.push("/chat")}
              >
                <View className="flex-row items-center">
                  <Text className="text-blue-600 font-extrabold text-lg mr-2">AI 코치에게 질문하기</Text>
                  <Text className="text-blue-600 text-xl">💬</Text>
                </View>
              </TouchableOpacity>
              
              {userStatus && (
                <View className="space-y-4">
                  {/* Weekly Goal Progress */}
                  <View className="bg-blue-50 p-6 rounded-[32px] border border-blue-100 shadow-sm mb-2">
                    <View className="flex-row justify-between items-end mb-4">
                      <View>
                        <Text className="font-black text-blue-900 text-lg">주간 목표 달성도</Text>
                        <Text className="text-blue-600 font-bold text-xs uppercase mt-0.5">
                          {userStatus.completed_days_this_week >= userStatus.weekly_goal 
                            ? "🎉 목표 달성! 대단해요!" 
                            : `이번 주 ${userStatus.weekly_goal}회 중 ${userStatus.completed_days_this_week}회 완료`}
                        </Text>
                      </View>
                      <Text className="text-blue-900 font-black text-2xl">
                        {Math.min(100, Math.round((userStatus.completed_days_this_week / userStatus.weekly_goal) * 100))}%
                      </Text>
                    </View>
                    <View className="h-4 bg-white rounded-full overflow-hidden border border-blue-100">
                      <View 
                        style={{ width: `${Math.min(100, (userStatus.completed_days_this_week / userStatus.weekly_goal) * 100)}%` }}
                        className="h-full bg-blue-600 rounded-full"
                      />
                    </View>
                    {userStatus.completed_days_this_week >= userStatus.weekly_goal && (
                      <View className="mt-4 bg-white/60 p-3 rounded-2xl items-center">
                        <Text className="text-blue-800 font-black text-xs">이번 주 목표를 모두 달성했습니다! 🏆</Text>
                      </View>
                    )}
                  </View>

                  {/* Weekly Activity Chart */}
                  <TouchableOpacity
                    activeOpacity={0.8}
                    onPress={() => router.push("/stats/weekly")}
                    className="bg-white p-6 rounded-[32px] border border-gray-100 shadow-sm"
                  >
                    <View className="flex-row justify-between items-center mb-5">
                      <Text className="font-black text-gray-800 text-lg">주간 활동</Text>
                      <View className="bg-gray-50 px-3 py-1.5 rounded-full border border-gray-100">
                        <Text className="text-gray-400 text-[10px] font-black uppercase">자세히 보기 ❯</Text>
                      </View>
                    </View>
                    <View className="flex-row justify-between items-center px-1">
                      {userStatus.activity_chart.map((day: any) => (
                        <View key={day.date} className="items-center">
                          <View 
                            style={{ 
                              backgroundColor: 
                                day.type === 'gym' ? '#2563eb' : // blue-600
                                day.type === 'home' ? '#8b5cf6' : // purple-500
                                day.type === 'stretch' ? '#10b981' : // emerald-500
                                '#f9fafb' // gray-50
                            }}
                            className={`w-10 h-10 rounded-2xl items-center justify-center mb-2 shadow-sm ${
                              day.completed ? "" : "border border-gray-100"
                            }`}
                          >
                            <Text className="text-[14px]">
                              {day.type === 'gym' ? '🏋️' : 
                               day.type === 'home' ? '🏠' : 
                               day.type === 'stretch' ? '🧘' : ''}
                            </Text>
                          </View>
                          <Text className={`text-[10px] font-bold ${day.completed ? "text-gray-800" : "text-gray-400"}`}>
                            {day.day_name}
                          </Text>
                        </View>
                      ))}
                    </View>
                    <View className="flex-row justify-center mt-6 space-x-6">
                      <View className="flex-row items-center"><View className="w-3 h-3 rounded-full bg-blue-600 mr-2"/><Text className="text-[10px] font-bold text-gray-500">헬스</Text></View>
                      <View className="flex-row items-center ml-4"><View className="w-3 h-3 rounded-full bg-purple-500 mr-2"/><Text className="text-[10px] font-bold text-gray-500">홈트</Text></View>
                      <View className="flex-row items-center ml-4"><View className="w-3 h-3 rounded-full bg-emerald-500 mr-2"/><Text className="text-[10px] font-bold text-gray-500">회복</Text></View>
                    </View>
                  </TouchableOpacity>
                </View>
              )}

              {/* DEBUG BUTTON - REMOVE IN PRODUCTION */}
              <TouchableOpacity 
                onPress={mockYesterday}
                className="mt-6 p-4 border border-red-100 rounded-2xl border-dashed items-center"
              >
                <Text className="text-red-300 text-[10px] font-bold">🛠️ [테스트용] 스트릭 1일 늘리기</Text>
                <Text className="text-red-200 text-[8px] mt-1">누를 때마다 연속 운동일수가 1일씩 증가합니다.</Text>
              </TouchableOpacity>
            </View>
          )}
        </View>
      </ScrollView>
    </SafeAreaView>
  );
}
