import React, { useEffect } from "react";
import { View, Text, TouchableOpacity, ScrollView } from "react-native";
import { useRouter, Stack } from "expo-router";
import { useUserStore } from "../src/store/userStore";
import { SafeAreaView } from "react-native-safe-area-context";

export default function Home() {
  const { userId, isOnboarded } = useUserStore();
  const router = useRouter();

  useEffect(() => {
    if (!userId || !isOnboarded) {
      // For now, let's keep it simple. In a real app, we'd check persistent storage.
    }
  }, [userId, isOnboarded]);

  return (
    <SafeAreaView className="flex-1 bg-white">
      <Stack.Screen options={{ title: "Fitness AI" }} />
      <ScrollView className="p-4">
        <View className="mb-6 bg-orange-100 p-6 rounded-2xl border border-orange-200">
          <Text className="text-2xl font-bold text-orange-800">안녕하세요! 👋</Text>
          <Text className="text-gray-600 mt-2">오늘도 건강한 하루를 만들어볼까요?</Text>
          {userId ? (
            <Text className="text-sm text-orange-600 mt-1">User ID: {userId}</Text>
          ) : null}
        </View>

        {!isOnboarded ? (
          <TouchableOpacity
            className="bg-orange-500 p-4 rounded-xl items-center shadow-sm"
            onPress={() => router.push("/onboarding")}
          >
            <Text className="text-white font-bold text-lg">온보딩 시작하기</Text>
          </TouchableOpacity>
        ) : (
          <View>
            <TouchableOpacity
              className="bg-orange-500 p-4 rounded-xl items-center shadow-sm mb-4"
              onPress={() => router.push("/recommend")}
            >
              <Text className="text-white font-bold text-lg">오늘의 운동 추천받기</Text>
            </TouchableOpacity>
            
            <View className="bg-gray-50 p-4 rounded-xl border border-gray-200">
              <Text className="font-bold text-gray-800 mb-2">현재 상태</Text>
              <Text className="text-gray-600">• 운동 목표: 근력 향상</Text>
              <Text className="text-gray-600">• 선호 장소: 헬스장</Text>
            </View>
          </View>
        )}
      </ScrollView>
    </SafeAreaView>
  );
}
