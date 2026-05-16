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
        const response = await client.get(`/api/user/${userId}/status`);
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
      alert("어제 운동 기록이 생성되었습니다!");
      fetchStatus(); // Refresh streak
    } catch (error) {
      console.error(error);
    }
  };

  return (
    <SafeAreaView className="flex-1 bg-white">
      <Stack.Screen options={{ title: "Fitness AI", headerShown: false }} />
      <ScrollView className="p-6 pt-10" showsVerticalScrollIndicator={false}>
        <View className="mb-8">
          <Text className="text-3xl font-black text-gray-900">홈</Text>
        </View>

        {isOnboarded && (
          <View className="mb-6 bg-blue-600 p-8 rounded-[40px] shadow-xl relative overflow-hidden">
            {/* Background Decorative Circles */}
            <View className="absolute -top-10 -right-10 w-40 h-40 bg-white/10 rounded-full" />
            <View className="absolute -bottom-20 -left-10 w-32 h-32 bg-white/5 rounded-full" />

            <Text className="text-white text-xl font-bold mb-1">안녕하세요! 👋</Text>
            <Text className="text-blue-100 text-sm mb-6">오늘도 건강한 하루를 만들어볼까요?</Text>

            <View className="flex-row items-center bg-white/20 self-start px-4 py-2 rounded-full border border-white/30">
              <Text className="text-2xl mr-2">🔥</Text>
              <View>
                <Text className="text-white font-black text-lg leading-tight">
                  {userStatus?.current_streak || 0}일째
                </Text>
                <Text className="text-blue-100 text-[10px] font-bold uppercase tracking-widest">
                  연속 운동 중
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
          <View>
            <TouchableOpacity
              className="bg-gray-900 p-5 rounded-3xl items-center shadow-lg mb-6 active:opacity-90"
              onPress={() => router.push("/recommend")}
            >
              <View className="flex-row items-center">
                <Text className="text-white font-extrabold text-lg mr-2">오늘의 운동 추천받기</Text>
                <Text className="text-white text-xl">✨</Text>
              </View>
            </TouchableOpacity>
            
            <View className="bg-gray-50 p-6 rounded-[32px] border border-gray-100">
              <View className="flex-row justify-between items-center mb-4">
                <Text className="font-black text-gray-800 text-lg">내 상태</Text>
                <TouchableOpacity onPress={() => router.push("/onboarding")}>
                  <Text className="text-blue-600 font-bold text-xs">수정하기</Text>
                </TouchableOpacity>
              </View>
              
              <View className="space-y-3">
                <View className="flex-row items-center">
                  <View className="w-8 h-8 bg-blue-50 rounded-lg items-center justify-center mr-3">
                    <Text className="text-xs">🎯</Text>
                  </View>
                  <Text className="text-gray-500 text-sm flex-1 font-medium">운동 목표</Text>
                  <Text className="text-gray-900 font-bold text-sm">
                    {userStatus?.goal === "weight_loss" ? "체중 감량" : 
                     userStatus?.goal === "muscle_gain" ? "근력 증진" : "건강 유지"}
                  </Text>
                </View>

                <View className="flex-row items-center mt-3">
                  <View className="w-8 h-8 bg-blue-50 rounded-lg items-center justify-center mr-3">
                    <Text className="text-xs">📈</Text>
                  </View>
                  <Text className="text-gray-500 text-sm flex-1 font-medium">숙련도</Text>
                  <Text className="text-gray-900 font-bold text-sm uppercase">
                    {userStatus?.experience_level || "beginner"}
                  </Text>
                </View>
              </View>
            </View>

            {/* DEBUG BUTTON - REMOVE IN PRODUCTION */}
            <TouchableOpacity 
              onPress={mockYesterday}
              className="mt-10 p-4 border border-red-100 rounded-2xl border-dashed items-center"
            >
              <Text className="text-red-300 text-[10px] font-bold">🛠️ [테스트용] 스트릭 1일 늘리기</Text>
              <Text className="text-red-200 text-[8px] mt-1">누를 때마다 연속 운동일수가 1일씩 증가합니다.</Text>
            </TouchableOpacity>
          </View>
        )}
      </ScrollView>
    </SafeAreaView>
  );
}
