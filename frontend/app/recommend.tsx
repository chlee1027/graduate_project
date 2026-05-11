import React, { useState, useEffect } from "react";
import { View, Text, TouchableOpacity, ScrollView, ActivityIndicator, Alert, Linking } from "react-native";
import { useRouter, Stack } from "expo-router";
import { useUserStore } from "../src/store/userStore";
import client from "../src/api/client";
import { SafeAreaView } from "react-native-safe-area-context";

export default function Recommend() {
  const router = useRouter();
  const { userId } = useUserStore();
  const [loading, setLoading] = useState(true);
  const [recommendation, setRecommendation] = useState<any>(null);
  const [location, setLocation] = useState<"home" | "gym">("gym");

  const fetchRecommendation = async (currentLocation: string) => {
    setLoading(true);
    try {
      const response = await client.post("/api/recommend/", {
        user_id: userId,
        location: currentLocation,
        available_minutes: 60,
        fatigue: 2,
        sleep_hours: 7.0,
        recent_adherence_7d: 0.8,
        streak: 3,
        avg_rpe_last_7d: 5.0,
      });
      setRecommendation(response.data);
    } catch (error) {
      console.error(error);
      Alert.alert("오류", "추천을 불러오지 못했습니다. 서버 상태나 네트워크를 확인해주세요.");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (userId) {
      fetchRecommendation(location);
    } else {
      setLoading(false);
      Alert.alert("오류", "사용자 정보가 없습니다. 온보딩을 먼저 진행해주세요.");
      router.replace("/onboarding");
    }
  }, [userId]);

  const handleLocationChange = (newLoc: "home" | "gym") => {
    setLocation(newLoc);
    fetchRecommendation(newLoc);
  };

  if (loading) {
    return (
      <View className="flex-1 justify-center items-center">
        <ActivityIndicator size="large" color="#2563eb" />
        <Text className="mt-4 text-gray-500">AI가 {location === "home" ? "홈트" : "헬스장"} 맞춤 운동을 찾고 있습니다...</Text>
      </View>
    );
  }

  return (
    <SafeAreaView className="flex-1 bg-white">
      <Stack.Screen options={{ title: "추천 결과" }} />
      <ScrollView className="p-4">
        <View className="flex-row bg-gray-100 p-1 rounded-2xl mb-6">
          <TouchableOpacity
            onPress={() => handleLocationChange("home")}
            className={`flex-1 p-3 rounded-xl items-center ${location === "home" ? "bg-white shadow-sm" : ""}`}
          >
            <Text className={location === "home" ? "text-blue-600 font-bold" : "text-gray-500"}>🏠 홈트레이닝</Text>
          </TouchableOpacity>
          <TouchableOpacity
            onPress={() => handleLocationChange("gym")}
            className={`flex-1 p-3 rounded-xl items-center ${location === "gym" ? "bg-white shadow-sm" : ""}`}
          >
            <Text className={location === "gym" ? "text-blue-600 font-bold" : "text-gray-500"}>🏋️ 헬스장</Text>
          </TouchableOpacity>
        </View>

        <Text className="text-xl font-bold mb-2">오늘의 추천 플랜</Text>
        <Text className="text-gray-500 mb-6">Bandit AI가 선택한 최고의 운동입니다.</Text>

        {recommendation ? (
          <>
            <View className="bg-blue-50 p-6 rounded-2xl border border-blue-100 mb-6">
              <Text className="text-blue-900 font-bold text-lg mb-1">
                {recommendation.selected_plan.name || recommendation.selected_plan.plan_id.replace(/_/g, " ").toUpperCase()}
              </Text>
              <Text className="text-gray-600 mb-4">난이도: {recommendation.selected_plan.intensity}</Text>
              
              <View className="flex-row items-center mb-4">
                <View className="w-2 h-2 rounded-full bg-blue-600 mr-2" />
                <Text className="text-gray-700">추천 시간: {recommendation.selected_plan.minutes}분</Text>
              </View>

              {recommendation.selected_plan.video_url && (
                <TouchableOpacity
                  onPress={() => Linking.openURL(recommendation.selected_plan.video_url)}
                  className="bg-white border border-blue-200 py-3 rounded-xl flex-row items-center justify-center shadow-sm"
                >
                  <Text className="text-blue-600 font-bold">📺 운동 가이드 영상 보기</Text>
                </TouchableOpacity>
              )}
            </View>

            <TouchableOpacity
              className="bg-blue-600 p-4 rounded-xl items-center shadow-sm"
              onPress={() => router.push({
                pathname: `/workout/${recommendation.selected_plan.plan_id}`,
                params: { recommendation_id: recommendation.recommendation_id }
              })}
            >
              <Text className="text-white font-bold text-lg">운동 시작하기</Text>
            </TouchableOpacity>
          </>
        ) : (
          <View className="p-10 items-center">
            <Text className="text-gray-400">추천 결과가 없습니다.</Text>
          </View>
        )}
        
        <TouchableOpacity
          className="p-4 items-center"
          onPress={() => fetchRecommendation(location)}
        >
          <Text className="text-blue-600">다른 추천 받기</Text>
        </TouchableOpacity>
      </ScrollView>
    </SafeAreaView>
  );
}
