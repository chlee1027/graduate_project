import React, { useEffect, useState } from "react";
import { View, Text, TouchableOpacity, ScrollView, ActivityIndicator } from "react-native";
import { useRouter, Stack } from "expo-router";
import { useUserStore } from "../src/store/userStore";
import client from "../src/api/client";
import { SafeAreaView } from "react-native-safe-area-context";

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
    <SafeAreaView className="flex-1 bg-white">
      <Stack.Screen options={{ title: "Fitness AI", headerShown: false }} />
      <ScrollView className="flex-1" showsVerticalScrollIndicator={false}>
        <View className="p-6 pt-10">
          <View className="mb-8">
            <Text className="text-3xl font-black text-gray-900">홈</Text>
          </View>

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
              
              {userStatus && (
                <View className="space-y-4">
                  {/* Weekly Activity Chart */}
                  <View className="bg-white p-6 rounded-[32px] border border-gray-100 shadow-sm">
                    <Text className="font-black text-gray-800 text-lg mb-5">주간 활동</Text>
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
                  </View>

                  {/* Overall Stats Cards */}
                  <View className="flex-row justify-between">
                    <View className="bg-gray-50 w-[48%] p-6 rounded-[32px] border border-gray-100">
                      <View className="w-10 h-10 bg-white rounded-2xl items-center justify-center mb-4 shadow-sm">
                        <Text className="text-lg">⏲️</Text>
                      </View>
                      <Text className="text-gray-400 text-[10px] font-bold uppercase mb-1">누적 시간</Text>
                      <View className="flex-row items-baseline">
                        <Text className="text-2xl font-black text-gray-900">{userStatus.total_workout_minutes}</Text>
                        <Text className="text-gray-400 font-bold text-xs ml-1">분</Text>
                      </View>
                    </View>

                    <View className="bg-gray-50 w-[48%] p-6 rounded-[32px] border border-gray-100">
                      <View className="w-10 h-10 bg-white rounded-2xl items-center justify-center mb-4 shadow-sm">
                        <Text className="text-lg">🏆</Text>
                      </View>
                      <Text className="text-gray-400 text-[10px] font-bold uppercase mb-1">완료 세션</Text>
                      <View className="flex-row items-baseline">
                        <Text className="text-2xl font-black text-gray-900">{userStatus.total_completed_workouts}</Text>
                        <Text className="text-gray-400 font-bold text-xs ml-1">회</Text>
                      </View>
                    </View>
                  </View>
                  
                  {/* User Level Card - Dynamic Styling */}
                  <View 
                    style={{ 
                      backgroundColor: 
                        userStatus.experience_level === 'beginner' ? '#ecfdf5' : // emerald-50
                        userStatus.experience_level === 'intermediate' ? '#eff6ff' : // blue-50
                        '#fffbeb' // amber-50
                    }}
                    className={`p-6 rounded-[32px] border flex-row items-center justify-between ${
                      userStatus.experience_level === 'beginner' ? 'border-emerald-100' : 
                      userStatus.experience_level === 'intermediate' ? 'border-blue-100' : 
                      'border-amber-100'
                    }`}
                  >
                    <View>
                      <Text className={`text-[10px] font-bold uppercase tracking-widest mb-1 ${
                        userStatus.experience_level === 'beginner' ? 'text-emerald-600' : 
                        userStatus.experience_level === 'intermediate' ? 'text-blue-600' : 
                        'text-amber-600'
                      }`}>
                        Current Expertise
                      </Text>
                      <Text className={`text-2xl font-black uppercase ${
                        userStatus.experience_level === 'beginner' ? 'text-emerald-900' : 
                        userStatus.experience_level === 'intermediate' ? 'text-blue-900' : 
                        'text-amber-900'
                      }`}>
                        {userStatus.experience_level}
                      </Text>
                    </View>
                    <View className={`px-4 py-2 rounded-2xl bg-white shadow-sm border ${
                      userStatus.experience_level === 'beginner' ? 'border-emerald-200' : 
                      userStatus.experience_level === 'intermediate' ? 'border-blue-200' : 
                      'border-amber-200'
                    }`}>
                      <Text className={`font-black text-xs ${
                        userStatus.experience_level === 'beginner' ? 'text-emerald-600' : 
                        userStatus.experience_level === 'intermediate' ? 'text-blue-600' : 
                        'text-amber-600'
                      }`}>
                        {userStatus.experience_level === 'beginner' ? '🌱 Start' : 
                         userStatus.experience_level === 'intermediate' ? '🚀 Growing' : 
                         '👑 Elite'}
                      </Text>
                    </View>
                  </View>
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
