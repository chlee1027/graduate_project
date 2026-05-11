import React, { useState, useEffect } from "react";
import { View, Text, TouchableOpacity, ScrollView, ActivityIndicator, Alert } from "react-native";
import { useRouter, Stack } from "expo-router";
import { useUserStore } from "../src/store/userStore";
import client from "../src/api/client";
import { SafeAreaView } from "react-native-safe-area-context";

export default function Recommend() {
  const router = useRouter();
  const { userId } = useUserStore();
  const [loading, setLoading] = useState(true);
  const [recommendation, setRecommendation] = useState<any>(null);

  const fetchRecommendation = async () => {
    setLoading(true);
    try {
      const response = await client.post("/api/recommend/", {
        user_id: userId,
        place: "gym",
        available_minutes: 60,
        fatigue: 2,
        recent_adherence_7d: 0.8,
      });
      setRecommendation(response.data);
    } catch (error) {
      console.error(error);
      Alert.alert("오류", "추천을 불러오지 못했습니다.");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchRecommendation();
  }, []);

  if (loading) {
    return (
      <View className="flex-1 justify-center items-center">
        <ActivityIndicator size="large" color="#f4511e" />
        <Text className="mt-4 text-gray-500">AI가 최적의 운동을 찾고 있습니다...</Text>
      </View>
    );
  }

  return (
    <SafeAreaView className="flex-1 bg-white">
      <Stack.Screen options={{ title: "추천 결과" }} />
      <ScrollView className="p-4">
        <Text className="text-xl font-bold mb-2">오늘의 추천 플랜</Text>
        <Text className="text-gray-500 mb-6">Bandit AI가 선택한 최고의 운동입니다.</Text>

        {recommendation && (
          <View className="bg-orange-50 p-6 rounded-2xl border border-orange-200 mb-6">
            <Text className="text-orange-800 font-bold text-lg mb-1">
              {recommendation.selected_plan.plan_id.replace(/_/g, " ").toUpperCase()}
            </Text>
            <Text className="text-gray-600 mb-4">난이도: {recommendation.selected_plan.intensity}</Text>
            
            <View className="flex-row items-center mb-2">
              <View className="w-2 h-2 rounded-full bg-orange-500 mr-2" />
              <Text className="text-gray-700">추천 시간: {recommendation.selected_plan.minutes}분</Text>
            </View>
            <View className="flex-row items-center">
              <View className="w-2 h-2 rounded-full bg-orange-500 mr-2" />
              <Text className="text-gray-700">추천 이유: {recommendation.reason === "exploration" ? "새로운 시도" : "최적의 선택"}</Text>
            </View>
          </View>
        )}

        <TouchableOpacity
          className="bg-orange-500 p-4 rounded-xl items-center shadow-sm"
          onPress={() => router.push({
            pathname: `/workout/${recommendation.selected_plan.plan_id}`,
            params: { recommendation_id: recommendation.recommendation_id }
          })}
        >
          <Text className="text-white font-bold text-lg">운동 시작하기</Text>
        </TouchableOpacity>
        
        <TouchableOpacity
          className="p-4 items-center"
          onPress={fetchRecommendation}
        >
          <Text className="text-orange-500">다른 추천 받기</Text>
        </TouchableOpacity>
      </ScrollView>
    </SafeAreaView>
  );
}
